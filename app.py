import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="RAG Knowledge Assistant",
    page_icon="🧠",
    layout="wide"
)

from ingestion import load_documents, chunk_documents
from retriever import build_vector_store, load_vector_store
from rag_pipeline import build_rag_chain

st.markdown("""
<style>
.source-box {
    background: #1e2130;
    border-left: 3px solid #00d4ff;
    padding: 12px;
    margin: 8px 0;
    border-radius: 6px;
    font-size: 0.82rem;
    color: #cccccc;
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chain" not in st.session_state:
    st.session_state.chain = None
if "index_built" not in st.session_state:
    st.session_state.index_built = False
if "doc_count" not in st.session_state:
    st.session_state.doc_count = 0
if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0

with st.sidebar:
    st.markdown("## 🗂️ Knowledge Base")
    st.markdown("---")

    uploaded_files = st.file_uploader(
        "Upload Documents",
        accept_multiple_files=True,
        type=["pdf", "txt"]
    )

    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected:**")
        for f in uploaded_files:
            st.markdown(f"• `{f.name}`")

    st.markdown("---")

    if st.button("⚡ Build Knowledge Index",
                 use_container_width=True,
                 type="primary"):
        if not uploaded_files:
            st.error("Please upload at least one file first.")
        else:
            progress = st.progress(0)
            status = st.empty()

            try:
                status.info("💾 Saving files...")
                progress.progress(10)
                os.makedirs("docs", exist_ok=True)

                for f in os.listdir("docs"):
                    os.remove(os.path.join("docs", f))

                for uf in uploaded_files:
                    uf.seek(0)
                    with open(os.path.join("docs", uf.name), "wb") as f:
                        f.write(uf.read())

                progress.progress(25)
                status.info("📖 Loading documents...")
                docs = load_documents("docs")

                if not docs:
                    st.error("Could not extract content. Try a different file.")
                    st.stop()

                progress.progress(45)
                status.info("✂️ Chunking documents...")
                chunks = chunk_documents(docs)

                progress.progress(65)
                status.info("🔢 Building embeddings (~30 seconds)...")
                build_vector_store(chunks)

                progress.progress(85)
                status.info("🤖 Starting AI chain...")
                st.session_state.chain = build_rag_chain()
                st.session_state.index_built = True
                st.session_state.doc_count = len(docs)
                st.session_state.chunk_count = len(chunks)
                st.session_state.messages = []

                progress.progress(100)
                status.success("✅ Ready!")
                st.success(f"""
                **Done!**
                - 📄 {len(docs)} page(s) loaded
                - ✂️ {len(chunks)} chunks indexed
                """)

            except Exception as e:
                status.empty()
                progress.empty()
                st.error(f"Error: {str(e)}")
                st.exception(e)

    if st.button("📂 Load Saved Index", use_container_width=True):
        try:
            with st.spinner("Loading..."):
                st.session_state.chain = build_rag_chain()
                st.session_state.index_built = True
            st.success("✅ Index loaded!")
        except FileNotFoundError:
            st.error("No saved index. Upload files and build index first.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        if st.session_state.index_built:
            try:
                st.session_state.chain = build_rag_chain()
            except Exception:
                pass
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Status")
    if st.session_state.index_built:
        st.success("🟢 Index Ready")
        st.markdown(f"- Pages: **{st.session_state.doc_count}**")
        st.markdown(f"- Chunks: **{st.session_state.chunk_count}**")
    else:
        st.warning("🟡 No Index Yet")

    st.markdown("---")
    st.caption("Model: LLaMA 3.3 70B (Groq)")
    st.caption("Embeddings: all-MiniLM-L6-v2")
    st.caption("Vector Store: FAISS + MMR")

st.markdown("# 🧠 RAG Knowledge Assistant")
st.markdown("Upload documents and ask questions — "
            "powered by LLaMA 3.3 70B + FAISS")

if not st.session_state.index_built:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 📤 Step 1\nUpload PDF or TXT files in the sidebar")
    with col2:
        st.info("### ⚡ Step 2\nClick Build Knowledge Index and wait")
    with col3:
        st.info("### 💬 Step 3\nAsk any question about your documents")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if (message["role"] == "assistant"
                and message.get("sources")):
            with st.expander(f"📄 {len(message['sources'])} Source(s)"):
                for i, s in enumerate(message["sources"]):
                    st.markdown(f"""
                    <div class="source-box">
                    <strong>Source {i+1}:</strong>
                    {os.path.basename(s['file'])} | Page: {s['page']}
                    <br><br>{s['preview']}
                    </div>
                    """, unsafe_allow_html=True)

if prompt := st.chat_input(
    "Ask a question about your documents...",
    disabled=not st.session_state.index_built
):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = st.session_state.chain({"question": prompt})
                answer = result["answer"]
                source_docs = result.get("source_documents", [])

                st.write(answer)

                sources = []
                seen = set()
                for doc in source_docs:
                    key = doc.page_content[:80]
                    if key in seen:
                        continue
                    seen.add(key)
                    sources.append({
                        "file": doc.metadata.get(
                            "source",
                            doc.metadata.get("filename", "Unknown")
                        ),
                        "page": doc.metadata.get("page", "N/A"),
                        "preview": doc.page_content[:300] + "..."
                    })

                if sources:
                    with st.expander(f"📄 {len(sources)} Source(s)"):
                        for i, s in enumerate(sources):
                            st.markdown(f"""
                            <div class="source-box">
                            <strong>Source {i+1}:</strong>
                            {os.path.basename(s['file'])} | Page: {s['page']}
                            <br><br>{s['preview']}
                            </div>
                            """, unsafe_allow_html=True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            except Exception as e:
                err = f"Error: {str(e)}"
                st.error(err)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": err,
                    "sources": []
                })