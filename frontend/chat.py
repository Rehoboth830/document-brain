import streamlit as st
import requests

API_BASE = "http://localhost:8000/api/v1"


def render_citations(citations: list):
    """
    Render citation cards below an answer.
    """
    if not citations:
        return

    with st.expander(f"Sources ({len(citations)} references)", expanded=False):
        for i, cite in enumerate(citations):
            source = cite.get("source", "Unknown")
            page = cite.get("page_number", "?")
            similarity = cite.get("similarity", 0)
            pct = round(similarity * 100, 1)

            if len(source) > 40:
                source = "..." + source[-37:]

            st.markdown(
                f'<div class="citation-card">'
                f'<span class="citation-badge">Source {i+1}</span> '
                f'{source} &nbsp;|&nbsp; Page {page} &nbsp;|&nbsp; '
                f'Relevance: {pct}%'
                f'</div>',
                unsafe_allow_html=True
            )


def render_chat():
    """
    Render the main chat interface.
    """
    if not st.session_state.get("document_loaded"):
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Get Started")
            st.markdown("Upload a **PDF**, **Word document**, or paste a **URL** in the sidebar to begin.")
            st.markdown("")
            st.markdown("**What you can do:**")
            st.markdown("- Ask questions in plain English")
            st.markdown("- Get answers with exact page citations")
            st.markdown("- Load multiple document types")
            st.markdown("- Query across the entire document")
        return

    for message in st.session_state.get("messages", []):
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
                render_citations(message["citations"])

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
                r = requests.post(
                    f"{API_BASE}/query",
                    json={"question": user_input.strip(), "n_results": 5}
                )

                if r.status_code == 200:
                    data = r.json()
                    answer = data["answer"]
                    citations = data["citations"]

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "citations": citations
                    })
                else:
                    error = r.json().get("detail", "Query failed")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error: {error}",
                        "citations": []
                    })
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Could not connect to API. Is the server running?",
                    "citations": []
                })

        st.rerun()
