<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0c29,50:302b63,100:24243e&height=220&section=header&text=🧠%20RAG%20Knowledge%20Assistant&fontSize=45&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Talk%20to%20your%20documents%20using%20AI%20•%20Powered%20by%20LLaMA%203.3%2070B%20•%20100%25%20Free&descAlignY=58&descSize=16&descColor=aaaaaa" width="100%"/>

<br/>

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)
![LLaMA](https://img.shields.io/badge/LLaMA_3.3_70B-F55036?style=for-the-badge&logo=meta&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Store-0467DF?style=for-the-badge&logo=meta&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Free_Inference-F55036?style=for-the-badge&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

<br/>

[![Live Demo](https://img.shields.io/badge/🚀%20LIVE%20DEMO-%20Click%20Here-FF4B4B?style=for-the-badge)](https://your-app-url.streamlit.app)

<br/>

> **Upload any PDF or text document.**
> **Ask any question.**
> **Get instant AI-powered answers with source citations.**

<br/>

| 🎯 90%+ Accuracy | ⚡ 2–4s Response | 💬 Memory | 💰 100% Free | ☁️ Cloud Ready |
|:---:|:---:|:---:|:---:|:---:|
| Strict RAG prompting | Groq fast inference | 5 turn history | Zero cost | Streamlit Cloud |

</div>

---

## 📌 Table of Contents

- [What Is This?](#-what-is-this)
- [Features](#-features)
- [Architecture](#️-architecture)
- [Tech Stack](#️-tech-stack)
- [Quick Start](#-quick-start)
- [Deploy to Cloud](#️-deploy-to-streamlit-cloud)
- [Project Structure](#-project-structure)
- [Performance](#-performance)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#️-roadmap)
- [Author](#-author)

---

## 🧠 What Is This?

**RAG Knowledge Assistant** is a production-grade AI application that lets you have intelligent conversations with your own documents.

Upload a **PDF** or **TXT** file and the AI will read, understand, and answer any question about it — referencing the exact source it used to generate the answer.

> No hallucinations &nbsp;•&nbsp; No guessing &nbsp;•&nbsp; Only answers from **YOUR** documents

**RAG** stands for **Retrieval-Augmented Generation** — a technique where:

1. 📄 Your document is broken into chunks and stored as vectors
2. 🔍 When you ask a question, the most relevant chunks are retrieved
3. 🤖 Those chunks are passed to the LLM as context
4. ✅ The LLM answers **strictly** from that context

This gives you **GPT-4 level intelligence** applied **specifically to your documents**.

---

## ✨ Features

<table>
<tr>
<td width="50%" valign="top">

### 📤 Multi-File Upload
Upload multiple **PDF** or **TXT** files at once. The system processes all of them into a single searchable knowledge base.

</td>
<td width="50%" valign="top">

### 🔍 MMR Retrieval
Uses **Maximal Marginal Relevance** search to return the most relevant AND diverse chunks — not just the most similar ones.

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🤖 LLaMA 3.3 70B
Powered by Meta's most capable open model running on **Groq's free API** — same quality as GPT-4 at zero cost.

</td>
<td width="50%" valign="top">

### 💬 Conversation Memory
Remembers your last **5 exchanges** so you can ask natural follow-up questions without repeating context.

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 📄 Source Citations
Every answer shows the **exact document chunks** used — including file name and page number for full transparency.

</td>
<td width="50%" valign="top">

### 🎯 Hallucination Prevention
Strict prompt engineering forces the LLM to answer **only from your documents** — never from outside knowledge.

</td>
</tr>
<tr>
<td width="50%" valign="top">

### ⚡ Fast Indexing
Documents are chunked, embedded and indexed in **under 60 seconds** regardless of file size.

</td>
<td width="50%" valign="top">

### ☁️ One-Click Deploy
Fully configured for **Streamlit Cloud** deployment — share your app with anyone via a public URL for free.

</td>
</tr>
</table>

---

## 🏗️ Architecture
