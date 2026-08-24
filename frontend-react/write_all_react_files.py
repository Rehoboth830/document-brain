import os

files = {}

files["components/ui/Sidebar.tsx"] = '''\
"use client"
import { motion } from "framer-motion"
import { Logo } from "./Logo"
import { UploadPanel } from "@/components/upload/UploadPanel"
import { DocumentState } from "@/types"
import { Github, Cpu, Database, Zap } from "lucide-react"

interface SidebarProps {
  session: DocumentState
  onDocumentLoaded: (name: string, chunks: number) => void
  onClear: () => void
}

const STACK = [
  { icon: Database, label: "Pinecone", desc: "Vector store" },
  { icon: Zap, label: "Groq", desc: "LLM inference" },
  { icon: Cpu, label: "LangChain", desc: "RAG pipeline" },
]

export function Sidebar({ session, onDocumentLoaded, onClear }: SidebarProps) {
  return (
    <motion.aside
      className="w-72 shrink-0 glass-strong border-r border-brain-border flex flex-col h-full"
      initial={{ x: -280, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ type: "spring", stiffness: 200, damping: 25 }}
    >
      <div className="p-5 border-b border-brain-border">
        <Logo size="sm" />
        <p className="text-xs text-brain-muted mt-2">
          Intelligent document Q&A with source citations
        </p>
      </div>

      <div className="p-4 border-b border-brain-border">
        <p className="text-xs font-medium text-brain-muted uppercase tracking-wider mb-3">
          Document
        </p>
        <UploadPanel
          session={session}
          onDocumentLoaded={onDocumentLoaded}
          onClear={onClear}
        />
      </div>

      <div className="p-4 border-b border-brain-border">
        <p className="text-xs font-medium text-brain-muted uppercase tracking-wider mb-3">
          Session
        </p>
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-brain-bg border border-brain-border">
          <div className="w-1.5 h-1.5 rounded-full bg-brain-success animate-pulse" />
          <span className="text-xs font-mono text-brain-muted">{session.sessionId}</span>
        </div>
        <p className="text-xs text-brain-muted mt-2">
          Your session persists across browser refreshes.
        </p>
      </div>

      <div className="p-4 border-b border-brain-border">
        <p className="text-xs font-medium text-brain-muted uppercase tracking-wider mb-3">
          Stack
        </p>
        <div className="space-y-2">
          {STACK.map(({ icon: Icon, label, desc }) => (
            <div key={label} className="flex items-center gap-2.5">
              <div className="w-6 h-6 rounded-md bg-brain-card border border-brain-border flex items-center justify-center">
                <Icon size={12} className="text-brain-accent" />
              </div>
              <div>
                <p className="text-xs font-medium text-brain-text">{label}</p>
                <p className="text-xs text-brain-muted">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-auto p-4">
        <div className="space-y-1">
          <p className="text-xs font-medium text-brain-text">Akinde Olugbenga Tope</p>
          <p className="text-xs text-brain-muted">IBM AI Engineering | GenAI | RAG</p>
          <a
            href="https://github.com/Rehoboth830/document-brain"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs text-brain-muted hover:text-brain-accent transition-colors mt-2"
          >
            <Github size={12} />
            View source code
          </a>
        </div>
      </div>
    </motion.aside>
  )
}
'''

files["components/ui/Logo.tsx"] = '''\
"use client"
import { motion } from "framer-motion"

export function Logo({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sizes = {
    sm: { icon: 28, text: "text-lg" },
    md: { icon: 36, text: "text-2xl" },
    lg: { icon: 48, text: "text-4xl" },
  }
  const s = sizes[size]

  return (
    <motion.div
      className="flex items-center gap-3"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <motion.div
        className="relative flex items-center justify-center rounded-xl bg-gradient-to-br from-brain-accent-dim to-brain-card"
        style={{ width: s.icon, height: s.icon }}
        whileHover={{ scale: 1.05 }}
        transition={{ type: "spring", stiffness: 400 }}
      >
        <svg width={s.icon * 0.6} height={s.icon * 0.6} viewBox="0 0 24 24" fill="none">
          <path d="M12 2C8.5 2 6 4.5 6 7.5C6 9 6.5 10.5 7.5 11.5C6.5 12 6 13 6 14C6 16 7.5 17.5 9.5 17.5H10V20C10 21.1 10.9 22 12 22C13.1 22 14 21.1 14 20V17.5H14.5C16.5 17.5 18 16 18 14C18 13 17.5 12 16.5 11.5C17.5 10.5 18 9 18 7.5C18 4.5 15.5 2 12 2Z" fill="#4a9eff" opacity="0.9"/>
          <circle cx="10" cy="8" r="1.5" fill="white" opacity="0.8"/>
          <circle cx="14" cy="8" r="1.5" fill="white" opacity="0.8"/>
          <path d="M10 11H14" stroke="white" strokeWidth="1.5" strokeLinecap="round" opacity="0.6"/>
        </svg>
        <motion.div
          className="absolute inset-0 rounded-xl"
          style={{ background: "radial-gradient(circle at 50% 0%, rgba(74,158,255,0.3), transparent 70%)" }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 3, repeat: Infinity }}
        />
      </motion.div>
      <div>
        <span className={"font-bold " + s.text + " text-gradient"}>Document</span>
        <span className={"font-light " + s.text + " text-brain-text"}> Brain</span>
      </div>
    </motion.div>
  )
}
'''

files["components/upload/UploadPanel.tsx"] = '''\
"use client"
import { useState, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Upload, Link, FileText, CheckCircle, Loader2, X, Globe } from "lucide-react"
import { uploadFile, uploadUrl, clearSession } from "@/lib/api"
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
      const result = await uploadFile(file, session.sessionId)
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
  }, [session.sessionId, onDocumentLoaded])

  const handleUrl = async () => {
    if (!urlInput.trim()) return
    setIsLoading(true)
    setError("")
    setProgress(0)
    const interval = setInterval(() => setProgress(p => Math.min(p + 1, 85)), 300)
    try {
      const result = await uploadUrl(urlInput.trim(), session.sessionId)
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
    try { await clearSession(session.sessionId) } catch {}
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

files["app/page.tsx"] = '''\
"use client"
import { useSession } from "@/hooks/useSession"
import { Sidebar } from "@/components/ui/Sidebar"
import { ChatInterface } from "@/components/chat/ChatInterface"
import { motion } from "framer-motion"

export default function Home() {
  const { session, setDocumentLoaded, clearDocument } = useSession()

  return (
    <main className="flex h-screen bg-brain-bg overflow-hidden">
      <div
        className="absolute inset-0 opacity-30 pointer-events-none"
        style={{ background: "radial-gradient(ellipse at 20% 50%, rgba(74,158,255,0.08) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(167,139,250,0.06) 0%, transparent 60%)" }}
      />
      <Sidebar session={session} onDocumentLoaded={setDocumentLoaded} onClear={clearDocument} />
      <motion.div
        className="flex-1 flex flex-col min-w-0"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <div className="px-6 py-4 border-b border-brain-border glass-strong">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-sm font-semibold text-brain-text">
                {session.loaded ? session.name : "No document loaded"}
              </h1>
              <p className="text-xs text-brain-muted">
                {session.loaded
                  ? session.chunks.toLocaleString() + " chunks indexed in Pinecone"
                  : "Upload a document from the sidebar to begin"}
              </p>
            </div>
            {session.loaded && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brain-card border border-brain-border">
                <div className="w-1.5 h-1.5 rounded-full bg-brain-success animate-pulse" />
                <span className="text-xs text-brain-muted">Ready</span>
              </div>
            )}
          </div>
        </div>
        <ChatInterface session={session} />
      </motion.div>
    </main>
  )
}
'''

files["app/layout.tsx"] = '''\
import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Document Brain - Intelligent Document Q&A",
  description: "Ask questions about any document with AI-powered source citations",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}
'''

files["hooks/useSession.ts"] = '''\
import { useState, useEffect } from "react"
import { DocumentState } from "@/types"

function generateSessionId(): string {
  return Math.random().toString(36).substring(2, 10)
}

export function useSession() {
  const [session, setSession] = useState<DocumentState>({
    loaded: false,
    name: "",
    chunks: 0,
    sessionId: "",
  })

  useEffect(() => {
    const stored = localStorage.getItem("db_session_id")
    const storedName = localStorage.getItem("db_document_name")
    const storedChunks = localStorage.getItem("db_chunks")
    const sessionId = stored || generateSessionId()
    if (!stored) localStorage.setItem("db_session_id", sessionId)
    setSession({
      loaded: !!storedName,
      name: storedName || "",
      chunks: storedChunks ? parseInt(storedChunks) : 0,
      sessionId,
    })
  }, [])

  const setDocumentLoaded = (name: string, chunks: number) => {
    localStorage.setItem("db_document_name", name)
    localStorage.setItem("db_chunks", chunks.toString())
    setSession(prev => ({ ...prev, loaded: true, name, chunks }))
  }

  const clearDocument = () => {
    const newSessionId = generateSessionId()
    localStorage.setItem("db_session_id", newSessionId)
    localStorage.removeItem("db_document_name")
    localStorage.removeItem("db_chunks")
    setSession({ loaded: false, name: "", chunks: 0, sessionId: newSessionId })
  }

  return { session, setDocumentLoaded, clearDocument }
}
'''

files["types/index.ts"] = '''\
export interface Citation {
  source: string
  page_number: string
  source_type: string
  similarity: number
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  citations?: Citation[]
  timestamp: Date
  isStreaming?: boolean
}

export interface DocumentState {
  loaded: boolean
  name: string
  chunks: number
  sessionId: string
}

export interface QueryResponse {
  answer: string
  citations: Citation[]
  question: string
  confidence: string
}
'''

files["lib/api.ts"] = '''\
import axios from "axios"
import { QueryResponse } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
})

export async function uploadFile(file: File, sessionId: string): Promise<{ chunks_stored: number }> {
  const formData = new FormData()
  formData.append("file", file)
  formData.append("session_id", sessionId)
  const res = await api.post("/upload/file", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return res.data
}

export async function uploadUrl(url: string, sessionId: string): Promise<{ chunks_stored: number }> {
  const res = await api.post("/upload/url", { url, session_id: sessionId })
  return res.data
}

export async function queryDocument(
  question: string,
  sessionId: string,
  onToken: (token: string) => void
): Promise<QueryResponse> {
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

export async function clearSession(sessionId: string): Promise<void> {
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

files[".env.local"] = "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1\n"

for path, content in files.items():
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("Written: " + path)

print("\nAll files written successfully")
