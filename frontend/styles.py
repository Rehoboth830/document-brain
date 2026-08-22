CUSTOM_CSS = """
<style>
    /* Main background */
    .stApp {
        background-color: #0f1117;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2d3748;
    }

    /* Chat message - user */
    .user-message {
        background: linear-gradient(135deg, #1e3a5f, #2d5986);
        border-radius: 12px 12px 4px 12px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #e2e8f0;
        font-size: 14px;
        line-height: 1.6;
    }

    /* Chat message - assistant */
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

    /* Citation card */
    .citation-card {
        background: #1e2535;
        border: 1px solid #2d3748;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 4px 0;
        font-size: 12px;
        color: #94a3b8;
    }

    /* Citation badge */
    .citation-badge {
        background: #1e3a5f;
        color: #4a9eff;
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 11px;
        font-weight: 600;
    }

    /* Upload area */
    .upload-header {
        color: #4a9eff;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    /* Status badge */
    .status-ready {
        background: #064e3b;
        color: #34d399;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 12px;
        font-weight: 500;
    }

    .status-empty {
        background: #1f2937;
        color: #9ca3af;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 12px;
        font-weight: 500;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Input box */
    .stTextInput > div > div > input {
        background-color: #1e2535;
        border: 1px solid #2d3748;
        color: #e2e8f0;
        border-radius: 8px;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #1e3a5f, #2d5986);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #2d5986, #3d6fa6);
        border: none;
    }

    /* Divider */
    hr {
        border-color: #2d3748;
    }
</style>
"""
