import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from backend.core.rag.rag_chain import load_document, ask
from backend.core.embeddings.vector_store import get_store_count, clear_store

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
        padding: 12px 16px;
        margin: 8px 0;
        color: #e2e8f0;
        font-size: 14px;
        line-height: 1.6;
    }
    .assistant-message {
        background: linear-gradient(135deg, #1a2332, #243447);
        border-radius: 12px 12px 12px 4px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #e2e8f0;
        font-size: 14px;
        line-height: 1.6;
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

with st.sidebar:
    st.markdown("## Document Brain")
    st.markdown("*Ask questions about any document*")
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
            if st.button("Load Document"):
                with st.spinner("Reading and indexing document..."):
                    try:
                        temp_path = f"data/uploads/{uploaded_file.name}"
                        os.makedirs("data/uploads", exist_ok=True)
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getvalue())
                        chunks_stored = load_document(temp_path)
                        st.session_state.document_loaded = True
                        st.session_state.document_name = uploaded_file.name
                        st.session_state.chunks_count = chunks_stored
                        st.session_state.messages = []
                        st.success(f"Loaded: {uploaded_file.name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to load document: {str(e)}")

    else:
        url_input = st.text_input("Enter URL", placeholder="https://example.com/article")
        if st.button("Load URL"):
            if url_input.strip():
                with st.spinner("Fetching and indexing URL..."):
                    try:
                        chunks_stored = load_document(url_input.strip())
                        st.session_state.document_loaded = True
                        st.session_state.document_name = url_input[:40] + "..."
                        st.session_state.chunks_count = chunks_stored
                        st.session_state.messages = []
                        st.success("URL loaded successfully")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to load URL: {str(e)}")
            else:
                st.warning("Please enter a URL")

    st.markdown("---")

    if st.session_state.document_loaded:
        st.success(f"Ready - {st.session_state.chunks_count} chunks")
        st.markdown(f"**{st.session_state.document_name[:35]}**")
        if st.button("Clear & Load New"):
            clear_store()
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
st.markdown("*Intelligent document Q&A with source citations*")

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
        st.markdown("- Load any document type")
else:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f'<div class="user-message">{message["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="assistant-message">{message["content"]}</div>',
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
            submitted = st.form_submit_button("Ask")

    if submitted and user_input.strip():
        st.session_state.messages.append({
            "role": "user",
            "content": user_input.strip()
        })

        with st.spinner("Thinking..."):
            try:
                result = ask(user_input.strip())
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "citations": result["citations"]
                })
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {str(e)}",
                    "citations": []
                })

        st.rerun()
