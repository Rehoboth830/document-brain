import os

# Fix api.ts - read session from localStorage directly
api_content = '''\
import axios from "axios"
import { QueryResponse } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
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
'''

with open("lib/api.ts", "w", encoding="utf-8", newline="\n") as f:
    f.write(api_content)
print("Written: lib/api.ts")

# Fix UploadPanel - remove sessionId from props, read from localStorage directly
upload_panel = '''\
"use client"
import { useState, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Upload, Link, FileText, CheckCircle, Loader2, X, Globe } from "lucide-react"
import { uploadFile, uploadUrl, clearSession, getSessionId } from "@/lib/api"
import { DocumentState } from "@/types"

interface UploadPanelProps {
  session: DocumentState
  onDocumentLoaded: (name: string, chunks: number) => void
  onClear: () => void
}

export function UploadPanel({ session, onDocumentLoaded, onClear }: UploadPanelProps) {
  const [mode, setMode] = useState<"file" | "url">("file")
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [urlInput, setUrlInput] = useState("")
  const [error, setError] = useState("")
  const [progress, setProgress] = useState(0)

  const handleFile = useCallback(async (file: File) => {
    if (!file) return
    setIsLoading(true)
    setError("")
    setProgress(0)
    const interval = setInterval(() => setProgress(p => Math.min(p + 2, 90)), 200)
    try {
      const result = await uploadFile(file)
      clearInterval(interval)
      setProgress(100)
      setTimeout(() => {
        onDocumentLoaded(file.name, result.chunks_stored)
        setProgress(0)
      }, 500)
    } catch (e: any) {
      clearInterval(interval)
      setError(e.response?.data?.detail || "Upload failed. Is the API running?")
      setProgress(0)
    } finally {
      setIsLoading(false)
    }
  }, [onDocumentLoaded])

  const handleUrl = async () => {
    if (!urlInput.trim()) return
    setIsLoading(true)
    setError("")
    setProgress(0)
    const interval = setInterval(() => setProgress(p => Math.min(p + 1, 85)), 300)
    try {
      const result = await uploadUrl(urlInput.trim())
      clearInterval(interval)
      setProgress(100)
      setTimeout(() => {
        onDocumentLoaded(urlInput.trim().slice(0, 40) + "...", result.chunks_stored)
        setUrlInput("")
        setProgress(0)
      }, 500)
    } catch (e: any) {
      clearInterval(interval)
      setError(e.response?.data?.detail || "Failed to fetch URL")
      setProgress(0)
    } finally {
      setIsLoading(false)
    }
  }

  const handleClear = async () => {
    try { await clearSession() } catch {}
    onClear()
  }

  if (session.loaded) {
    return (
      <motion.div
        className="glass rounded-2xl p-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <CheckCircle className="text-brain-success shrink-0" size={16} />
            <div className="min-w-0">
              <p className="text-xs text-brain-muted">Document loaded</p>
              <p className="text-sm font-medium text-brain-text truncate">{session.name}</p>
              <p className="text-xs text-brain-accent">{session.chunks.toLocaleString()} chunks indexed</p>
            </div>
          </div>
          <button
            onClick={handleClear}
            className="shrink-0 p-1.5 rounded-lg hover:bg-brain-border transition-colors text-brain-muted hover:text-brain-error"
          >
            <X size={14} />
          </button>
        </div>
      </motion.div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex rounded-xl overflow-hidden border border-brain-border">
        {(["file", "url"] as const).map((id) => (
          <button
            key={id}
            onClick={() => setMode(id)}
            className={"flex-1 flex items-center justify-center gap-1.5 py-2 text-sm font-medium transition-all " + (mode === id ? "bg-brain-accent text-white" : "bg-brain-card text-brain-muted hover:text-brain-text")}
          >
            {id === "file" ? <FileText size={14} /> : <Globe size={14} />}
            {id === "file" ? "File" : "URL"}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {mode === "file" ? (
          <motion.div key="file" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }}>
            <label
              className={"relative flex flex-col items-center justify-center gap-3 p-6 rounded-2xl border-2 border-dashed cursor-pointer transition-all " + (isDragging ? "border-brain-accent bg-brain-accent-dim" : "border-brain-border hover:border-brain-accent hover:bg-brain-card")}
              onDragOver={e => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={e => { e.preventDefault(); setIsDragging(false); const file = e.dataTransfer.files[0]; if (file) handleFile(file) }}
            >
              <input type="file" className="hidden" accept=".pdf,.docx,.doc" onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f) }} disabled={isLoading} />
              {isLoading ? <Loader2 className="text-brain-accent animate-spin" size={28} /> : <Upload className="text-brain-accent" size={28} />}
              <div className="text-center">
                <p className="text-sm font-medium text-brain-text">{isLoading ? "Processing..." : "Drop file or click to upload"}</p>
                <p className="text-xs text-brain-muted mt-1">PDF, DOCX supported</p>
              </div>
              {progress > 0 && (
                <div className="w-full bg-brain-border rounded-full h-1.5">
                  <motion.div className="bg-brain-accent h-1.5 rounded-full" initial={{ width: 0 }} animate={{ width: progress + "%" }} transition={{ ease: "easeOut" }} />
                </div>
              )}
            </label>
          </motion.div>
        ) : (
          <motion.div key="url" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }} className="space-y-2">
            <input
              type="url"
              value={urlInput}
              onChange={e => setUrlInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleUrl()}
              placeholder="https://example.com/article"
              className="w-full px-3 py-2.5 rounded-xl bg-brain-card border border-brain-border text-brain-text text-sm placeholder:text-brain-muted focus:outline-none focus:border-brain-accent transition-colors"
              disabled={isLoading}
            />
            <button
              onClick={handleUrl}
              disabled={isLoading || !urlInput.trim()}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-brain-accent text-white text-sm font-medium hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? <Loader2 size={14} className="animate-spin" /> : <Link size={14} />}
              {isLoading ? "Loading..." : "Load URL"}
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {error && (
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xs text-brain-error bg-red-950/30 border border-red-900/30 rounded-lg px-3 py-2">
          {error}
        </motion.p>
      )}
    </div>
  )
}
'''

with open("components/upload/UploadPanel.tsx", "w", encoding="utf-8", newline="\n") as f:
    f.write(upload_panel)
print("Written: components/upload/UploadPanel.tsx")

# Fix ChatInterface - remove session param, read from localStorage
chat_interface = '''\
"use client"
import { useState, useRef, useEffect, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Send, Loader2, Brain } from "lucide-react"
import { MessageBubble } from "./MessageBubble"
import { queryDocument, getSessionId } from "@/lib/api"
import { Message, DocumentState } from "@/types"

const SUGGESTED = [
  "What is this document about?",
  "Summarize the key points",
  "Who is the author?",
  "What are the main conclusions?",
]

interface ChatInterfaceProps {
  session: DocumentState
}

export function ChatInterface({ session }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = useCallback(async (question: string) => {
    if (!question.trim() || isLoading || !session.loaded) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: question.trim(),
      timestamp: new Date(),
    }

    const assistantId = (Date.now() + 1).toString()
    const assistantMessage: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      citations: [],
      timestamp: new Date(),
      isStreaming: true,
    }

    setMessages(prev => [...prev, userMessage, assistantMessage])
    setInput("")
    setIsLoading(true)

    try {
      const result = await queryDocument(
        question.trim(),
        (token: string) => {
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantId
                ? { ...m, content: m.content + token }
                : m
            )
          )
        }
      )

      setMessages(prev =>
        prev.map(m =>
          m.id === assistantId
            ? { ...m, content: result.answer, citations: result.citations, isStreaming: false }
            : m
        )
      )
    } catch (e: any) {
      const errorMsg = e.response?.data?.detail || "Something went wrong. Please try again."
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantId
            ? { ...m, content: errorMsg, isStreaming: false }
            : m
        )
      )
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }, [isLoading, session])

  if (!session.loaded) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-6 p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center space-y-4"
        >
          <motion.div
            animate={{ y: [0, -8, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          >
            <Brain size={56} className="text-brain-accent mx-auto opacity-60" />
          </motion.div>
          <div>
            <h2 className="text-xl font-semibold text-brain-text mb-2">
              Upload a document to begin
            </h2>
            <p className="text-sm text-brain-muted max-w-md">
              Document Brain reads any PDF, Word document, or webpage and answers your questions with precise source citations.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-2 max-w-sm mt-4">
            {["PDF files", "Word documents", "Web URLs", "Any language"].map(f => (
              <div key={f} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-brain-card border border-brain-border">
                <div className="w-1.5 h-1.5 rounded-full bg-brain-accent" />
                <span className="text-xs text-brain-muted">{f}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        <AnimatePresence initial={false}>
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-3"
            >
              <p className="text-xs text-brain-muted text-center">
                {session.name} loaded — {session.chunks.toLocaleString()} chunks indexed
              </p>
              <p className="text-xs text-brain-muted text-center mb-4">Try asking:</p>
              <div className="grid grid-cols-1 gap-2">
                {SUGGESTED.map((s, i) => (
                  <motion.button
                    key={s}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.08 }}
                    onClick={() => sendMessage(s)}
                    className="text-left px-4 py-2.5 rounded-xl glass text-sm text-brain-muted hover:text-brain-text hover:border-brain-accent/40 transition-all"
                  >
                    {s}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}
          {messages.map(message => (
            <MessageBubble key={message.id} message={message} />
          ))}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      <div className="px-4 pb-4 pt-2 border-t border-brain-border">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendMessage(input)}
            placeholder="Ask anything about your document..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 rounded-xl bg-brain-card border border-brain-border text-brain-text text-sm placeholder:text-brain-muted focus:outline-none focus:border-brain-accent transition-colors disabled:opacity-50"
          />
          <motion.button
            onClick={() => sendMessage(input)}
            disabled={isLoading || !input.trim()}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-4 py-3 rounded-xl bg-brain-accent text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-blue-500 transition-colors"
          >
            {isLoading
              ? <Loader2 size={18} className="animate-spin" />
              : <Send size={18} />
            }
          </motion.button>
        </div>
        <p className="text-xs text-brain-muted text-center mt-2">
          Powered by Pinecone + Groq + LangChain
        </p>
      </div>
    </div>
  )
}
'''

with open("components/chat/ChatInterface.tsx", "w", encoding="utf-8", newline="\n") as f:
    f.write(chat_interface)
print("Written: components/chat/ChatInterface.tsx")

print("\nAll files fixed. Session ID now read directly from localStorage at call time.")
