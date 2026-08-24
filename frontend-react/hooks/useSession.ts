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
