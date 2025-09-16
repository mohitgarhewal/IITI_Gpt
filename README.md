# IITI_GPT 🚀

**Author:** Mohit Garhewal  
**University:** Indian Institute of Technology, Indore
**Department:** Metallurgical Engineering and Materials Science

---

## 1. Introduction
A concise full‑stack + ML prototype that provides a conversational AI with chat logging and optional RAG support. Built for fast experimentation and easy deployment.

---

## 2. Source code
- **Main repo:** `https://github.com/mohitgarhewal/IITI_Gpt.git`  
- **Frontend:** `https://github.com/mohitgarhewal/IITI_Gpt/tree/main/IITI_gpt_frontend`  
- **Backend:** `https://github.com/mohitgarhewal/IITI_Gpt/tree/main/IITI_gpt_backend`


---

## 3. System design document
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

## 4. Interaction logs  🗂️
**(Reserved — to be provided by the author)**

- **Prompts & templates:** (space to paste prompt templates and versions)
- **Chat history exports:** (space to paste or link JSON/CSV exports)

---

## 5. Demo ▶️
- **Demo video:** `demos/iiti_gpt_demo.mp4` (or external link)  
- **Screenshots:** `docs/screenshots/chat-ui-1.png`, `docs/screenshots/admin-1.png`


---

## Contact
- **Email** mems230005028@iiti.ac.in

---


