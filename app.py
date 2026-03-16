# app.py
# Run with: streamlit run app.py

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# ---- PAGE CONFIG (must be first Streamlit call) ----
st.set_page_config(
    page_title="RAG Knowledge Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- IMPORTS ----
from ingestion import load_documents, chunk_documents
from retriever import build_vector_store, load_vector_store
from rag_pipeline import build_rag_chain

# ---- STYLING ----
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f1117;
    }

    /* Header */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        color: #aaaaaa;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Source boxes */
    .source-box {
        background: #1e2130;
        border-left: 3px solid #00d4ff;
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 6px;
        font-size: 0.82rem;
        color: #cccccc;
        line-height: 1.5;
    }

    .source-box strong {
        color: #00d4ff;
    }

    /* Status badges */
    .badge-ready {
        background: #1a3a2a;
        color: #4caf50;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .badge-not-ready {
        background: #3a2a1a;
        color: #ff9800;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* Chat input */
    .stChatInput input {
        background-color: #1e2130 !important;
        color: white !important;
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: #161b27;
    }

    /* Divider */
    hr {
        border-color: #2a2f45;
    }
</style>
""", unsafe_allow_html=True)


# ---- SESSION STATE INIT ----
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


# ---- SIDEBAR ----
with st.sidebar:
    st.markdown("## 🗂️ Knowledge Base")
    st.markdown("---")

    # File uploader
    uploaded_files = st.file_uploader(
        "Upload Documents",
        accept_multiple_files=True,
        type=["pdf", "txt"],
        help="Upload PDF or TXT files to build your knowledge base"
    )

    if uploaded_files:
        st.markdown(f"**📎 {len(uploaded_files)} file(s) ready:**")
        for f in uploaded_files:
            size_kb = round(len(f.getvalue()) / 1024, 1)
            st.markdown(f"• `{f.name}` ({size_kb} KB)")

    st.markdown("---")

    # Build Index Button
    build_clicked = st.button(
        "⚡ Build Knowledge Index",
        use_container_width=True,
        type="primary"
    )

    if build_clicked:
        if not uploaded_files:
            st.error("⚠️ Please upload at least one PDF or TXT file first.")
        else:
            progress_bar = st.progress(0)
            status = st.empty()

            try:
                # Step 1: Save files
                status.info("💾 Saving uploaded files...")
                progress_bar.progress(10)

                os.makedirs("docs", exist_ok=True)
                for old_file in os.listdir("docs"):
                    os.remove(os.path.join("docs", old_file))

                for uploaded_file in uploaded_files:
                    uploaded_file.seek(0)
                    save_path = os.path.join("docs", uploaded_file.name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.read())

                progress_bar.progress(25)

                # Step 2: Load documents
                status.info("📖 Loading documents...")
                docs = load_documents("docs")

                if not docs:
                    st.error("❌ No content could be extracted from the files.")
                    st.stop()

                progress_bar.progress(45)

                # Step 3: Chunk documents
                status.info("✂️ Chunking documents...")
                chunks = chunk_documents(docs)

                if not chunks:
                    st.error("❌ Failed to create chunks from documents.")
                    st.stop()

                progress_bar.progress(65)

                # Step 4: Build vector store
                status.info("🔢 Creating embeddings (this takes ~30 seconds)...")
                build_vector_store(chunks)
                progress_bar.progress(85)

                # Step 5: Build RAG chain
                status.info("🤖 Initializing AI chain...")
                st.session_state.chain = build_rag_chain()
                st.session_state.index_built = True
                st.session_state.doc_count = len(docs)
                st.session_state.chunk_count = len(chunks)
                st.session_state.messages = []

                progress_bar.progress(100)
                status.success("✅ Knowledge base ready!")

                st.success(f"""
                **Index Built Successfully!**
                - 📄 {len(docs)} page(s) loaded
                - ✂️ {len(chunks)} chunks created
                - 🧠 AI ready to answer questions
                """)

            except Exception as e:
                progress_bar.empty()
                status.empty()
                st.error(f"❌ Error building index: {str(e)}")
                st.exception(e)

    st.markdown("---")

    # Load existing index
    if st.button("📂 Load Saved Index", use_container_width=True):
        try:
            with st.spinner("Loading saved index..."):
                st.session_state.chain = build_rag_chain()
                st.session_state.index_built = True
            st.success("✅ Saved index loaded!")
        except FileNotFoundError:
            st.error("No saved index found. Please upload files and build the index.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # Clear chat
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        if st.session_state.index_built:
            try:
                st.session_state.chain = build_rag_chain()
            except Exception:
                pass
        st.rerun()

    st.markdown("---")

    # Status panel
    st.markdown("### 📊 Status")
    if st.session_state.index_built:
        st.markdown('<span class="badge-ready">🟢 Index Ready</span>',
                    unsafe_allow_html=True)
        st.markdown(f"- Pages loaded: **{st.session_state.doc_count}**")
        st.markdown(f"- Chunks indexed: **{st.session_state.chunk_count}**")
        st.markdown(f"- Messages: **{len(st.session_state.messages)}**")
    else:
        st.markdown('<span class="badge-not-ready">🟡 No Index Yet</span>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Model:** LLaMA 3.3 70B (Groq)")
    st.markdown("**Embeddings:** all-MiniLM-L6-v2")
    st.markdown("**Vector Store:** FAISS + MMR")


# ---- MAIN AREA ----
st.markdown('<div class="main-title">🧠 RAG Knowledge Assistant</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sub-title">Upload documents and ask questions — '
            'powered by LLaMA 3.3 70B + FAISS</div>',
            unsafe_allow_html=True)

# Welcome screen
if not st.session_state.index_built:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 📤 Step 1
        **Upload Documents**
        
        Use the sidebar to upload your PDF or TXT files.
        Multiple files supported.
        """)

    with col2:
        st.markdown("""
        ### ⚡ Step 2
        **Build Index**
        
        Click "Build Knowledge Index" to process 
        and embed your documents.
        """)

    with col3:
        st.markdown("""
        ### 💬 Step 3
        **Start Chatting**
        
        Ask any question about your documents.
        The AI will find and answer from your content.
        """)

    st.markdown("---")
    st.info("👈 Get started by uploading documents in the sidebar")

else:
    # Show chat interface when index is ready
    st.markdown(f"💬 **{len(st.session_state.messages) // 2} question(s) asked** "
                f"| Ask anything about your uploaded documents below")
    st.markdown("---")

# ---- DISPLAY CHAT HISTORY ----
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        # Show sources for assistant messages
        if (message["role"] == "assistant"
                and "sources" in message
                and message["sources"]):
            with st.expander(f"📄 View {len(message['sources'])} Source(s) Used"):
                for i, source in enumerate(message["sources"]):
                    st.markdown(f"""
                    <div class="source-box">
                        <strong>Source {i+1}:</strong> 
                        {os.path.basename(source['file'])} 
                        | Page: {source['page']}<br><br>
                        {source['preview']}
                    </div>
                    """, unsafe_allow_html=True)


# ---- CHAT INPUT ----
if prompt := st.chat_input(
    "Ask a question about your documents...",
    disabled=not st.session_state.index_built
):
    # Add and display user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching knowledge base..."):
            try:
                result = st.session_state.chain.invoke({
                    "question": prompt
                })

                answer = result["answer"]
                source_docs = result.get("source_documents", [])

                # Display answer
                st.write(answer)

                # Extract source metadata
                sources = []
                seen_content = set()

                for doc in source_docs:
                    # Deduplicate sources by content
                    content_key = doc.page_content[:100]
                    if content_key in seen_content:
                        continue
                    seen_content.add(content_key)

                    sources.append({
                        "file": doc.metadata.get("source",
                                doc.metadata.get("filename", "Unknown")),
                        "page": doc.metadata.get("page", "N/A"),
                        "preview": doc.page_content[:300] + "..."
                    })

                # Show sources
                if sources:
                    with st.expander(
                        f"📄 View {len(sources)} Source(s) Used"
                    ):
                        for i, source in enumerate(sources):
                            st.markdown(f"""
                            <div class="source-box">
                                <strong>Source {i+1}:</strong> 
                                {os.path.basename(source['file'])} 
                                | Page: {source['page']}<br><br>
                                {source['preview']}
                            </div>
                            """, unsafe_allow_html=True)

                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            except Exception as e:
                error_msg = (
                    f"❌ Error generating response: {str(e)}\n\n"
                    "Please try again or rebuild the index."
                )
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "sources": []
                })