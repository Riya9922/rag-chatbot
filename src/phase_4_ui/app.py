import streamlit as st
from src.phase_3_assistant.rag_engine import generate_answer
from src.phase_3_assistant.refusal_handler import get_disclaimer

# Page Configuration
st.set_page_config(
    page_title="MF FAQ Assistant | Facts-Only",
    page_icon="🛡️",
    layout="centered"
)

# Premium Styling
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stChatFloatingInputContainer { background-color: #ffffff; }
    .stChatMessage { border: 1px solid #e0e0e0; border-radius: 10px; margin-bottom: 10px; }
    .mf-footer { font-size: 0.85rem; color: #757575; border-top: 1px solid #eeeeee; padding-top: 20px; text-align: center; margin-top: 30px; }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🛡️ Mutual Fund FAQ Assistant")
st.caption("Factual, verifiable information from official AMC sources.")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for example questions and controls
with st.sidebar:
    st.image("https://groww.in/logo-groww.png", width=120) # Placeholder or local logo
    st.header("Help")
    st.info("I answer objective queries about HDFC Mutual Fund schemes using official factsheets.")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.subheader("Example Questions")
    examples = [
        "What is the exit load for HDFC Mid-Cap Fund?",
        "Minimum SIP amount for HDFC Focused Fund?",
        "What is the risk level of HDFC ELSS Tax Saver?",
        "Benchmark index for HDFC Large Cap Fund?"
    ]
    for ex in examples:
        if st.button(ex):
            st.session_state.user_query = ex

# Display Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
user_input = st.chat_input("Ask a question...")
if "user_query" in st.session_state:
    user_input = st.session_state.pop("user_query")

if user_input:
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Assistant Response (RAG)
    with st.spinner("Retrieving facts..."):
        result = generate_answer(user_input)
        
        answer = result["answer"]
        source = result["source"]
        date = result["date"]
        
        # Build formatted output
        if result["is_refusal"]:
            full_response = answer
        else:
            full_response = (
                f"{answer}\n\n"
                f"**Source:** {source}\n"
                f"*Last updated from sources: {date}*"
            )
        
    with st.chat_message("assistant"):
        st.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Global Disclaimer Footer
st.markdown(f"<div class='mf-footer'>{get_disclaimer()}</div>", unsafe_allow_html=True)
