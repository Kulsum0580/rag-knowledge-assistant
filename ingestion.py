import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_documents(folder_path: str):
    documents = []

    if not os.path.exists(folder_path):
        return []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in [".pdf", ".txt"]:
            continue

        try:
            if ext == ".pdf":
                loader = PyPDFLoader(file_path)
            else:
                loader = TextLoader(file_path, encoding="utf-8")

            loaded = loader.load()
            for doc in loaded:
                doc.metadata["filename"] = filename
            documents.extend(loaded)

        except Exception as e:
            print(f"Error loading {filename}: {e}")

    return documents


def chunk_documents(documents):
    if not documents:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    return splitter.split_documents(documents)