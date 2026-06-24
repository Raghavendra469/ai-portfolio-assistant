from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

print("Loading documents...")

loader = DirectoryLoader(
    "knowledge_base",
    glob="*.txt"
)

documents = loader.load()

for doc in documents:

    source = doc.metadata["source"].lower()

    if "project_" in source:
        doc.metadata["type"] = "project"

    elif "achievement" in source:
        doc.metadata["type"] = "achievement"

    elif "certification" in source:
        doc.metadata["type"] = "certification"

    elif "skills" in source:
        doc.metadata["type"] = "skill"

    elif "contact-info" in source:
        doc.metadata["type"] = "contact"

    elif "about-me" in source:
        doc.metadata["type"] = "profile"

    elif "experience" in source:
        doc.metadata["type"] = "experience"

    elif "education" in source:
        doc.metadata["type"] = "education"

    elif "career_goals" in source:
        doc.metadata["type"] = "career"

    else:
        doc.metadata["type"] = "general"   

    print(f"Loaded {len(documents)} documents")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory="vector_db"
)

print("Vector Database Created Successfully")