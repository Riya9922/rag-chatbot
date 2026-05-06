import re

ADVISORY_KEYWORDS = [
    r"\bshould\b", r"\binvest\b", r"\bbuy\b", r"\bsell\b", r"\bbest\b", 
    r"\bbetter\b", r"\badvice\b", r"\brecommend\b", r"\bcomparison\b",
    r"\bpredict\b", r"\bfuture\b", r"\breturns\b"
]

def is_advisory_query(query):
    query_lower = query.lower()
    for pattern in ADVISORY_KEYWORDS:
        if re.search(pattern, query_lower):
            # Check if it's a factual query despite keywords
            # e.g., "What is the historical returns" vs "Should I invest for returns"
            if "what" in query_lower or "is" in query_lower or "detail" in query_lower:
                if any(x in query_lower for x in ["should", "best", "recommend"]):
                    return True
                return False # Allow factual return queries if framed as "what is"
            return True
    return False

def get_refusal_response():
    return (
        "I am sorry, but I can only provide factual information about mutual fund schemes. "
        "I cannot provide investment advice, opinions, or recommendations. "
        "For guidance, please refer to official educational resources from AMFI or SEBI: "
        "https://www.amfiindia.com/ or https://www.sebi.gov.in/"
    )
