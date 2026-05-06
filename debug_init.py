import sys
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("Starting import trace...")

import os
print("Imported os")

from dotenv import load_dotenv
print("Imported load_dotenv")
load_dotenv()
print("Loaded dotenv")

print("Checking OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

try:
    print("Importing FastAPI...")
    from fastapi import FastAPI
    print("Imported FastAPI")

    print("Importing MFRetriever...")
    from src.phase_3_retrieval.retriever import MFRetriever
    print("Imported MFRetriever")

    print("Initializing MFRetriever...")
    retriever = MFRetriever()
    print("Initialized MFRetriever")

    print("Importing OpenAI...")
    from openai import OpenAI
    print("Imported OpenAI")

    print("Initializing OpenAI client...")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("Initialized OpenAI client")

    print("All initializations succeeded!")
except Exception as e:
    import traceback
    print("Exception occurred:")
    traceback.print_exc()

print("Trace complete.")
