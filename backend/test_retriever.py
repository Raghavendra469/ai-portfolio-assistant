from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma(
    persist_directory="vector_db",
    embedding_function=embedding_model
)

query = "What certifications does Raghavendra have?"

results = db.similarity_search_with_score(
    query,
    k=5
)

for doc, score in results:
    print("\nSCORE:", score)
    print(doc.page_content[:300])
    print("=" * 50)