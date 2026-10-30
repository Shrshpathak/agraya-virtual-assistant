# 🏢 Agraya Corporation Virtual Assistant

An AI-powered chatbot that helps employees find answers to their everyday company-related questions.

The **Agraya Corporation Virtual Assistant** uses Retrieval-Augmented Generation (RAG) to understand company documents and provide helpful answers about workplace policies, employee information, and company guidelines.

Instead of searching through long PDF documents, employees can simply ask a question and get a relevant answer through the chatbot.

## ✨ Features

- 💬 **Interactive Chatbot:** Ask questions in simple, natural language.
- 📄 **Document-Based Answers:** Finds relevant information from company policy documents.
- 👨‍💼 **Employee Information:** Provides employee-related details using available employee data.
- 🧠 **RAG-Based System:** Combines document retrieval with an AI language model to generate useful responses.
- 🏢 **Company-Focused Assistant:** Designed to support everyday employee queries.
- ⚡ **Streamlit Interface:** Simple and easy-to-use chat interface.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Chatbot interface |
| LangChain | RAG workflow |
| Groq | AI model integration |
| ChromaDB | Vector database |
| Hugging Face | Text embeddings |
| PyPDF | Reading PDF documents |
| Faker | Generating sample employee data |

## ⚙️ How It Works

1. The company policy PDF is loaded into the application.
2. The document is divided into smaller text sections.
3. Hugging Face embeddings convert these sections into vectors.
4. ChromaDB stores the vectors for searching.
5. When an employee asks a question, the system retrieves relevant information.
6. The AI model uses that information to generate a response.

## 🚀 Getting Started

Follow these steps to run the project on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/Shrshpathak/agraya-virtual-assistant.git
```

### 2. Open the Project Folder

```bash
cd agraya-virtual-assistant
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Your API Key

Create a `.env` file in the project folder and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key
```

Keep your API key private. Never upload your `.env` file to GitHub.

### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser.

## 📁 Project Resources

- `app.py` – Main application file.
- `assistant.py` – Handles chatbot responses and retrieval.
- `gui.py` – Manages the Streamlit chat interface.
- `prompts.py` – Contains the assistant's instructions.
- `data/` – Stores company policy documents and related data.
- `requirements.txt` – Contains the required Python packages.

## 🎯 Project Goal

The main goal of this project is to make company information easier to access. Employees can ask questions directly instead of manually searching through multiple documents.

It is a practical implementation of RAG that brings together document processing, vector search, and AI-based question answering in one application.

---

**Built  using Python, LangChain, and Streamlit.**
