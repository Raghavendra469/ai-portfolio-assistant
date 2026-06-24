from rank_bm25 import BM25Okapi
from langchain_community.document_loaders import DirectoryLoader

# ------------------------------------
# Load Documents Once
# ------------------------------------

loader = DirectoryLoader(
    "knowledge_base",
    glob="*.txt"
)

documents = loader.load()

# ------------------------------------
# Add Metadata Types
# ------------------------------------

for doc in documents:

    source = doc.metadata["source"].lower()

    if "project_" in source:
        doc.metadata["type"] = "project"

    elif "certification" in source:
        doc.metadata["type"] = "certification"

    elif "achievement" in source:
        doc.metadata["type"] = "achievement"

    elif "skill" in source:
        doc.metadata["type"] = "skill"

    elif "experience" in source:
        doc.metadata["type"] = "experience"

    elif "contact" in source:
        doc.metadata["type"] = "contact"

    elif "education" in source:
        doc.metadata["type"] = "education"

    else:
        doc.metadata["type"] = "general"


# ------------------------------------
# BM25 Search
# ------------------------------------

def bm25_search(
    query,
    k=5,
    category=None
):

    # ----------------------------
    # Category Filtering
    # ----------------------------

    filtered_documents = documents

    if category:

        filtered_documents = [

            doc

            for doc in documents

            if doc.metadata.get("type")
            == category

        ]

    if len(filtered_documents) == 0:
        return []

    # ----------------------------
    # Build BM25 Corpus
    # ----------------------------

    tokenized_docs = [

        doc.page_content.lower().split()

        for doc in filtered_documents

    ]

    bm25 = BM25Okapi(
        tokenized_docs
    )

    # ----------------------------
    # Tokenize Query
    # ----------------------------

    tokenized_query = (
        query.lower()
        .replace("?", "")
        .split()
    )

    # ----------------------------
    # BM25 Scores
    # ----------------------------

    scores = bm25.get_scores(
        tokenized_query
    )

    ranked = sorted(
        zip(filtered_documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    # ----------------------------
    # Remove Zero Scores
    # ----------------------------

    results = []

    for doc, score in ranked:

        if score <= 0:
            continue

        results.append(doc)

        if len(results) >= k:
            break

    return results


# ------------------------------------
# Debug Testing
# ------------------------------------

if __name__ == "__main__":

    test_queries = [

        "Silver Star Award",
        "AI-900",
        "Cisco DevNet",
        "Royalty Management",
        "WhatsApp QR",
        "Brain Tumor Detection"

    ]

    for query in test_queries:

        print("\n" + "=" * 50)
        print("QUERY:", query)

        docs = bm25_search(
            query,
            k=3
        )

        for doc in docs:

            print(
                doc.metadata["source"]
            )