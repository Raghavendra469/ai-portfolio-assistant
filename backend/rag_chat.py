from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Embedding Model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load ChromaDB
db = Chroma(
    persist_directory="vector_db",
    embedding_function=embedding_model
)

# Gemini LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

print("\n Raghav AI is Ready!")
print("Type 'exit' to quit.\n")

while True:

    query = input("Ask: ")

    if query.lower() == "exit":
        break

    # MMR Retriever
    retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 10,
            "fetch_k": 20
        }
    )

    docs = retriever.invoke(query)

    print("\n========== RETRIEVED CHUNKS ==========")

    for i, doc in enumerate(docs):

        print(f"\nChunk {i+1}")

        print(
            "SOURCE:",
            doc.metadata.get("source", "Unknown")
        )

        print(doc.page_content[:500])

        print("-" * 60)

    # Build Context
    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    # Prompt
    prompt = f"""
You are Raghav AI.

Answer questions about Raghavendra Kodavalla.

Rules:

1. Use only information from the context.
2. If information is not available, say:
   "I don't have enough information to answer that."
3. When asked about projects, only mention actual projects.
4. Do not classify certifications, achievements, education, or research papers as projects.
5. Provide concise but professional answers.

Context:
{context}

Question:
{query}

Answer:
"""

    response = llm.invoke(prompt)

    print("\n========== ANSWER ==========\n")

    print(response.content)

    print("\n============================\n")