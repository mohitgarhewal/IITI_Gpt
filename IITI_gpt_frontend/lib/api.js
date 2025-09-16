// frontend/src/api.js
const BACKEND_URL = "http://127.0.0.1:5000"

export async function sendChat(userQuery, messages = [], opts = {}) {
  const body = {
    user_query: userQuery,
    messages: messages,
    max_iterations: opts.max_iterations,
    critique_threshold: opts.critique_threshold,
  }

  const resp = await fetch(`${BACKEND_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ error: "Unknown error" }))
    throw new Error(err.error || JSON.stringify(err))
  }
  const data = await resp.json()
  return data
}
