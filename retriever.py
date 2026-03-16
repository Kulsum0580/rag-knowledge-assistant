# retriever.py
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

FAISS_INDEX_PATH = "faiss_index"


def get_embeddings():
    """
    Returns HuggingFace embeddings model.
    all-MiniLM-L6-v2 is fast, free, and accurate for RAG tasks.
    """
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


def build_vector_store(chunks):
    """
    Converts chunks into vector embeddings and saves FAISS index to disk.
    """
    if not chunks:
        raise ValueError("❌ No chunks provided to build vector store.")

    print("🔄 Building vector store... please wait.")
    embeddings = get_embeddings()

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(FAISS_INDEX_PATH)

    print(f"✅ Vector store saved — {len(chunks)} chunks indexed.")
    return vectorstore


def load_vector_store():
    """
    Loads FAISS index from disk.
    """
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError(
            "❌ No FAISS index found. "
            "Please upload documents and click 'Build Knowledge Index' first."
        )

    embeddings = get_embeddings()

    vectorstore = FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    print("✅ Vector store loaded successfully.")
    return vectorstore


def get_retriever(vectorstore, k=5):
    """
    MMR retrieval gives diverse, high-quality results.
    k=5 chunks returned per query.
    fetch_k=20 candidates considered before MMR filtering.
    """
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": k,
            "fetch_k": 20,
            "lambda_mult": 0.65
        }
    )


if __name__ == "__main__":
    from ingestion import load_documents, chunk_documents

    print("Testing retriever pipeline...")
    docs = load_documents("docs")

    if not docs:
        print("Add PDFs to /docs folder to test.")
    else:
        chunks = chunk_documents(docs)
        vs = build_vector_store(chunks)
        retriever = get_retriever(vs)

        test_query = "What is this document about?"
        results = retriever.invoke(test_query)
        print(f"\n🔍 Query: '{test_query}'")
        print(f"📦 Retrieved {len(results)} chunks\n")
        for i, doc in enumerate(results):
            print(f"--- Chunk {i+1} ---")
            print(doc.page_content[:200])
            print()