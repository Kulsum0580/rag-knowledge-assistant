# ingestion.py
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_documents(folder_path: str):
    """
    Loads all PDF and TXT files from the given folder.
    Returns a list of LangChain Document objects.
    """
    documents = []
    supported_extensions = [".pdf", ".txt"]

    if not os.path.exists(folder_path):
        print(f"❌ Folder '{folder_path}' does not exist.")
        return []

    files = os.listdir(folder_path)
    if not files:
        print(f"❌ No files found in '{folder_path}'.")
        return []

    for filename in files:
        file_path = os.path.join(folder_path, filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in supported_extensions:
            print(f"⚠️  Skipping unsupported file: {filename}")
            continue

        try:
            if ext == ".pdf":
                loader = PyPDFLoader(file_path)
            elif ext == ".txt":
                loader = TextLoader(file_path, encoding="utf-8")

            loaded_docs = loader.load()

            # Add filename to metadata for source tracking
            for doc in loaded_docs:
                doc.metadata["filename"] = filename

            documents.extend(loaded_docs)
            print(f"✅ Loaded: {filename} ({len(loaded_docs)} page(s))")

        except Exception as e:
            print(f"❌ Failed to load {filename}: {e}")

    print(f"\n📄 Total pages/sections loaded: {len(documents)}")
    return documents


def chunk_documents(documents):
    """
    Splits documents into overlapping chunks for better retrieval accuracy.
    """
    if not documents:
        print("❌ No documents to chunk.")
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )

    chunks = splitter.split_documents(documents)
    print(f"✂️  Total chunks created: {len(chunks)}")
    return chunks


if __name__ == "__main__":
    docs = load_documents("docs")
    if docs:
        chunks = chunk_documents(docs)
        print(f"\nFirst chunk preview:\n{chunks[0].page_content[:300]}")
    else:
        print("Add PDFs or TXT files to the /docs folder to test.")