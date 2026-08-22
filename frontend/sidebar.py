import streamlit as st
import requests

from frontend.config import API_BASE_URL`nAPI_BASE = API_BASE_URL


def render_sidebar():
    """
    Render the left sidebar with document upload controls.
    """
    with st.sidebar:
        st.markdown("## Document Brain")
        st.markdown("*Ask questions about any document*")
        st.markdown("---")

        st.markdown('<div class="upload-header">Load a Document</div>', unsafe_allow_html=True)

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
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        try:
                            r = requests.post(f"{API_BASE}/upload/file", files=files)
                            if r.status_code == 200:
                                data = r.json()
                                st.session_state.document_loaded = True
                                st.session_state.document_name = uploaded_file.name
                                st.session_state.chunks_count = data["chunks_stored"]
                                st.session_state.messages = []
                                st.success(f"Loaded: {uploaded_file.name}")
                                st.rerun()
                            else:
                                st.error(f"Error: {r.json().get('detail', 'Upload failed')}")
                        except Exception as e:
                            st.error(f"Could not connect to API: {str(e)}")

        else:
            url_input = st.text_input("Enter URL", placeholder="https://example.com/article")

            if st.button("Load URL"):
                if url_input.strip():
                    with st.spinner("Fetching and indexing URL..."):
                        try:
                            r = requests.post(f"{API_BASE}/upload/url", json={"url": url_input.strip()})
                            if r.status_code == 200:
                                data = r.json()
                                st.session_state.document_loaded = True
                                st.session_state.document_name = url_input.strip()[:40] + "..."
                                st.session_state.chunks_count = data["chunks_stored"]
                                st.session_state.messages = []
                                st.success("URL loaded successfully")
                                st.rerun()
                            else:
                                st.error(f"Error: {r.json().get('detail', 'Failed')}")
                        except Exception as e:
                            st.error(f"Could not connect to API: {str(e)}")
                else:
                    st.warning("Please enter a URL")

        st.markdown("---")

        if st.session_state.get("document_loaded"):
            st.markdown(
                f'<div class="status-ready">Ready - {st.session_state.get("chunks_count", 0)} chunks</div>',
                unsafe_allow_html=True
            )
            st.markdown(f"**Document:** {st.session_state.get('document_name', '')[:35]}")

            if st.button("Clear & Load New"):
                try:
                    requests.post(f"{API_BASE}/session/clear")
                except:
                    pass
                st.session_state.document_loaded = False
                st.session_state.document_name = ""
                st.session_state.messages = []
                st.rerun()
        else:
            st.markdown(
                '<div class="status-empty">No document loaded</div>',
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.markdown("**Built by**")
        st.markdown("Akinde Olugbenga Tope")
        st.markdown("*IBM AI Engineering | GenAI | RAG*")


