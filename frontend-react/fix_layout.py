# Fix 1: Sidebar - make it scrollable and fix overflow
sidebar = '''\
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
'''

with open("components/ui/Sidebar.tsx", "w", encoding="utf-8", newline="\n") as f:
    f.write(sidebar)
print("Written: Sidebar.tsx - scrollable, no overflow")

# Fix 2: ChatInterface - fix scroll container
chat = '''\
"use client"
import { useState, useRef, useEffect, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Send, Loader2, Brain } from "lucide-react"
import { MessageBubble } from "./MessageBubble"
import { queryDocument } from "@/lib/api"
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
  const scrollRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" })
    }
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
    <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-4 space-y-4"
        style={{ scrollBehavior: "smooth" }}
      >
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-3"
          >
            <p className="text-xs text-brain-muted text-center">
              {session.name} loaded
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
        <AnimatePresence initial={false}>
          {messages.map(message => (
            <MessageBubble key={message.id} message={message} />
          ))}
        </AnimatePresence>
        <div ref={bottomRef} className="h-1" />
      </div>

      <div className="px-4 pb-4 pt-2 border-t border-brain-border shrink-0 bg-brain-bg">
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
    f.write(chat)
print("Written: ChatInterface.tsx - scroll fixed")

# Fix 3: page.tsx - fix main layout height
page = '''\
"use client"
import { useSession } from "@/hooks/useSession"
import { Sidebar } from "@/components/ui/Sidebar"
import { ChatInterface } from "@/components/chat/ChatInterface"
import { motion } from "framer-motion"

export default function Home() {
  const { session, setDocumentLoaded, clearDocument } = useSession()

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-brain-bg">
      <div
        className="absolute inset-0 opacity-30 pointer-events-none"
        style={{ background: "radial-gradient(ellipse at 20% 50%, rgba(74,158,255,0.08) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(167,139,250,0.06) 0%, transparent 60%)" }}
      />
      <Sidebar session={session} onDocumentLoaded={setDocumentLoaded} onClear={clearDocument} />
      <motion.div
        className="flex-1 flex flex-col min-w-0 min-h-0 overflow-hidden"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <div className="px-6 py-4 border-b border-brain-border glass-strong shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-sm font-semibold text-brain-text truncate">
                {session.loaded ? session.name : "No document loaded"}
              </h1>
              <p className="text-xs text-brain-muted">
                {session.loaded
                  ? session.chunks.toLocaleString() + " chunks indexed in Pinecone"
                  : "Upload a document from the sidebar to begin"}
              </p>
            </div>
            {session.loaded && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brain-card border border-brain-border shrink-0">
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

with open("app/page.tsx", "w", encoding="utf-8", newline="\n") as f:
    f.write(page)
print("Written: app/page.tsx - layout fixed")

print("\nAll layout fixes applied")
