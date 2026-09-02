import axios from "axios"
import { QueryResponse } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 300000,
})

export function getSessionId(): string {
  if (typeof window === "undefined") return "default"
  let id = localStorage.getItem("db_session_id")
  if (!id) {
    id = Math.random().toString(36).substring(2, 10)
    localStorage.setItem("db_session_id", id)
  }
  return id
}

export async function uploadFile(file: File): Promise<{ chunks_stored: number }> {
  const sessionId = getSessionId()
  console.log("Uploading with session:", sessionId)
  const formData = new FormData()
  formData.append("file", file)
  formData.append("session_id", sessionId)
  const res = await api.post("/upload/file", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return res.data
}

export async function uploadUrl(url: string): Promise<{ chunks_stored: number }> {
  const sessionId = getSessionId()
  const res = await api.post("/upload/url", { url, session_id: sessionId })
  return res.data
}

export async function queryDocument(
  question: string,
  onToken: (token: string) => void
): Promise<QueryResponse> {
  const sessionId = getSessionId()
  console.log("Querying with session:", sessionId)
  const res = await api.post<QueryResponse>("/query", {
    question,
    session_id: sessionId,
    n_results: 5,
  })
  const words = res.data.answer.split(" ")
  for (let i = 0; i < words.length; i++) {
    await new Promise(r => setTimeout(r, 30))
    onToken(words[i] + (i < words.length - 1 ? " " : ""))
  }
  return res.data
}

export async function clearSession(): Promise<void> {
  const sessionId = getSessionId()
  await api.post("/session/clear", { session_id: sessionId })
}

export async function healthCheck(): Promise<boolean> {
  try {
    const res = await api.get("/health")
    return res.data.status === "healthy"
  } catch {
    return false
  }
}
