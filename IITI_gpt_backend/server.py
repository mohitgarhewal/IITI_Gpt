# server.py
import os
import traceback
from typing import List, Dict, Any
from importlib import import_module

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS

# ---- Load your iiti_gpt module (must be in same folder or in PYTHONPATH) ----
# Put server.py and iiti_gpt.py in same directory for this import to work:
try:
    iiti = import_module("iiti_gpt")
except Exception as e:
    raise ImportError("Could not import iiti_gpt.py. Ensure server.py and iiti_gpt.py are in same folder.") from e

# After importing iiti and retrieving attributes...
if getattr(iiti, "primary_retriever", None) is None:
    if hasattr(iiti, "init_retrievers"):
        ok = iiti.init_retrievers()
        if not ok:
            raise RuntimeError("Failed to initialize retrievers via iiti.init_retrievers().")
    else:
        raise RuntimeError("iiti_gpt.py has no primary_retriever and no init_retrievers() helper.")
# now re-grab
primary_retriever = iiti.primary_retriever
mmr_retriever = iiti.mmr_retriever

# grab types & helpers from your module so classes match exactly
try:
    HumanMessage = iiti.HumanMessage
    AIMessage = iiti.AIMessage
    BaseMessage = iiti.BaseMessage
    build_core_router_graph = iiti.build_core_router_graph
    # `primary_retriever` / `mmr_retriever` should be defined in iiti_gpt.py (you built them there)
    primary_retriever = getattr(iiti, "primary_retriever", None)
    mmr_retriever = getattr(iiti, "mmr_retriever", None)
    MyState = getattr(iiti, "MyState", dict)
except AttributeError as e:
    raise RuntimeError("iiti_gpt.py doesn't expose required attributes (HumanMessage, AIMessage, build_core_router_graph, primary_retriever).") from e

if primary_retriever is None:
    raise RuntimeError("iiti_gpt.py must define `primary_retriever` (vectorstore.as_retriever(...)).")

# ---- Flask app ----
app = Flask(__name__)
CORS(app)

# configuration from env
PORT = int(os.getenv("PORT", "5000"))
HOST = os.getenv("HOST", "0.0.0.0")

# ---- compile the graph once on server start (may take a moment) ----
print("Compiling LangGraph runnable (this may take a moment)...")
compiled_app = build_core_router_graph(
    primary_retriever=primary_retriever,
    mmr_retriever=mmr_retriever,
    per_subquery_k=int(os.getenv("PER_SUBQUERY_K", 5)),
    final_ctx_k=int(os.getenv("FINAL_CTX_K", 8)),
    critique_threshold=float(os.getenv("CRITIQUE_THRESHOLD", 0.78)),
    max_iterations=int(os.getenv("MAX_ITERATIONS", 2))
)
print("Compiled graph ready.")

# ---------- helpers: convert frontend messages -> BaseMessage objects ----------
def dicts_to_base_messages(msgs: List[Dict[str, str]]) -> List[BaseMessage]:
    """Convert [{role,content}] -> list of BaseMessage (HumanMessage/AIMessage) expected by graph."""
    out: List[BaseMessage] = []
    for m in msgs or []:
        role = (m.get("role") or "").lower()
        content = m.get("content", "")
        if role in ("user", "human"):
            out.append(HumanMessage(content=content))
        elif role in ("assistant", "ai"):
            out.append(AIMessage(content=content))
        elif role == "system":
            # treat system as human message content since your graph uses system via prompts
            out.append(HumanMessage(content=f"[SYSTEM] {content}"))
        else:
            # fallback to human message
            out.append(HumanMessage(content=content))
    return out

def base_messages_to_dicts(msg_objs: List[Any]) -> List[Dict[str, str]]:
    """Convert messages returned by graph (BaseMessage objects or dicts) -> plain dicts for JSON."""
    out: List[Dict[str, str]] = []
    for m in msg_objs or []:
        # If it's already a dict (some nodes may return dicts), pass through
        if isinstance(m, dict):
            out.append({"role": m.get("role", "assistant"), "content": m.get("content", "")})
            continue
        # otherwise try to access content and class name
        content = getattr(m, "content", str(m))
        clsname = m.__class__.__name__.lower()
        if "human" in clsname:
            role = "user"
        elif "ai" in clsname or "assistant" in clsname:
            role = "assistant"
        else:
            role = getattr(m, "role", "assistant")
        out.append({"role": role, "content": content})
    return out

# ---------- /chat endpoint ----------
@app.route("/chat", methods=["POST"])
def chat():
    """
    POST JSON:
    {
      "user_query": "string",          # required (also used to seed messages if none provided)
      "messages": [{role,content}, ...],  # optional conversation history
      "max_iterations": 2,             # optional overrides
      "critique_threshold": 0.78       # optional
    }
    Response JSON:
    {
      "user_query": "...",
      "final_answer": "...",
      "messages": [{role,content}, ...],    # full history (as plain dicts)
      "used_contexts": [...],
      "retrieved_by_subquery": {...},
      "relevance_score": ...,
      "critique_verdict": ...,
      "iterations": ...
    }
    """
    try:
        payload = request.get_json(force=True)
        user_query = payload.get("user_query", "") or ""
        client_messages = payload.get("messages", [])  # list of {role,content}
        max_iterations = payload.get("max_iterations", None)
        critique_threshold = payload.get("critique_threshold", None)

        # convert to BaseMessage objects for graph
        msgs = dicts_to_base_messages(client_messages)

        # ensure there's at least a user & assistant placeholder because some nodes expect AIMessage
        if not msgs:
            msgs = [HumanMessage(content=user_query), AIMessage(content="")]

        if not any(isinstance(m, AIMessage) for m in msgs):
            msgs.append(AIMessage(content=""))

        # build initial state dict - this matches MyState TypedDict shape
        state: Dict[str, Any] = {
            "user_query": user_query,
            "messages": msgs,
        }
        # optional overrides
        if max_iterations is not None:
            state["max_iterations"] = int(max_iterations)
        if critique_threshold is not None:
            state["critique_threshold"] = float(critique_threshold)

        # invoke compiled graph (synchronous)
        result = compiled_app.invoke(state)

        # convert returned messages to serializable dicts
        out_messages = result.get("messages", [])
        # convert BaseMessage objects -> dicts if needed
        if out_messages and not isinstance(out_messages[0], dict):
            out_messages = base_messages_to_dicts(out_messages)

        response = {
            "user_query": result.get("user_query"),
            "final_answer": result.get("final_answer"),
            "messages": out_messages,
            "used_contexts": result.get("used_contexts", []),
            "retrieved_by_subquery": result.get("retrieved_by_subquery", {}),
            "relevance_score": result.get("relevance_score"),
            "critique_verdict": result.get("critique_verdict"),
            "iterations": result.get("iterations"),
        }
        return jsonify(response)
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"error": str(e), "trace": tb}), 500

# health
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    print(f"Starting server on {HOST}:{PORT} ...")
    # Use debug=False in production
    app.run(host=HOST, port=PORT, debug=True)
