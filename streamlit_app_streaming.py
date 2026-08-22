import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from backend.core.embeddings.pinecone_store import (
    store_chunks_pinecone,
    retrieve_chunks_pinecone,
    clear_namespace,
    generate_session_id
)
from backend.core.ingestion.ingestion import ingest_document
from backend.core.rag.llm import get_llm
from backend.core.rag.prompt import get_prompt
from backend.core.rag.rag_chain import (
    load_document,
    format_context,
    extract_citations,
    clean_answer,
    is_summary_request
)

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
    .streaming-box {
        background: linear-gradient(135deg, #1a2332, #243447);
        border-radius: 12px 12px 12px 4px;
        padding: 14px 18px;
        margin: 8px 0;
        color: #e2e8f0;
        font-size: 14px;
        line-height: 1.7;
        border-left: 3px solid #4a9eff;
        min-height: 50px;
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
        f'<div style="margin: 4px 0 12px">Session: '
        f'<span class="session-badge">{st.session_state.session_id}</span></div>',
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
        st.markdown("- Get streaming answers with exact page citations")
        st.markdown("- Your document persists across sessions via Pinecone")
        st.markdown("- Each user gets a private isolated session")
else:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f'<div class="user-message">{message["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            content = message["content"]
            is_rate_limit = "rate limit" in content.lower() or "temporarily busy" in content.lower()

            if is_rate_limit:
                st.markdown(
                    f'<div class="warning-box">{content}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="assistant-message">{content}</div>',
                    unsafe_allow_html=True
                )

            if message.get("citations"):
                with st.expander(f"Sources ({len(message['citations'])} references)"):
                    for i, cite in enumerate(message["citations"]):
                        source = cite.get("source", "Unknown")
                        page = cite.get("page_number", "?")
                        similarity = cite.get("similarity", 0)
                        pct = round(float(similarity) * 100, 1)
                        if len(source) > 40:
                            source = "..." + source[-37:]
                        st.markdown(
                            f'<div class="citation-card">'
                            f'Source {i+1} | {source} | Page {page} | Relevance: {pct}%'
                            f'</div>',
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
        question = user_input.strip()
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        st.markdown(
            f'<div class="user-message">{question}</div>',
            unsafe_allow_html=True
        )

        summary_mode = is_summary_request(question)
        n_results = 10 if summary_mode else 5
        threshold = 0.20 if summary_mode else 0.30

        with st.spinner("Searching document..."):
            try:
                chunks = retrieve_chunks_pinecone(
                    question,
                    namespace=st.session_state.session_id,
                    n_results=n_results
                )
            except Exception:
                chunks = []

        if not chunks:
            answer = "No document loaded. Please upload a document first."
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "citations": []
            })
            st.rerun()
        else:
            avg_similarity = sum(c["similarity"] for c in chunks) / len(chunks)

            if avg_similarity < threshold:
                answer = "I could not find relevant information about this in the provided document. Try rephrasing your question."
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "citations": []
                })
                st.rerun()
            else:
                context = format_context(chunks)
                citations = extract_citations(chunks)

                prompt = get_prompt()
                llm = get_llm()

                messages = prompt.format_messages(
                    context=context,
                    question=question
                )

                stream_placeholder = st.empty()
                full_response = ""

                try:
                    with st.spinner("Generating answer..."):
                        for chunk in llm.stream(messages):
                            token = chunk.content
                            full_response += token

                    final_answer = clean_answer(full_response)

                    stream_placeholder.markdown(
                        f'<div class="assistant-message">{final_answer}</div>',
                        unsafe_allow_html=True
                    )

                    if citations:
                        with st.expander(f"Sources ({len(citations)} references)"):
                            for i, cite in enumerate(citations):
                                source = cite.get("source", "Unknown")
                                page = cite.get("page_number", "?")
                                similarity = cite.get("similarity", 0)
                                pct = round(float(similarity) * 100, 1)
                                if len(source) > 40:
                                    source = "..." + source[-37:]
                                st.markdown(
                                    f'<div class="citation-card">'
                                    f'Source {i+1} | {source} | Page {page} | Relevance: {pct}%'
                                    f'</div>',
                                    unsafe_allow_html=True
                                )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_answer,
                        "citations": citations
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
