import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from frontend.styles import CUSTOM_CSS
from frontend.sidebar import render_sidebar
from frontend.chat import render_chat

st.set_page_config(
    page_title="Document Brain",
    page_icon="brain",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_loaded" not in st.session_state:
    st.session_state.document_loaded = False
if "document_name" not in st.session_state:
    st.session_state.document_name = ""
if "chunks_count" not in st.session_state:
    st.session_state.chunks_count = 0

st.markdown("# Document Brain")
st.markdown("*Intelligent document Q&A with source citations*")

render_sidebar()
render_chat()
