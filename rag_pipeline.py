# rag_pipeline.py
import os

# Handle import of streamlit safely
# (needed for Streamlit Cloud secrets)
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from retriever import load_vector_store, get_retriever

load_dotenv()


# -------------------------------------------------------
# API KEY LOADER
# Works in THREE places:
# 1. Local development (.env file)
# 2. Streamlit Cloud (secrets.toml)
# 3. Environment variable set directly on server
# -------------------------------------------------------
def get_groq_key():
    # First try .env file (local development)
    key = os.getenv("GROQ_API_KEY")

    # Second try Streamlit secrets (Streamlit Cloud deployment)
    if not key and STREAMLIT_AVAILABLE:
        try:
            key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass

    # If still not found, raise clear error
    if not key:
        raise ValueError(
            "❌ GROQ_API_KEY not found.\n"
            "Local: Add GROQ_API_KEY=your_key to your .env file\n"
            "Streamlit Cloud: Add GROQ_API_KEY in App Settings > Secrets"
        )

    return key


# -------------------------------------------------------
# ANSWER GENERATION PROMPT
# Controls exactly how the LLM answers questions.
# Strict rules = higher accuracy.
# -------------------------------------------------------
QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are an expert knowledge assistant with access to a 
specific knowledge base. Your job is to give accurate, complete, and 
helpful answers strictly based on the provided context.

STRICT RULES YOU MUST FOLLOW:
1. ONLY use information from the CONTEXT section below.
2. If the answer cannot be found in the context, respond with:
   "I couldn't find specific information about this in the uploaded 
   documents. Please try rephrasing or ask about a different topic."
3. NEVER invent facts, guess, or use outside knowledge.
4. Structure your answer clearly with bullet points or numbered lists 
   when listing multiple items.
5. Be thorough — do not give a one-line answer if more detail 
   is available in the context.
6. If the question is a follow-up to previous conversation, 
   use the context to answer it fully.
7. Always be professional, clear and easy to understand.

---
CONTEXT FROM KNOWLEDGE BASE:
{context}
---

QUESTION: {question}

DETAILED ANSWER:"""
)


# -------------------------------------------------------
# QUESTION CONDENSING PROMPT
# Rephrases follow-up questions into full standalone
# questions so the retriever finds the right chunks.
# -------------------------------------------------------
CONDENSE_PROMPT = ChatPromptTemplate.from_template("""
You are a helpful assistant. Given a conversation history and a 
follow-up question, rephrase the follow-up question into a clear, 
complete standalone question that includes all necessary context 
from the conversation history.

IMPORTANT RULES:
1. Return ONLY the rephrased standalone question.
2. Do not add any explanation, preamble or extra text.
3. Keep the rephrased question concise and specific.
4. If the follow-up question is already standalone and clear, 
   return it exactly as is.

Conversation History:
{chat_history}

Follow-up Question: {question}

Standalone Question:""")


# -------------------------------------------------------
# BUILD RAG CHAIN
# Combines: retriever + memory + LLM into full pipeline
# -------------------------------------------------------
def build_rag_chain():
    """
    Builds the complete RAG chain.

    Flow:
    User question
        → Condense with chat history into standalone question
        → Retrieve top-5 relevant chunks from FAISS
        → Feed chunks + question into LLM with strict prompt
        → Return answer + source documents
    """

    # Load saved FAISS vector store from disk
    vectorstore = load_vector_store()

    # Get MMR retriever — returns diverse, relevant chunks
    retriever = get_retriever(vectorstore, k=5)

    # Load Groq API key (works locally + Streamlit Cloud)
    groq_key = get_groq_key()

    # LLaMA 3.3 70B on Groq — free, fast, high accuracy
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,        # 0 = most factual and consistent
        max_tokens=2048,
        groq_api_key=groq_key
    )

    # Memory: remembers last 5 exchanges for follow-up questions
    memory = ConversationBufferWindowMemory(
        k=5,
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    # Assemble the full conversational RAG chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        condense_question_prompt=CONDENSE_PROMPT,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        return_source_documents=True,   # Returns which chunks were used
        verbose=False
    )

    print("✅ RAG chain ready.")
    return chain


# -------------------------------------------------------
# STANDALONE TEST
# Run: python rag_pipeline.py
# (Only works after building FAISS index first)
# -------------------------------------------------------
if __name__ == "__main__":
    print("Testing RAG pipeline...\n")

    try:
        chain = build_rag_chain()

        # Test questions — change these to match your documents
        test_questions = [
            "What is this document about?",
            "What are the main topics covered?",
            "Summarize the key points."
        ]

        for question in test_questions:
            print(f"❓ Question: {question}")
            result = chain.invoke({"question": question})
            print(f"💬 Answer: {result['answer']}")
            print(f"📄 Sources used: {len(result['source_documents'])}")
            print("-" * 60)

    except FileNotFoundError as e:
        print(f"\n{e}")
        print("👉 First run: python retriever.py to build the index.")

    except ValueError as e:
        print(f"\n{e}")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")