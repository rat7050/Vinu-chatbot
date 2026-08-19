# 🤖 Vinu Chatbot

A simple and interactive AI chatbot built with **Python, Streamlit, LangChain, and Groq**.

Vinu Chatbot provides a clean conversational interface where users can ask questions and receive AI-generated responses powered by the **`openai/gpt-oss-20b`** model through Groq. The application also maintains the current conversation using Streamlit session state.

---

## ✨ Features

* 💬 Interactive chat interface
* 🤖 AI-powered responses
* ⚡ Fast inference using Groq
* 🦜 LangChain integration
* 🎨 Streamlit web UI
* 🧠 Conversation history during the active session
* 🔐 API key stored using Streamlit secrets
* 🐍 Simple Python implementation

---

## 🛠️ Tech Stack

| Technology       | Purpose                     |
| ---------------- | --------------------------- |
| 🐍 Python        | Core programming language   |
| 🎈 Streamlit     | Web-based chatbot interface |
| 🦜 LangChain     | LLM integration             |
| ⚡ Groq           | Fast model inference        |
| 🧠 GPT-OSS-20B   | Large language model        |
| 🔑 python-dotenv | Environment configuration   |

The repository currently declares `streamlit`, `langchain`, `langchain-core`, `langchain-groq`, and `python-dotenv` in `requirements.txt`.

---

## 🏗️ Architecture

```text
                 ┌──────────────────┐
                 │      User        │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Streamlit UI   │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Vinu Chatbot   │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   LangChain      │
                 │   ChatGroq       │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  GPT-OSS-20B     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ AI Response      │
                 └──────────────────┘

        Conversation history
                 │
                 ▼
          Streamlit Session State
```

---

## 📁 Project Structure

```text
Vinu-chatbot/
│
├── chatbot.py
├── requirements.txt
├── .gitignore
│
└── .devcontainer/
    └── devcontainer.json
```

### File Description

| File                              | Description                         |
| --------------------------------- | ----------------------------------- |
| `chatbot.py`                      | Main Streamlit chatbot application  |
| `requirements.txt`                | Python dependencies                 |
| `.gitignore`                      | Files excluded from Git             |
| `.devcontainer/devcontainer.json` | Development container configuration |

The current repository contains these files on the `main` branch.

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/rat7050/Vinu-chatbot.git
```

```bash
cd Vinu-chatbot
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Configure Groq API Key

The application reads the Groq API key from **Streamlit secrets**.

For local development, create:

```text
.streamlit/secrets.toml
```

Add:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

> ⚠️ Never commit your API key to GitHub.

---

# ▶️ Run the Application

Start Streamlit with:

```bash
streamlit run chatbot.py
```

Open the URL shown by Streamlit, usually:

```text
http://localhost:8501
```

You can then start chatting with Vinu.

---

# 💬 Example Questions

Try questions such as:

```text
What is Artificial Intelligence?
```

```text
Explain machine learning in simple terms.
```

```text
What is LangChain?
```

```text
Write a Python program to reverse a string.
```

```text
Explain the difference between AI and ML.
```

---

# 🧠 How It Works

The chatbot follows a straightforward workflow:

```text
User enters message
        ↓
Streamlit receives input
        ↓
ChatGroq sends the request
        ↓
GPT-OSS-20B generates response
        ↓
Response displayed in chat
        ↓
Message stored in session state
```

The application initializes a `ChatGroq` model with:

```python
model = ChatGroq(
    temperature=0,
    model_name="openai/gpt-oss-20b",
    max_tokens=100
)
```

It stores user and assistant messages in `st.session_state.messages`.

---

# 🧠 Conversation Memory

Vinu Chatbot maintains chat history while the Streamlit session is active.

The application uses:

```python
st.session_state.messages
```

to store messages in the following format:

```python
{
    "role": "user",
    "content": "What is AI?"
}
```

and:

```python
{
    "role": "assistant",
    "content": "Artificial Intelligence..."
}
```

This allows previous messages to remain visible during the current session.

---

# 🎨 User Interface

The chatbot provides a simple interface with:

```text
╔══════════════════════════════════════╗
║          🤖 Vinu Chatbot             ║
║                                      ║
║  Ask anything to Vinu                ║
║                                      ║
║  👤 What is Python?                  ║
║                                      ║
║  🤖 Python is a programming...       ║
║                                      ║
║  ──────────────────────────────────  ║
║  Ask your question here...           ║
╚══════════════════════════════════════╝
```

---

# 🔒 Security

Keep your API key private.

### ❌ Never do this

```python
GROQ_API_KEY = "gsk_xxxxxxxxx"
```

### ✅ Use Streamlit secrets

```toml
GROQ_API_KEY = "your_groq_api_key"
```

This keeps credentials outside your source code.

---

# 🚧 Future Improvements

This project can be made much more powerful by adding:

* [ ] 🧠 Proper conversational context sent to the LLM
* [ ] 🌐 Web search capability
* [ ] 📄 PDF/document question answering
* [ ] 📚 RAG with a vector database
* [ ] 🎤 Voice input
* [ ] 🔊 Text-to-speech responses
* [ ] 👤 User authentication
* [ ] 💾 Persistent chat history
* [ ] 🗑️ Clear conversation button
* [ ] 🌙 Dark/light theme
* [ ] 📱 Responsive UI
* [ ] 🚀 Deployment
* [ ] 📊 Chat analytics

---

# 🌐 Deployment

The application is suitable for deployment on Streamlit-compatible hosting platforms.

Before deploying, configure the following secret:

```text
GROQ_API_KEY
```

as a secure deployment secret rather than placing it directly in the repository.

---

# 📚 Learning Objectives

This project demonstrates practical usage of:

* Large Language Models
* Generative AI
* LangChain
* Groq API
* Streamlit
* Python
* Chat interfaces
* Session-based conversation state
* API key management

---

# 🎯 Project Goal

The goal of **Vinu Chatbot** is to build a lightweight AI assistant with a simple user interface while learning how modern LLM applications are developed with Python.

```text
Python
   +
LangChain
   +
Groq
   +
GPT-OSS-20B
   +
Streamlit
   =
🤖 Vinu Chatbot
```

---

# 👨‍💻 Author

## Ratnesh Kumar

B.Tech — Artificial Intelligence & Data Science

GitHub: [@rat7050](https://github.com/rat7050)

---

# ⭐ Support

If you found this project useful, consider giving the repository a ⭐ on GitHub.

---

## 📄 License

This project is created for educational and learning purposes.
