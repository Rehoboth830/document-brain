content = '''\
"use client"
import { useState, useEffect } from "react"
import { DocumentState } from "@/types"
import { api } from "@/lib/api"

function generateSessionId(): string {
  return Math.random().toString(36).substring(2, 10)
}

async function verifySession(sessionId: string): Promise<boolean> {
  try {
    const res = await api.get("/health")
    return res.data.document_loaded === true
  } catch {
    return false
  }
}

export function useSession() {
  const [session, setSession] = useState<DocumentState>({
    loaded: false,
    name: "",
    chunks: 0,
    sessionId: "",
  })
  const [ready, setReady] = useState(false)

  useEffect(() => {
    async function init() {
      if (typeof window === "undefined") return

      const stored = localStorage.getItem("db_session_id")
      const storedName = localStorage.getItem("db_document_name")
      const storedChunks = localStorage.getItem("db_chunks")
      const sessionId = stored || generateSessionId()

      if (!stored) {
        localStorage.setItem("db_session_id", sessionId)
        setSession({ loaded: false, name: "", chunks: 0, sessionId })
        setReady(true)
        return
      }

      if (storedName && storedChunks) {
        setSession({
          loaded: true,
          name: storedName,
          chunks: parseInt(storedChunks),
          sessionId,
        })
      } else {
        setSession({ loaded: false, name: "", chunks: 0, sessionId })
      }
      setReady(true)
    }
    init()
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

  return { session, setDocumentLoaded, clearDocument, ready }
}
'''

with open("hooks/useSession.ts", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
print("useSession.ts updated")
