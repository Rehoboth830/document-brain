"use client"
import { motion } from "framer-motion"
import { Logo } from "./Logo"
import { UploadPanel } from "@/components/upload/UploadPanel"
import { DocumentState } from "@/types"
import { Code2, Cpu, Database, Zap } from "lucide-react"

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
      className="w-72 shrink-0 glass-strong border-r border-brain-border flex flex-col h-screen overflow-hidden"
      initial={{ x: -280, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ type: "spring", stiffness: 200, damping: 25 }}
    >
      <div className="p-5 border-b border-brain-border shrink-0">
        <Logo size="sm" />
        <p className="text-xs text-brain-muted mt-2">
          Intelligent document Q&A with source citations
        </p>
      </div>

      <div className="flex-1 overflow-y-auto">
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
            <div className="w-1.5 h-1.5 rounded-full bg-brain-success animate-pulse shrink-0" />
            <span className="text-xs font-mono text-brain-muted truncate">{session.sessionId}</span>
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
                <div className="w-6 h-6 rounded-md bg-brain-card border border-brain-border flex items-center justify-center shrink-0">
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
      </div>

      <div className="p-4 border-t border-brain-border shrink-0">
        <div className="space-y-1">
          <p className="text-xs font-medium text-brain-text">Akinde Olugbenga Tope</p>
          <p className="text-xs text-brain-muted">IBM AI Engineering | GenAI | RAG</p>
          <a
            href="https://github.com/Rehoboth830/document-brain"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs text-brain-muted hover:text-brain-accent transition-colors mt-2"
          >
            <Code2 size={12} />
            View source code
          </a>
        </div>
      </div>
    </motion.aside>
  )
}
