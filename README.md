# 🔗 Chainlit + FastAPI + OpenAI Agent SDK – Real-Time Agentic Chat

This project combines **FastAPI** and **OpenAI Agent SDK** to build a backend LLM agent with tool calls and real-time streaming support. It uses **Chainlit** as the frontend for a clean developer interface and supports **token-by-token streaming**, **tool call visual steps**, and **agent switching**.

---

## 🚀 Features

- 🧪 **Chainlit** for UI with live agent step visualization
- 🧠 Agent execution using **OpenAI Agent SDK**
- ⚙️ Uses **FastAPI** for scalable backend routing
- 🔧 Support for **tool calls** and **tool HandsOff**
- ✅ Token-by-token **streaming** to Chainlit using SSE

---

## Quick Start
1. Clone the Repo

- git clone https://github.com/yourusername/agent-fastapi-streaming.git
- cd agent-fastapi-streaming

2. Setup Environment with uv

- uv venv
- source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
- uv pip install .  

3. Set Environment Variables

- Create a .env file in the root:
- GEMINI_API_KEY=your_gemini_or_openai_key_here

