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
