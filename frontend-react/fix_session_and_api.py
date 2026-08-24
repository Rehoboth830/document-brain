import os

# Fix 1: useSession.ts - generate and lock session ID immediately
session_hook = '''\
"use client"
import { useState, useEffect } from "react"
import { DocumentState } from "@/types"

function generateSessionId(): string {
  return Math.random().toString(36).substring(2, 10)
}

function getOrCreateSessionId(): string {
  if (typeof window === "undefined") return ""
  let id = localStorage.getItem("db_session_id")
  if (!id) {
    id = generateSessionId()
    localStorage.setItem("db_session_id", id)
  }
  return id
}

export function useSession() {
  const [session, setSession] = useState<DocumentState>(() => {
    return {
      loaded: false,
      name: "",
      chunks: 0,
      sessionId: "",
    }
  })

  useEffect(() => {
    const sessionId = getOrCreateSessionId()
    const storedName = localStorage.getItem("db_document_name")
    const storedChunks = localStorage.getItem("db_chunks")

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

with open("hooks/useSession.ts", "w", encoding="utf-8", newline="\n") as f:
    f.write(session_hook)
print("Written: hooks/useSession.ts")

# Fix 2: Add a debug display to page.tsx so we always see the session ID being used
page = '''\
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
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono text-brain-muted opacity-50">
                {session.sessionId}
              </span>
              {session.loaded && (
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brain-card border border-brain-border">
                  <div className="w-1.5 h-1.5 rounded-full bg-brain-success animate-pulse" />
                  <span className="text-xs text-brain-muted">Ready</span>
                </div>
              )}
            </div>
          </div>
        </div>
        <ChatInterface session={session} />
      </motion.div>
    </main>
  )
}
'''

with open("app/page.tsx", "w", encoding="utf-8", newline="\n") as f:
    f.write(page)
print("Written: app/page.tsx")

print("\nDone. Session ID is now locked in localStorage on first visit.")
