pinecone_store = '''import os
import uuid
from pinecone import Pinecone, ServerlessSpec
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "document-brain"
DIMENSION = 384
METRIC = "cosine"

_pc = None
_index = None
_ef = None


def get_ef():
    global _ef
    if _ef is None:
        _ef = embedding_functions.DefaultEmbeddingFunction()
    return _ef


def get_client():
    global _pc
    if _pc is None:
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in .env file.")
        _pc = Pinecone(api_key=api_key)
        print("Pinecone client initialized")
    return _pc


def get_index():
    global _index
    if _index is None:
        pc = get_client()
        existing = [i.name for i in pc.list_indexes()]
        if INDEX_NAME not in existing:
            print(f"Creating Pinecone index: {INDEX_NAME}")
            pc.create_index(
                name=INDEX_NAME,
                dimension=DIMENSION,
                metric=METRIC,
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print("Index created successfully")
        _index = pc.Index(INDEX_NAME)
        print(f"Connected to Pinecone index: {INDEX_NAME}")
    return _index


def store_chunks_pinecone(chunks: list[dict], namespace: str) -> int:
    index = get_index()
    ef = get_ef()

    texts = [chunk["text"] for chunk in chunks]
    print(f"Embedding {len(chunks)} chunks for namespace: {namespace}")
    embeddings = ef(texts)

    batch_size = 100
    stored = 0

    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i+batch_size]
        batch_embeddings = embeddings[i:i+batch_size]

        vectors = []
        for j, (chunk, embedding) in enumerate(zip(batch_chunks, batch_embeddings)):
            vectors.append({
                "id": f"{namespace}_{chunk[\'chunk_id\']}",
                "values": embedding,
                "metadata": {
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "source_type": chunk["source_type"],
                    "page_number": str(chunk["page_number"])
                }
            })

        index.upsert(vectors=vectors, namespace=namespace)
        stored += len(vectors)
        print(f"Stored {stored}/{len(chunks)} chunks...")

    print(f"Pinecone store complete: {stored} chunks in namespace {namespace}")
    return stored


def retrieve_chunks_pinecone(query: str, namespace: str, n_results: int = 5) -> list[dict]:
    index = get_index()
    ef = get_ef()

    print(f"Retrieving top {n_results} chunks from namespace: {namespace}")
    query_embedding = ef([query])[0]

    results = index.query(
        vector=query_embedding,
        top_k=n_results,
        namespace=namespace,
        include_metadata=True
    )

    chunks = []
    for i, match in enumerate(results.matches):
        chunks.append({
            "rank": i + 1,
            "text": match.metadata.get("text", ""),
            "source": match.metadata.get("source", ""),
            "source_type": match.metadata.get("source_type", ""),
            "page_number": match.metadata.get("page_number", "?"),
            "similarity": round(match.score, 4)
        })

    print(f"Retrieved {len(chunks)} chunks")
    return chunks


def get_namespace_count(namespace: str) -> int:
    try:
        index = get_index()
        stats = index.describe_index_stats()
        ns_stats = stats.namespaces.get(namespace)
        if ns_stats:
            return ns_stats.vector_count
        return 0
    except Exception:
        return 0


def clear_namespace(namespace: str):
    try:
        index = get_index()
        index.delete(delete_all=True, namespace=namespace)
        print(f"Namespace cleared: {namespace}")
    except Exception as e:
        print(f"Could not clear namespace: {e}")


def generate_session_id() -> str:
    return str(uuid.uuid4())[:8]
'''

rag_chain = '''import re
from backend.core.embeddings.pinecone_store import (
    store_chunks_pinecone,
    retrieve_chunks_pinecone,
    get_namespace_count,
    clear_namespace,
    generate_session_id
)
from backend.core.ingestion.ingestion import ingest_document
from backend.core.rag.llm import get_llm
from backend.core.rag.prompt import get_prompt


def format_context(chunks: list[dict]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[Source {i+1} | {chunk[\'source\']} | Page {chunk[\'page_number\']}]\\n{chunk[\'text\']}"
        )
    return "\\n\\n---\\n\\n".join(context_parts)


def extract_citations(chunks: list[dict]) -> list[dict]:
    citations = []
    seen = set()
    for chunk in chunks:
        key = f"{chunk[\'source\']}_{chunk[\'page_number\']}"
        if key not in seen:
            seen.add(key)
            citations.append({
                "source": chunk["source"],
                "page_number": chunk["page_number"],
                "source_type": chunk["source_type"],
                "similarity": chunk["similarity"]
            })
    return citations


def clean_answer(text: str) -> str:
    if "</think>" in text:
        text = text.split("</think>")[-1]
    text = text.strip()
    return text


def load_document(source: str, session_id: str = None) -> tuple[int, str]:
    if session_id is None:
        session_id = generate_session_id()

    print(f"Loading document: {source[:60]}")
    print(f"Session ID: {session_id}")

    clear_namespace(session_id)
    chunks = ingest_document(source)
    stored = store_chunks_pinecone(chunks, namespace=session_id)

    print(f"Document loaded: {stored} chunks in Pinecone namespace {session_id}")
    return stored, session_id


def ask(question: str, session_id: str, n_results: int = 5) -> dict:
    count = get_namespace_count(session_id)

    if count == 0:
        return {
            "answer": "No document loaded. Please upload a document first.",
            "citations": [],
            "question": question,
            "confidence": "none"
        }

    chunks = retrieve_chunks_pinecone(question, namespace=session_id, n_results=n_results)

    if not chunks:
        return {
            "answer": "I could not find relevant information in the document.",
            "citations": [],
            "question": question,
            "confidence": "low"
        }

    avg_similarity = sum(c["similarity"] for c in chunks) / len(chunks)
    if avg_similarity < 0.35:
        return {
            "answer": "I could not find relevant information about this in the provided document. Try rephrasing your question.",
            "citations": [],
            "question": question,
            "confidence": "low"
        }

    context = format_context(chunks)
    citations = extract_citations(chunks)

    llm = get_llm()
    prompt = get_prompt()
    chain = prompt | llm

    try:
        response = chain.invoke({
            "context": context,
            "question": question
        })
        answer = clean_answer(response.content)
    except Exception as e:
        error_msg = str(e).lower()
        if "rate limit" in error_msg or "429" in error_msg:
            answer = "The AI service is temporarily busy due to rate limits. Please wait 30 seconds and try again."
        else:
            answer = f"An error occurred: {str(e)}"

    return {
        "answer": answer,
        "citations": citations,
        "question": question,
        "confidence": "high"
    }
'''

streamlit_app = '''import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from backend.core.rag.rag_chain import load_document, ask
from backend.core.embeddings.pinecone_store import get_namespace_count, clear_namespace, generate_session_id

st.set_page_config(
    page_title="Document Brain",
    page_icon="brain",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2d3748;
    }
    .user-message {
        background: linear-gradient(135deg, #1e3a5f, #2d5986);
        border-radius: 12px 12px 4px 12px;
        padding: 14px 18px;
        margin: 8px 0;
        color: #e2e8f0;
        font-size: 14px;
        line-height: 1.7;
    }
    .assistant-message {
        background: linear-gradient(135deg, #1a2332, #243447);
        border-radius: 12px 12px 12px 4px;
        padding: 14px 18px;
        margin: 8px 0;
        color: #e2e8f0;
        font-size: 14px;
        line-height: 1.7;
        border-left: 3px solid #4a9eff;
    }
    .citation-card {
        background: #1e2535;
        border: 1px solid #2d3748;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 4px 0;
        font-size: 12px;
        color: #94a3b8;
    }
    .session-badge {
        background: #1a3a1a;
        color: #4ade80;
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 11px;
        font-family: monospace;
    }
    .warning-box {
        background: #2d2000;
        border: 1px solid #b45309;
        border-radius: 8px;
        padding: 10px 14px;
        color: #fbbf24;
        font-size: 13px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_loaded" not in st.session_state:
    st.session_state.document_loaded = False
if "document_name" not in st.session_state:
    st.session_state.document_name = ""
if "chunks_count" not in st.session_state:
    st.session_state.chunks_count = 0
if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()

with st.sidebar:
    st.markdown("## Document Brain")
    st.markdown("*Intelligent document Q&A*")
    st.markdown(
        f\'<div style="margin: 4px 0 12px">Session: \'
        f\'<span class="session-badge">{st.session_state.session_id}</span></div>\',
        unsafe_allow_html=True
    )
    st.markdown("---")

    source_type = st.radio(
        "Source type",
        ["PDF / Word File", "Web URL"],
        label_visibility="collapsed"
    )

    if source_type == "PDF / Word File":
        uploaded_file = st.file_uploader(
            "Upload document",
            type=["pdf", "docx", "doc"],
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            if st.button("Load Document", use_container_width=True):
                with st.spinner("Reading, embedding and storing in Pinecone..."):
                    try:
                        temp_path = f"data/uploads/{uploaded_file.name}"
                        os.makedirs("data/uploads", exist_ok=True)
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getvalue())
                        chunks_stored, session_id = load_document(
                            temp_path,
                            session_id=st.session_state.session_id
                        )
                        st.session_state.document_loaded = True
                        st.session_state.document_name = uploaded_file.name
                        st.session_state.chunks_count = chunks_stored
                        st.session_state.messages = []
                        st.success(f"Loaded: {uploaded_file.name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {str(e)}")

    else:
        url_input = st.text_input("Enter URL", placeholder="https://example.com/article")
        if st.button("Load URL", use_container_width=True):
            if url_input.strip():
                with st.spinner("Fetching and indexing..."):
                    try:
                        chunks_stored, session_id = load_document(
                            url_input.strip(),
                            session_id=st.session_state.session_id
                        )
                        st.session_state.document_loaded = True
                        st.session_state.document_name = url_input[:40] + "..."
                        st.session_state.chunks_count = chunks_stored
                        st.session_state.messages = []
                        st.success("URL loaded successfully")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {str(e)}")
            else:
                st.warning("Please enter a URL")

    st.markdown("---")

    if st.session_state.document_loaded:
        st.success(f"Ready - {st.session_state.chunks_count} chunks")
        st.markdown(f"**{st.session_state.document_name[:35]}**")
        if st.button("Clear & Load New", use_container_width=True):
            clear_namespace(st.session_state.session_id)
            st.session_state.session_id = generate_session_id()
            st.session_state.document_loaded = False
            st.session_state.document_name = ""
            st.session_state.messages = []
            st.rerun()
    else:
        st.info("No document loaded")

    st.markdown("---")
    st.markdown("**Built by**")
    st.markdown("Akinde Olugbenga Tope")
    st.markdown("IBM AI Engineering | GenAI | RAG")

st.markdown("# Document Brain")
st.markdown("*Intelligent document Q&A with source citations - powered by Pinecone + Groq*")

if not st.session_state.document_loaded:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Get Started")
        st.markdown("Upload a **PDF**, **Word document**, or paste a **URL** in the sidebar.")
        st.markdown("")
        st.markdown("**What you can do:**")
        st.markdown("- Ask questions in plain English")
        st.markdown("- Get answers with exact page citations")
        st.markdown("- Your document persists across sessions via Pinecone")
        st.markdown("- Each user gets a private isolated session")
else:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f\'<div class="user-message">{message["content"]}</div>\',
                unsafe_allow_html=True
            )
        else:
            content = message["content"]
            is_rate_limit = "rate limit" in content.lower() or "temporarily busy" in content.lower()

            if is_rate_limit:
                st.markdown(
                    f\'<div class="warning-box">{content}</div>\',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f\'<div class="assistant-message">{content}</div>\',
                    unsafe_allow_html=True
                )

            if message.get("citations"):
                with st.expander(f"Sources ({len(message[\'citations\'])} references)"):
                    for i, cite in enumerate(message["citations"]):
                        source = cite.get("source", "Unknown")
                        page = cite.get("page_number", "?")
                        similarity = cite.get("similarity", 0)
                        pct = round(float(similarity) * 100, 1)
                        if len(source) > 40:
                            source = "..." + source[-37:]
                        st.markdown(
                            f\'<div class="citation-card">\' 
                            f\'Source {i+1} | {source} | Page {page} | Relevance: {pct}%\'
                            f\'</div>\',
                            unsafe_allow_html=True
                        )

    st.markdown("---")

    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Ask a question",
                placeholder="What does this document say about...",
                label_visibility="collapsed"
            )
        with col2:
            submitted = st.form_submit_button("Ask", use_container_width=True)

    if submitted and user_input.strip():
        st.session_state.messages.append({
            "role": "user",
            "content": user_input.strip()
        })

        with st.spinner("Searching document and generating answer..."):
            try:
                result = ask(user_input.strip(), session_id=st.session_state.session_id)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "citations": result["citations"]
                })
            except Exception as e:
                error_msg = str(e).lower()
                if "rate limit" in error_msg or "429" in error_msg:
                    answer = "The AI is temporarily busy. Please wait 30 seconds and try again."
                else:
                    answer = f"An error occurred: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "citations": []
                })

        st.rerun()
'''

requirements = """langchain==0.3.25
langchain-community==0.3.24
langchain-groq==0.3.2
langsmith==0.2.3
pinecone==6.0.2
chromadb==0.5.23
pymupdf==1.25.5
python-docx==1.1.2
beautifulsoup4==4.13.4
requests==2.32.3
streamlit==1.45.1
python-multipart==0.0.20
python-dotenv==1.1.0
pytest==8.3.5
"""

files = {
    "backend/core/embeddings/pinecone_store.py": pinecone_store,
    "backend/core/rag/rag_chain.py": rag_chain,
    "streamlit_app.py": streamlit_app,
    "requirements.txt": requirements,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {path}")

print("\nAll files written successfully")
