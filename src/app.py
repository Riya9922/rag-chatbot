import streamlit as st
import os
from dotenv import load_dotenv
from src.vector_store import get_vector_store
from src.refusal_handler import is_advisory_query, get_refusal_response
import openai

load_dotenv()

# Page Config
st.set_page_config(page_title="MF FAQ Assistant", layout="centered")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stChatMessage { border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    .stFooter { font-size: 0.8rem; color: #6c757d; text-align: center; margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("🛡️ Mutual Fund FAQ Assistant")
st.subheader("Facts‑Only. No investment advice.")

# Sidebar - Multi-thread support (Simulated by resetting session)
with st.sidebar:
    st.info("This assistant provides factual information about HDFC Mutual Fund schemes.")
    if st.button("New Conversation"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Example Questions")
    if st.button("What is the expense ratio of HDFC Mid-Cap Fund?"):
        st.session_state.temp_query = "What is the expense ratio of HDFC Mid-Cap Fund?"
    if st.button("Minimum SIP for HDFC ELSS Tax Saver?"):
        st.session_state.temp_query = "Minimum SIP for HDFC ELSS Tax Saver?"
    if st.button("What is the exit load for HDFC Focused Fund?"):
        st.session_state.temp_query = "What is the exit load for HDFC Focused Fund?"

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handling User Input
query = st.chat_input("Ask a factual question about HDFC funds...")
if "temp_query" in st.session_state:
    query = st.session_state.pop("temp_query")

if query:
    # 1. Add user message to history
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # 2. Refusal Handling
    if is_advisory_query(query):
        response = get_refusal_response()
    else:
        # 3. RAG Retrieval
        try:
            collection = get_vector_store()
            results = collection.query(
                query_texts=[query],
                n_results=3
            )
            
            context = "\n".join(results['documents'][0])
            source_url = results['metadatas'][0][0]['url'] if results['metadatas'][0] else "Unknown"
            scraped_at = results['metadatas'][0][0]['scraped_at'] if results['metadatas'][0] else "N/A"
            
            # 4. LLM Generation
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            system_prompt = (
                "You are a factual Mutual Fund FAQ assistant. Answer ONLY based on the provided context. "
                "Limit your response to a maximum of 3 sentences. Do not provide advice or opinions."
            )
            
            prompt = f"Context:\n{context}\n\nQuestion: {query}"
            
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            
            raw_answer = completion.choices[0].message.content
            response = f"{raw_answer}\n\n**Source:** {source_url}\n\n*Last updated from sources: {scraped_at}*"
            
        except Exception as e:
            response = f"I encountered an error while retrieving data. Please try again later. (Error: {e})"

    # 5. Display and store response
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer Disclaimer
st.markdown("---")
st.markdown("<div class='stFooter'>Facts-only. No investment advice. Data retrieved from Groww.in.</div>", unsafe_allow_html=True)
