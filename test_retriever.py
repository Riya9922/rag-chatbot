import sys
import traceback

try:
    from src.phase_3_retrieval.retriever import MFRetriever
    print("MFRetriever imported successfully.")
    
    retriever = MFRetriever()
    print("MFRetriever initialized successfully.")
    
    facts = retriever.retrieve("What is the NAV of HDFC Mid Cap?")
    print("Retrieved facts:", facts)
except Exception as e:
    print("Error occurred:")
    traceback.print_exc()
