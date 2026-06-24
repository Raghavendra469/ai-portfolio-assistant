from sentence_transformers import CrossEncoder

print("Loading Reranker...")

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

print("Reranker Loaded")


def rerank_documents(
    query,
    docs,
    top_k=5
):

    if not docs:
        return []

    pairs = [

        (
            query,
            doc.page_content
        )

        for doc in docs

    ]

    scores = reranker.predict(
        pairs
    )

    ranked = sorted(
        zip(docs, scores),
        key=lambda x: x[1],
        reverse=True
    )

    print("\nRERANKED RESULTS")

    for doc, score in ranked:

        print(
            f"{score:.4f}",
            doc.metadata.get(
                "source"
            )
        )

    return [

        doc

        for doc, score

        in ranked[:top_k]

    ]