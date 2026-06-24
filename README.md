# AI Portfolio Assistant – AI-Assisted Development Journey

## Overview

This document describes how I designed, developed, debugged, and improved an AI Portfolio Assistant using AI coding assistants and Large Language Models. The goal of the project was to build a conversational AI system capable of answering questions about my experience, projects, certifications, achievements, skills, and career journey.

The project was developed using an iterative AI-assisted workflow involving architecture planning, code generation, debugging, retrieval optimization, memory implementation, hybrid search, reranking, frontend integration, and deployment experimentation.

---

# Project Goal

Traditional resumes provide static information. Recruiters often need to manually read through multiple sections to understand a candidate's experience.

The goal was to build an AI assistant that allows recruiters to ask natural language questions such as:

* Who is Raghavendra?
* What projects has he worked on?
* Describe those projects.
* What certifications does he have?
* What is his work experience?
* What are his achievements?
* How can I contact him?

and receive accurate responses generated from a personal knowledge base.

---

# Initial Architecture

The first version of the project followed a basic Retrieval-Augmented Generation (RAG) architecture.

Knowledge Base (.txt Files)
↓
Document Loader
↓
Text Chunking
↓
Embeddings
↓
Chroma Vector Database
↓
Similarity Search
↓
LLM
↓
Response

Technologies:

* Python
* FastAPI
* LangChain
* ChromaDB
* HuggingFace Embeddings
* Groq Llama 3.3 70B
* React
* Vite

---

# Knowledge Base Design

I structured my information into multiple files:

* about-me.txt
* skills.txt
* experience.txt
* certifications.txt
* achievements.txt
* contact-info.txt
* project_ai_portfolio_assistant.txt
* project_ai_email_agent.txt
* project_royalty_management_system.txt
* project_qr_generator.txt

This separation helped retrieval quality and allowed category-based filtering.

---

# Challenges Encountered

## Problem 1: Projects Were Not Retrieved Correctly

Initial behavior:

Question:

"What projects has he worked on?"

The system sometimes returned:

* Certifications
* Achievements
* Research Publications

instead of actual projects.

### Solution

I introduced metadata tagging during ingestion:

* project
* certification
* achievement
* experience
* education
* skill

This enabled category-aware retrieval.

---

## Problem 2: Follow-Up Questions Failed

Example:

User:
"What projects has he worked on?"

Assistant:
"AI Email Agent, AI Portfolio Assistant..."

User:
"Describe them"

The assistant lost context and returned unrelated information.

### Solution

Implemented conversational memory using:

ChatMessageHistory

Added query rewriting using conversation history.

Example:

Original Query:
"Describe them"

Rewritten Query:
"What are the details of AI Email Agent, AI Portfolio Assistant, Royalty Management System, and Smart QR Code Generator?"

This significantly improved multi-turn conversations.

---

## Problem 3: Missing Project Details

Even after memory implementation, retrieval occasionally returned incomplete project information.

### Solution

Implemented Hybrid Search:

Vector Search (Chroma)
+
Keyword Search (BM25)

Benefits:

* Semantic understanding
* Exact keyword matching
* Better recall

---

# Hybrid Search Implementation

I implemented BM25 retrieval alongside ChromaDB.

Workflow:

User Query
↓
Chroma Retrieval
+
BM25 Retrieval
↓
Merge Results
↓
Deduplicate
↓
Context Generation

This improved retrieval for:

* Awards
* Certifications
* Exact project names
* Contact information

---

# Query Rewriting

To handle conversational context, I added a query rewriting stage.

Example:

Conversation:

User:
"What projects has he worked on?"

Assistant:
[List of projects]

User:
"Describe them"

Query Rewriter Output:

"What are the details of AI Email Automation Agent, AI Portfolio Assistant, Royalty Management System, and Smart QR Code Generator?"

This enabled context-aware retrieval.

---

# Reranking

After implementing Hybrid Search, I experimented with CrossEncoder-based reranking.

Workflow:

Query
↓
Hybrid Search
↓
Candidate Documents
↓
CrossEncoder Reranker
↓
Top Documents

Goal:

Improve relevance by reordering retrieved documents based on query-document similarity.

---

# Frontend Development

Built a React-based chat interface featuring:

* Chat history
* User messages
* Assistant messages
* Auto scrolling
* Loading indicators
* Source display

The frontend communicates with FastAPI APIs.

---

# Debugging Examples

Throughout development I encountered multiple issues:

### Environment Variables

Problem:

GOOGLE_API_KEY returned None.

Resolution:

Debugged dotenv loading and environment configuration.

---

### LangChain Version Changes

Problem:

Module import failures.

Example:

ModuleNotFoundError

Resolution:

Updated imports and migrated to newer package structures.

---

### Retrieval Quality Issues

Problem:

Projects, achievements, and certifications were mixed together.

Resolution:

Implemented metadata-based filtering and retrieval strategies.

---

### Frontend Integration

Problem:

Backend responses were received in browser network logs but not displayed in UI.

Resolution:

Debugged React state management and response handling.

---

### Deployment Challenges

Attempted deployment using:

* Render
* AWS EC2

Challenges included:

* Memory limitations
* Dependency installation issues
* Package compatibility
* Infrastructure configuration

These experiences helped me better understand production deployment considerations for AI systems.

---

# Key Learnings

This project helped me gain hands-on experience with:

* Retrieval-Augmented Generation (RAG)
* LangChain
* FastAPI
* Vector Databases
* ChromaDB
* Hybrid Search
* BM25
* Query Rewriting
* Conversational Memory
* Reranking
* Prompt Engineering
* Frontend Integration
* AI-Assisted Development Workflows
* Deployment Troubleshooting

---

# Future Improvements

Planned enhancements include:

* LangGraph workflows
* Multi-agent architecture
* RAG evaluation pipelines
* Advanced reranking
* Cloud vector databases
* Production monitoring
* Authentication and user sessions

---

# Conclusion

This project demonstrates my ability to use AI tools not only for code generation but also for architecture design, debugging, iterative problem solving, retrieval optimization, and full-stack AI application development.

The most valuable aspect of the project was learning how to collaborate effectively with AI systems while maintaining engineering judgment and systematically improving the application through experimentation and debugging.
