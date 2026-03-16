import os

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from dotenv import load_dotenv
from retriever import load_vector_store, get_retriever

load_dotenv()


def get_groq_key():
    key = os.getenv("GROQ_API_KEY")
    if not key and STREAMLIT_AVAILABLE:
        try:
            key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
    if not key:
        raise ValueError("GROQ_API_KEY not found.")
    return key


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain():
    vectorstore = load_vector_store()
    retriever = get_retriever(vectorstore, k=5)

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=2048,
        groq_api_key=get_groq_key()
    )

    prompt = PromptTemplate(
        input_variables=["context", "question", "chat_history"],
        template="""You are an expert knowledge assistant. Answer questions
accurately based ONLY on the provided context.

RULES:
1. Only use information from the CONTEXT below.
2. If the answer is not in the context say:
   "I couldn't find this information in the uploaded documents."
3. Never make up facts or use outside knowledge.
4. Be detailed and structured in your answers.
5. Use bullet points when listing multiple items.

CONVERSATION HISTORY:
{chat_history}

---
CONTEXT:
{context}
---

QUESTION: {question}

ANSWER:"""
    )

    # Store chat history as simple string
    chat_history_store = {"history": []}

    def get_chat_history_str():
        if not chat_history_store["history"]:
            return "No previous conversation."
        lines = []
        for h in chat_history_store["history"][-5:]:
            lines.append(f"Human: {h['question']}")
            lines.append(f"Assistant: {h['answer']}")
        return "\n".join(lines)

    def run_chain(inputs):
        question = inputs["question"]
        docs = retriever.invoke(question)
        context = format_docs(docs)
        chat_history = get_chat_history_str()

        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({
            "context": context,
            "question": question,
            "chat_history": chat_history
        })

        # Save to history
        chat_history_store["history"].append({
            "question": question,
            "answer": answer
        })

        return {
            "answer": answer,
            "source_documents": docs
        }

    return run_chain