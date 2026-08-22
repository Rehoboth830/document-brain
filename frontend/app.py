import streamlit as st

st.set_page_config(
    page_title="Document Brain",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Document Brain")
st.subheader("Ask questions about any document")
st.info("Upload a PDF, Word document, or paste a URL to get started.")
st.markdown("---")
st.caption("Built by Akinde Olugbenga Tope · Powered by LangChain + Groq + ChromaDB")
