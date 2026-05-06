import re

# Keywords and patterns that indicate advisory or opinion-based queries
ADVISORY_PATTERNS = [
    r"\bshould\s+i\s+invest\b",
    r"\bwhich\s+is\s+better\b",
    r"\bbest\s+fund\b",
    r"\bworth\s+buying\b",
    r"\brecommend\b",
    r"\badvice\b",
    r"\bpredict\b",
    r"\bfuture\s+returns\b",
    r"\bcompare\s+performance\b"
]

def check_for_advice(user_query):
    """
    Returns True if the query is seeking investment advice or opinions.
    """
    query_lower = user_query.lower()
    for pattern in ADVISORY_PATTERNS:
        if re.search(pattern, query_lower):
            return True
    return False

def get_refusal_message():
    """
    Standardised refusal response for non-factual queries.
    """
    return (
        "I am a factual Mutual Fund assistant and I strictly avoid providing investment advice, "
        "opinions, or recommendations. My purpose is to provide objective data from official sources.\n\n"
        "For investment guidance, please refer to official educational resources:\n"
        "- AMFI: https://www.amfiindia.com/\n"
        "- SEBI: https://www.sebi.gov.in/"
    )

def get_disclaimer():
    """
    Mandatory footer disclaimer.
    """
    return "Facts-only. No investment advice."
