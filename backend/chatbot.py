# chatbot.py

from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory

from bm25_retriever import bm25_search
from reranker import rerank_documents
import os

load_dotenv()

# Memory

chat_history = ChatMessageHistory()

# Embeddings

embedding_model = HuggingFaceEmbeddings(
model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Vector DB

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "vector_db"
)

db = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embedding_model
)

# LLM

llm = ChatGroq(
model="llama-3.3-70b-versatile",
temperature=0
)

def detect_category(query):

    query = query.lower()

    profile_keywords = [
        "who is",
        "about raghavendra",
        "introduce",
        "tell me about raghavendra",
        "background",
        "summary"
    ]

    contact_keywords = [
        "contact",
        "phone",
        "linkedin",
        "github",
        "reach",
        "connect"
    ]

    if any(
        keyword in query
        for keyword in profile_keywords
    ):
        return "profile"

    if any(
        keyword in query
        for keyword in contact_keywords
    ):
        return "contact"

    if "current project" in query:
        return "current_projects"

    if "project" in query:
        return "project"

    if "achievement" in query:
        return "achievement"

    if "certification" in query:
        return "certification"

    if "skill" in query:
        return "skill"

    if "experience" in query:
        return "experience"

    return None
    
def merge_documents(vector_docs, bm25_docs):

    seen = set()
    merged_docs = []

    for doc in vector_docs + bm25_docs:

        # Use source + content as unique identifier
        doc_id = (
            doc.metadata.get("source", "")
            + doc.page_content
        )

        if doc_id not in seen:

            seen.add(doc_id)
            merged_docs.append(doc)

    return merged_docs


def ask_raghav_ai(query: str):

    # -----------------------------
    # STEP 1 - Build Conversation History
    # -----------------------------

    history_text = "\n".join(
        [
            f"{msg.type}: {msg.content}"
            for msg in chat_history.messages
        ]
    )

    # -----------------------------
    # STEP 2 - Rewrite Query
    # -----------------------------

    rewrite_prompt = f"""
    You are a query rewriting assistant.

    Conversation History:
    {history_text}

    Current User Question:
    {query}

    Instructions:

    - Rewrite the question as a standalone question.
    - Resolve references like:
    - them
    - that project
    - that certification
    - tell me more
    - Use conversation history when needed.
    - Keep the rewritten question concise.

    Only return the rewritten question.
    """

    rewritten_query = llm.invoke(
        rewrite_prompt
    ).content

    print("\nOriginal Query:")
    print(query)

    print("\nRewritten Query:")
    print(rewritten_query)

    # -----------------------------
    # STEP 3 - Retrieval
    # -----------------------------

    retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 8,
            "fetch_k": 20
        }
    )

    category = detect_category(
        rewritten_query
    )

    # ------------------------
    # PROFILE
    # ------------------------

    if category == "profile":

        docs = db.similarity_search(
            rewritten_query,
            k=6,
            filter={
                "type": "profile"
            }
        )

    # ------------------------
    # CURRENT PROJECTS
    # ------------------------

    elif category == "current_projects":

        docs = db.similarity_search(
            rewritten_query,
            k=10,
            filter={
                "type": "project"
            }
        )
       
    # ------------------------
    # PROJECTS
    # ------------------------

    elif category == "project":

        vector_docs = db.similarity_search(
            rewritten_query,
            k=10,
            filter={
                "type": "project"
            }
        )

        bm25_docs = bm25_search(
            rewritten_query,
            k=10,
            category="project"
        )

        docs = merge_documents(
            vector_docs,
            bm25_docs
        )

    # ------------------------
    # CONTACT
    # ------------------------

    elif category == "contact":

        docs = db.similarity_search(
            rewritten_query,
            k=3,
            filter={
                "type": "contact"
            }
        )

    # ------------------------
    # OTHER CATEGORIES
    # ------------------------

    elif category:

        vector_docs = db.similarity_search(
            rewritten_query,
            k=5,
            filter={
                "type": category
            }
        )

        bm25_docs = bm25_search(
            rewritten_query,
            k=5,
            category=category
        )

        docs = merge_documents(
            vector_docs,
            bm25_docs
        )

        docs = rerank_documents(
            rewritten_query,
            docs,
            top_k=5
        )

    # ------------------------
    # GENERAL SEARCH
    # ------------------------

    else:

        vector_docs = retriever.invoke(
            rewritten_query
        )

        bm25_docs = bm25_search(
            rewritten_query,
            k=5
        )

        docs = merge_documents(
            vector_docs,
            bm25_docs
        )

        docs = rerank_documents(
            rewritten_query,
            docs,
            top_k=5
        )
    
    print("\nRETRIEVED DOCUMENTS:\n")

    for doc in docs:
        print(
            doc.metadata.get("source")
        )

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    # -----------------------------
    # STEP 4 - Final Prompt
    # -----------------------------

    prompt = f"""
    You are Raghav AI.

    You answer questions about Raghavendra Kodavalla.

    Rules:

    - Use only the provided context.
    - Never hallucinate information.
    - If information is missing say:
    "I don't have enough information to answer that."
    - Keep answers concise.
    - Use bullets where appropriate.
    - For profile questions provide a short professional introduction.
    - For project questions explain each project separately.
    - Research papers are NOT projects.
    - Certifications are NOT projects.
    - Achievements are NOT projects.
    - Internships are NOT projects.
    * If asked about total work experience, calculate it using all employment and internship durations available in the context.
    * Include internships when calculating total professional experience.
    * If a role is marked "Present", calculate duration up to the current date.
    * Show the calculation before giving the final total.

    Context:
    {context}

    Question:
    {query}

    Answer:
    """
    try:

        response = llm.invoke(prompt)

        # Save memory
        chat_history.add_user_message(query)
        chat_history.add_ai_message(response.content)

        sources = list(
            set(
                [
                    doc.metadata.get("source")
                    for doc in docs
                ]
            )
        )

        return {
            "answer": response.content,
            "sources": sources
        }

    except Exception as e:

        return {
            "answer": f"Error: {str(e)}",
            "sources": []
        }

def clear_memory():
    chat_history.clear()
