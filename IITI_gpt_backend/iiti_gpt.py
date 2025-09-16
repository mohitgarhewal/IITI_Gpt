# iiti_gpt.py
# Single-file IITI assistant with Router → SubQuerier → QA(RAG) → Critique/Refine loop.
# Uses OpenAI via langchain_openai and FAISS for retrieval.

import os
from pathlib import Path
from typing import TypedDict, List, Literal, Tuple, Dict, Optional, Set
from collections import defaultdict

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

# ---- Vectorstore utilities (FAISS) ----
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
# If using OpenAI embeddings, we import lazily in _get_embeddings()

# =========================
# Config (from environment)
# =========================
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DOCS_PATH = os.getenv("DOCS_PATH", "./docs")
FAISS_DIR = os.getenv("FAISS_DIR", "./faiss_store")
EMBED_BACKEND = os.getenv("EMBED_BACKEND", "hf")  # "hf" or "openai"
HF_EMBED_MODEL = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

# =====================
# LangChain LLM backend
# =====================
llm = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0.0,
    api_key=os.getenv("OPENAI_API_KEY"),
)

# ===========================
# App State (LangGraph state)
# ===========================
class MyState(TypedDict, total=False):
    # inputs / running context
    user_query: str
    messages: List[BaseMessage]
    route: str
    router_reason: str

    # planning
    subqueries: List[str]

    # RAG context visibility
    retrieved_by_subquery: Dict[str, List[Dict]]   # all retrieved (pre-fusion)
    used_contexts: List[Dict]                      # fused contexts actually used
    context_snippets: str                          # numbered snippets fed to LLM
    source_diversity: int                          # distinct 'source' count
    had_no_results: bool                           # no docs found?
    retrieval_mode: Literal["primary", "mmr"]      # which retriever on this pass

    # answers & meta
    final_answer: str
    relevance_score: float
    critique_verdict: Literal["GOOD", "RETRY"]
    critique_rationale: str
    revised_subqueries: List[str]
    iterations: int
    max_iterations: int
    critique_threshold: float
    refine_action: Literal["RETRY", "STOP"]

# ===========================
# Router (query classification)
# ===========================
class RouteDecision(BaseModel):
    route: Literal["CHAT", "GENERAL", "SUBQUERIER", "CLARIFY"]
    reason: str

router_system = """\
You are a query router for an IIT Indore (IITI) assistant.
Classify the user's query into exactly one destination:
- CHAT: greetings, small talk, or meta questions about the assistant.
- GENERAL: general-purpose help that does not require IITI-specific knowledge.
- SUBQUERIER: queries about Indian Institute of Technology Indore (IIT Indore / IITI).
- CLARIFY: the question is ambiguous; ask a targeted clarifying question.
Prefer GENERAL over SUBQUERIER only if the topic is clearly not about IITI.
"""

router_prompt = ChatPromptTemplate.from_messages([
    ("system", router_system),
    MessagesPlaceholder("history"),
    ("human", "{input}")
])
router_chain = router_prompt | llm.with_structured_output(RouteDecision)

def query_router_node(state: MyState, config=None, runtime=None):
    history = state.get("messages", [])
    decision: RouteDecision = router_chain.invoke({
        "history": history,
        "input": state.get("user_query", "")
    })
    return {"route": decision.route, "router_reason": decision.reason}

# ===========================
# Generalized Chatbot (fallback)
# ===========================
general_system = """\
You are a helpful, concise, general-purpose assistant.
Answer clearly. If unsure, say so briefly and suggest the minimal next step.
If the router labeled the query as CLARIFY, ask ONE targeted clarifying question first.
"""

general_prompt = ChatPromptTemplate.from_messages([
    ("system", general_system),
    MessagesPlaceholder("history"),
    ("human", "{input}")
])
general_chain = general_prompt | llm

def general_chat_node(state: MyState, config=None, runtime=None):
    history = state.get("messages", [])
    user_q = state.get("user_query", "")
    if state.get("route") == "CLARIFY":
        user_q = f"The router marked this as ambiguous. Ask ONE clarifying question for: {user_q}"
    ai_msg: AIMessage = general_chain.invoke({"history": history, "input": user_q})
    new_history = history + [HumanMessage(content=state.get("user_query", "")), ai_msg]
    return {"messages": new_history, "final_answer": ai_msg.content}

# ===========================
# SubQuerier (planning only)
# ===========================
class SubQueryPlan(BaseModel):
    needs_breakdown: bool
    subqueries: List[str]
    rationale: str

subquerier_system = """\
You are a sub-query planner for Indian Institute of Technology Indore (IIT Indore / IITI).
Given a user question, produce the minimal set of precise, IITI-specific sub-queries that,
together, would fully answer it. Keep them scoped to IITI (admissions, departments,
programs, fees, placements, hostels, campus facilities, transport, contacts, policies, etc.).
Return 1–5 sub-queries. Prefer fewer if sufficient. Do NOT retrieve or answer—only plan.
"""

subquerier_prompt = ChatPromptTemplate.from_messages([
    ("system", subquerier_system),
    ("human", "User question:\n{question}")
])
subquery_chain = subquerier_prompt | llm.with_structured_output(SubQueryPlan)

def subquerier_node(state: MyState, config=None, runtime=None):
    question = state.get("user_query", "")
    plan: SubQueryPlan = subquery_chain.invoke({"question": question})
    subs = plan.subqueries or [question]
    bullets = "\n".join([f"- {q}" for q in subs])
    reply = "I’ll break this into the following IITI-specific sub-queries:\n" + bullets + f"\n\nReason: {plan.rationale}"
    history = state.get("messages", [])
    ai_msg = AIMessage(content=reply)
    new_history = history + [HumanMessage(content=question), ai_msg]
    return {
        "messages": new_history,
        "final_answer": ai_msg.content,
        "subqueries": subs
    }

# ===========================
# RAG (per-subquery) + fusion
# ===========================
def _rrf_merge(results_per_subq: List[List[Document]], k: int = 8, c: int = 60) -> List[Tuple[Document, float]]:
    scores: Dict[Tuple[str, str], float] = defaultdict(float)
    pick: Dict[Tuple[str, str], Document] = {}

    def _key(d: Document) -> Tuple[str, str]:
        src = str(d.metadata.get("source", ""))
        pid = str(d.metadata.get("id", d.metadata.get("page", "")))
        return (src, pid)

    for docs in results_per_subq:
        for rank, d in enumerate(docs, start=1):
            key = _key(d)
            scores[key] += 1.0 / (c + rank)
            if key not in pick:
                pick[key] = d

    fused = [(pick[k], v) for k, v in scores.items()]
    fused.sort(key=lambda x: x[1], reverse=True)
    return fused[:k]

def _doc_to_ctx_dict(d: Document) -> Dict:
    return {
        "source": d.metadata.get("source", "unknown"),
        "page": d.metadata.get("page", d.metadata.get("id", "")),
        "title": d.metadata.get("title", ""),
        "text": (d.page_content or "").strip()[:800]
    }

def _format_snippets(docs: List[Document]) -> str:
    lines = []
    for i, d in enumerate(docs, start=1):
        src = d.metadata.get("source", "unknown")
        page = d.metadata.get("page", d.metadata.get("id", ""))
        snippet = (d.page_content or "").strip().replace("\n", " ")
        lines.append(f"[{i}] ({src}, p:{page}) {snippet[:800]}")
    return "\n".join(lines)

answer_system = """\
You are an IIT Indore (IITI) answer synthesizer. Use ONLY the provided context.
Write a concise, correct answer to the user's question. Cite sources inline using [#].
Then include a "Sources:" list mapping numbers to their source metadata.
If context is insufficient, say what's missing and (optionally) point to the relevant IITI office/page.
"""

answer_prompt = ChatPromptTemplate.from_messages([
    ("system", answer_system),
    ("human",
     "Initial user question:\n{question}\n\n"
     "Sub-queries:\n{subqueries}\n\n"
     "Context snippets (each is numbered):\n{numbered_snippets}\n\n"
     "Write the final answer with inline citations [#] and a Sources list.")
])
answer_chain = answer_prompt | llm

def build_qa_rag_node(primary_retriever,
                      mmr_retriever=None,
                      per_subquery_k: int = 5,
                      final_ctx_k: int = 8):
    def qa_rag_node(state: MyState, config=None, runtime=None):
        question = state.get("user_query", "")
        subs = state.get("subqueries") or [question]
        mode = state.get("retrieval_mode", "primary")
        retriever = mmr_retriever if (mode == "mmr" and mmr_retriever is not None) else primary_retriever

        # retrieve
        results_per_subq: List[List[Document]] = []
        retrieved_all: Dict[str, List[Dict]] = {}
        seen_sources: Set[str] = set()

        for sq in subs:
            try:
                docs = retriever.invoke(sq)[:per_subquery_k]
            except Exception:
                docs = []
            results_per_subq.append(docs)
            ctx_dicts = [_doc_to_ctx_dict(d) for d in docs]
            retrieved_all[sq] = ctx_dicts
            for c in ctx_dicts:
                if c.get("source"):
                    seen_sources.add(c["source"])

        fused = _rrf_merge(results_per_subq, k=final_ctx_k)
        fused_docs = [d for d, _ in fused]
        used_contexts = [_doc_to_ctx_dict(d) for d in fused_docs]
        numbered_snips = _format_snippets(fused_docs) if fused_docs else "None"

        had_no_results = (sum(len(lst or []) for lst in retrieved_all.values()) == 0) or (len(fused_docs) == 0)
        diversity = len({s for s in seen_sources if s})

        subs_bullets = "\n".join([f"- {q}" for q in subs])
        ai_msg = answer_chain.invoke({
            "question": question,
            "subqueries": subs_bullets,
            "numbered_snippets": numbered_snips
        })

        history = state.get("messages", [])
        new_history = history + [HumanMessage(content=question), AIMessage(content=ai_msg.content)]
        return {
            "messages": new_history,
            "final_answer": ai_msg.content,
            "retrieved_by_subquery": retrieved_all,
            "used_contexts": used_contexts,
            "context_snippets": numbered_snips,
            "had_no_results": had_no_results,
            "source_diversity": diversity
        }
    return qa_rag_node

# ===========================
# Critique + Refinement loop
# ===========================
class CritiqueDecision(BaseModel):
    score: float = Field(description="Relevance score in [0,1], higher is better.")
    verdict: Literal["GOOD", "RETRY"]
    rationale: str
    revised_subqueries: Optional[List[str]] = Field(
        default=None,
        description="If RETRY, propose 1–5 revised IITI sub-queries."
    )

critic_system = """\
You are a strict evaluator of answer relevance for IIT Indore (IITI) Q&A.
Given the user's question, planned sub-queries, the contexts used, and the draft answer:
1) Score the answer's relevance/grounding in [0,1] (0=irrelevant/ungrounded, 1=perfectly grounded).
2) If important aspects are missing or unsupported, set verdict=RETRY and propose 1–5 revised/augmented sub-queries
   that would likely pull the missing evidence from IITI sources.
3) Otherwise verdict=GOOD.
Keep sub-queries precise and IITI-focused.
"""

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", critic_system),
    ("human",
     "Initial user question:\n{question}\n\n"
     "Current sub-queries:\n{subqueries}\n\n"
     "Contexts used (numbered):\n{numbered_snippets}\n\n"
     "Draft answer:\n{answer}\n\n"
     "Evaluate and respond with score, verdict, rationale, and optionally revised_subqueries.")
])
critic_chain = critic_prompt | llm.with_structured_output(CritiqueDecision)

def critique_node(state: MyState, config=None, runtime=None):
    question = state.get("user_query", "")
    subs = state.get("subqueries", [])
    numbered = state.get("context_snippets", "None")
    answer = state.get("final_answer", "")
    sub_bullets = "\n".join([f"- {q}" for q in subs]) if subs else "None"

    decision: CritiqueDecision = critic_chain.invoke({
        "question": question,
        "subqueries": sub_bullets,
        "numbered_snippets": numbered,
        "answer": answer
    })

    threshold = state.get("critique_threshold", 0.78)
    verdict = decision.verdict
    if decision.score < threshold:
        verdict = "RETRY"

    return {
        "relevance_score": float(decision.score),
        "critique_verdict": verdict,
        "critique_rationale": decision.rationale,
        "revised_subqueries": decision.revised_subqueries or []
    }

class SubqueryRefinement(BaseModel):
    new_subqueries: List[str] = Field(
        description="1–5 revised IITI-focused sub-queries to improve retrieval coverage."
    )

refiner_system = """\
You are a sub-query refiner for IIT Indore (IITI).
Goal: improve retrieval coverage and grounding for the user's question.
Given the initial question, current sub-queries, and the sources we already retrieved,
propose 1–5 revised sub-queries that (a) target missing aspects and (b) diversify sources.
Prefer official IITI terms and sections (e.g., Student Gymkhana, Councils, Cells, Dean of Student Affairs),
and synonyms for clubs/events/facilities when relevant. Keep them IITI-scoped.
Return only sub-queries; do NOT answer.
"""

refiner_prompt = ChatPromptTemplate.from_messages([
    ("system", refiner_system),
    ("human",
     "Initial question:\n{question}\n\n"
     "Current sub-queries:\n{subqueries}\n\n"
     "Already seen sources (avoid repeating if possible):\n{seen_sources}\n\n"
     "Propose revised sub-queries.")
])
refine_subqueries_chain = refiner_prompt | llm.with_structured_output(SubqueryRefinement)

def apply_refinement_node(state: MyState, config=None, runtime=None):
    max_iters = state.get("max_iterations", 2)
    iters = int(state.get("iterations", 0))
    verdict = state.get("critique_verdict", "GOOD")
    current_subs = state.get("subqueries", []) or []
    revised = state.get("revised_subqueries", []) or []

    if verdict != "RETRY" or iters >= max_iters:
        return {"iterations": iters, "refine_action": "STOP"}

    retrieved = state.get("retrieved_by_subquery", {}) or {}
    seen_sources_sorted = sorted({(c.get("source") or "unknown")
                                  for lst in retrieved.values() for c in (lst or [])})
    source_diversity = int(state.get("source_diversity", 0))
    had_no_results = bool(state.get("had_no_results", False))

    candidate = revised if revised and revised != current_subs else None
    need_diversify = (source_diversity <= 1)

    if candidate is None or need_diversify or had_no_results:
        question = state.get("user_query", "")
        subs_bullets = "\n".join([f"- {q}" for q in current_subs]) if current_subs else "None"
        seen_list = "\n".join([f"- {s}" for s in seen_sources_sorted]) if seen_sources_sorted else "None"
        try:
            refined: SubqueryRefinement = refine_subqueries_chain.invoke({
                "question": question,
                "subqueries": subs_bullets,
                "seen_sources": seen_list
            })
            candidate = refined.new_subqueries or current_subs
        except Exception:
            candidate = current_subs + [f"IIT Indore Student Gymkhana information about: {question}"]

        if candidate == current_subs:
            return {"iterations": iters, "refine_action": "STOP", "critique_verdict": "GOOD"}

    next_mode = state.get("retrieval_mode", "primary")
    if had_no_results or need_diversify:
        next_mode = "mmr"

    return {
        "subqueries": candidate,
        "iterations": iters + 1,
        "refine_action": "RETRY",
        "retrieval_mode": next_mode
    }

# ===========================
# Build Graph
# ===========================
def build_core_router_graph(primary_retriever,
                            mmr_retriever=None,
                            per_subquery_k: int = 5,
                            final_ctx_k: int = 8,
                            critique_threshold: float = 0.78,
                            max_iterations: int = 2):
    g = StateGraph(MyState)

    def set_query_node(state: MyState, config=None, runtime=None):
        return {
            "user_query": state.get("user_query", ""),
            "iterations": state.get("iterations", 0),
            "max_iterations": state.get("max_iterations", max_iterations),
            "critique_threshold": state.get("critique_threshold", critique_threshold),
            "retrieval_mode": state.get("retrieval_mode", "primary"),
        }

    g.add_node("SetQuery", set_query_node)
    g.add_node("QueryRouter", query_router_node)
    g.add_node("GeneralChat", general_chat_node)
    g.add_node("SubQuerier", subquerier_node)
    g.add_node("QARAG", build_qa_rag_node(primary_retriever, mmr_retriever, per_subquery_k, final_ctx_k))
    g.add_node("Critique", critique_node)
    g.add_node("ApplyRefinement", apply_refinement_node)

    g.add_edge(START, "SetQuery")
    g.add_edge("SetQuery", "QueryRouter")

    g.add_conditional_edges(
        "QueryRouter",
        lambda s: s.get("route", "GENERAL"),
        {
            "CHAT": "GeneralChat",
            "GENERAL": "GeneralChat",
            "SUBQUERIER": "SubQuerier",
            "CLARIFY": "GeneralChat",
        },
       
    )

    g.add_edge("SubQuerier", "QARAG")
    g.add_edge("QARAG", "Critique")
    g.add_conditional_edges("Critique", lambda s: "APPLY", {"APPLY": "ApplyRefinement"})
    g.add_conditional_edges(
        "ApplyRefinement",
        lambda s: s.get("refine_action", "STOP"),
        {"RETRY": "QARAG", "STOP": END},
        
    )
    g.add_edge("GeneralChat", END)
    return g.compile()

# ===========================
# FAISS index build/load
# ===========================
def _load_docs(root: str) -> List[Document]:
    rootp = Path(root)
    docs: List[Document] = []

    for p in list(rootp.rglob("*.txt")) + list(rootp.rglob("*.md")) + list(rootp.rglob("*.csv")):
        try:
            docs.extend(TextLoader(str(p), encoding="utf-8").load())
        except Exception:
            pass

    for p in list(rootp.rglob("*.pdf")):
        try:
            docs.extend(PyPDFLoader(str(p)).load())
        except Exception:
            pass

    return docs

def _split_docs(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    return splitter.split_documents(docs)

def _get_embeddings():
    if EMBED_BACKEND.lower() == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=OPENAI_EMBED_MODEL, api_key=os.getenv("OPENAI_API_KEY"))
    return HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)

def build_or_load_faiss_index(docs_path: str, faiss_store_path: str = "faiss_store"):
    idx_path = Path(faiss_store_path)
    embeddings = _get_embeddings()
    if idx_path.exists():
        vs = FAISS.load_local(faiss_store_path, embeddings, allow_dangerous_deserialization=True)
        print(f"[RAG] Loaded FAISS from {faiss_store_path}")
        return vs

    print(f"[RAG] Building FAISS index from {docs_path} ...")
    raw_docs = _load_docs(docs_path)
    if not raw_docs:
        raise RuntimeError(f"No documents found under {docs_path}. Put your IITI PDFs or texts there.")
    chunks = _split_docs(raw_docs)
    vs = FAISS.from_documents(chunks, embeddings)
    vs.save_local(faiss_store_path)
    print(f"[RAG] Saved FAISS to {faiss_store_path} (docs: {len(raw_docs)}, chunks: {len(chunks)})")
    return vs


# ----------------------------
# Module-level retriever exports & init helper (server expects these)
# ----------------------------
primary_retriever = None
mmr_retriever = None

def init_retrievers(docs_path: str = DOCS_PATH,
                    faiss_store_path: str = FAISS_DIR,
                    per_k: int = 8,
                    embedding_provider: str = EMBED_BACKEND,
                    hf_model: str = HF_EMBED_MODEL):
    """
    Build or load FAISS vectorstore and set module-level `primary_retriever` and `mmr_retriever`.
    Returns True on success, False on failure.
    """
    global primary_retriever, mmr_retriever
    try:
        vs = build_or_load_faiss_index(docs_path, faiss_store_path)
        primary_retriever = vs.as_retriever(search_type="similarity", search_kwargs={"k": per_k})
        try:
            mmr_retriever = vs.as_retriever(search_type="mmr", search_kwargs={"k": per_k, "lambda_mult": 0.5})
        except Exception:
            # mmr may not be available in older vectorstore implementations — fallback to primary
            mmr_retriever = primary_retriever
        print(f"[iiti_gpt] init_retrievers: primary/mmr retrievers set (k={per_k}).")
        return True
    except Exception as e:
        print(f"[iiti_gpt] init_retrievers failed: {e}")
        primary_retriever = None
        mmr_retriever = None
        return False

# Auto-init on import when safe: if a saved FAISS index exists or docs are present or env var asks for it.
try_auto = False
try:
    if Path(FAISS_DIR).exists():
        try_auto = True
    elif Path(DOCS_PATH).exists() and any(Path(DOCS_PATH).iterdir()):
        # docs are present — optional auto build (this blocks import while building index)
        try_auto = os.getenv("AUTO_INIT_RETRIEVERS", "false").lower() in ("1", "true", "yes")
    elif os.getenv("AUTO_INIT_RETRIEVERS", "false").lower() in ("1", "true", "yes"):
        try_auto = True
except Exception:
    try_auto = False

if try_auto:
    # Only attempt auto init if env var or FAISS_DIR exists. Building can take time.
    _ok = False
    try:
        _ok = init_retrievers(docs_path=DOCS_PATH, faiss_store_path=FAISS_DIR)
    except Exception:
        _ok = False
    if not _ok:
        print("[iiti_gpt] Auto init retrievers attempted but failed.")

# Development fallback retriever so server can run during early dev (no real contexts returned).
class _DevRetriever:
    def get_relevant_documents(self, query: str):
        # return empty list => QA node will have no contexts
        return []

    def as_retriever(self, **kwargs):
        return self

# Optionally keep a dev fallback but DO NOT enable it silently in production.
# Uncomment the next two lines to enable fallback automatically when no retriever is available:
# if primary_retriever is None:
#     primary_retriever = mmr_retriever = _DevRetriever()


# ===========================
# CLI entry
# ===========================
if __name__ == "__main__":
    # Build/load vector store
    _vectorstore = build_or_load_faiss_index(DOCS_PATH, FAISS_DIR)

    # Define retrievers
    primary_retriever = _vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 8})
    mmr_retriever = _vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 8, "lambda_mult": 0.5})

    # Build graph
    app = build_core_router_graph(
        primary_retriever=primary_retriever,
        mmr_retriever=mmr_retriever,
        per_subquery_k=5,
        final_ctx_k=8,
        critique_threshold=0.78,
        max_iterations=2
    )

    # Example run (replace with your own input mechanism)
    s: MyState = {
        "user_query": "Tell me about the Aquatics Club at IIT Indore.",
        "messages": []
    }
    out = app.invoke(s)

    print("Route:", out.get("route"), "| Reason:", out.get("router_reason"))
    print("Iterations:", out.get("iterations"), "/", out.get("max_iterations"))
    print("Retrieval mode (final):", out.get("retrieval_mode"))
    print("Relevance score:", out.get("relevance_score"))
    print("Critique verdict:", out.get("critique_verdict"))
    print("\nFINAL ANSWER:\n", out.get("final_answer"))
    print("\n--- USED CONTEXTS (Fused) ---")
    for i, c in enumerate(out.get("used_contexts", []), 1):
        print(f"[{i}] {c.get('source')} p:{c.get('page')} :: {c.get('text','')[:200]}...")
    print("\n--- ALL RETRIEVED CONTEXTS (Pre-fusion) ---")
    for sq, lst in (out.get("retrieved_by_subquery", {}) or {}).items():
        print(f"\nSubquery: {sq}")
        for j, c in enumerate(lst, 1):
            print(f"  ({j}) {c.get('source')} p:{c.get('page')} :: {c.get('text','')[:160]}...")
