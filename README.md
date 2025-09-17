# IITI_GPT 🚀

**Author:** Mohit Garhewal  
**University:** Indian Institute of Technology, Indore  
**Department:** Metallurgical Engineering and Materials Science

---

## 1. Introduction

IITI-GPT is a full-stack + ML prototype designed to help students at IITI get accurate answers to their questions about the institute. It provides a conversational AI interface with chat logging and optional Retrieval-Augmented Generation (RAG) support, built for fast experimentation and easy deployment.

---

## Project Aim

The main goal of IITI-GPT is to resolve students’ queries related to IITI—whether about academics, campus facilities, events, or procedures—by using intelligent AI agents. When a student asks a question, the system:

1. **Reasons**: The AI agent analyzes the question to understand its intent and context.
2. **Plans**: It determines the best approach to find the answer, including which sources to consult and how to structure the response.
3. **Executes**: The agent retrieves relevant information from trusted documents and databases, filters out noise, and synthesizes a clear, accurate answer.

This process ensures that students receive reliable, context-aware responses quickly and conveniently on their mobile devices.

### How AI Agents Work

- **Reasoning Agent**: Interprets the user’s question, identifies key topics, and decides what information is needed.
- **Planning Agent**: Chooses the most relevant sources (such as official IITI documents or FAQs), organizes the search, and outlines the answer.
- **Execution Agent**: Fetches data, applies filters to ensure accuracy and relevance, and generates a concise, user-friendly response.

By combining these agents, IITI-GPT delivers high-quality answers tailored to each student’s needs, making campus information accessible and actionable.

---

## 2. Source Code

- **Main repo:** [https://github.com/mohitgarhewal/IITI_Gpt.git](https://github.com/mohitgarhewal/IITI_Gpt.git)  
- **Frontend:** [https://github.com/mohitgarhewal/IITI_Gpt/tree/main/IITI_gpt_frontend](https://github.com/mohitgarhewal/IITI_Gpt/tree/main/IITI_gpt_frontend)  
- **Backend:** [https://github.com/mohitgarhewal/IITI_Gpt/tree/main/IITI_gpt_backend](https://github.com/mohitgarhewal/IITI_Gpt/tree/main/IITI_gpt_backend)

---

## 3. System Design Document

Detailed design (architecture, data design, components, tech choices) is available here:  
`<LINK_TO_DESIGN_DOCUMENT>`

**Quick summary**
- **Architecture:** React (UI) ↔ FastAPI (Backend) ↔ ML Inference Service. Postgres for persistence, Redis for cache/pubsub, S3/MinIO for assets.
- **Data model (core):** `users`, `chats`, `messages`, `interaction_logs` (JSONB for flexible metadata).
- **Components:** UI · Auth · API · Inference · Storage · DB · Cache.
- **Tech choices (short):**
  - **React + TypeScript** — rapid UI + type safety
  - **FastAPI (Python)** — async, ML-friendly
  - **PyTorch / Transformers** — standard for conversational models
  - **Postgres + JSONB** — reliable + flexible fields
  - **Redis** — low-latency cache / pubsub

---

## 4. How the System Works

- **Student asks a question** via the chat interface (web or mobile).
- **AI agents reason, plan, and execute**:
  - The reasoning agent interprets the query and identifies what information is needed.
  - The planning agent selects trusted sources (IITI docs, FAQs, official announcements) and decides how to answer.
  - The execution agent retrieves, filters, and synthesizes the best possible answer.
- **Response delivered instantly** to the student, with chat history logged for future reference.
- **Mobile-first design** ensures answers are accessible anywhere, anytime.

---

## 5. Interaction Logs 🗂️

- **Chat history exports:** [https://chatgpt.com/share/68ca6f00-e5c8-8004-a15f-2938e0b6f4ba](https://chatgpt.com/share/68ca6f00-e5c8-8004-a15f-2938e0b6f4ba)

---

## 6. Demo ▶️

- **Demo video & images link :** https://drive.google.com/drive/folders/1GCt1-ZO-TeFmp87LauH0ZlwoutAXh-9j?usp=sharing

---

## 7. Contact

- **Email:** mems230005028@iiti.ac.in

---
