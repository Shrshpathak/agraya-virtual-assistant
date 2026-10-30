
import logging
from pathlib import Path

from dotenv import load_dotenv
import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

from data.employees import generate_employee_data
from assistant import Assistant
from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE
from gui import AssistantGUI


if __name__ == "__main__":

    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    st.set_page_config(
        page_title="Agraya Corporation | Employee Assistant",
        page_icon="🧬",
        layout="wide"
    )

    PDF_PATH = Path("data/agraya_corporation_policies_demo.pdf")

    if not PDF_PATH.exists():
        st.error(
            f"Policy PDF not found: {PDF_PATH}. "
            "Please place the Agraya PDF inside the data folder."
        )
        st.stop()

    @st.cache_data(
        ttl=3600,
        show_spinner="Loading Employee Data..."
    )
    def get_user_data():
        return generate_employee_data(1)[0]

    @st.cache_resource(
        ttl=3600,
        show_spinner="Loading Agraya Policy Database..."
    )
    def init_vector_store(pdf_path):

        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=200
            )

            splits = text_splitter.split_documents(docs)

            embedding_function = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )

            # Separate database for Agraya policies
            persistent_path = "./data/agraya_vectorstore"

            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=embedding_function,
                collection_name="agraya_corporate_policies",
                persist_directory=persistent_path
            )

            return vectorstore

        except Exception as e:
            logging.error(
                f"Error initializing vector store: {str(e)}"
            )

            st.error(
                f"Failed to initialize policy database: {str(e)}"
            )

            return None

    # Load employee information
    customer_data = get_user_data()

    # Load Agraya policy PDF into ChromaDB
    vector_store = init_vector_store(str(PDF_PATH))

    if vector_store is None:
        st.stop()

    if "customer" not in st.session_state:
        st.session_state.customer = customer_data

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "ai",
                "content": WELCOME_MESSAGE
            }
        ]

    # Groq LLM
    llm = ChatGroq(
        model="openai/gpt-oss-20b"
    )

    # Initialize assistant
    assistant = Assistant(
        system_prompt=SYSTEM_PROMPT,
        llm=llm,
        message_history=st.session_state.messages,
        employee_information=st.session_state.customer,
        vector_store=vector_store
    )

    # Render Streamlit interface
    gui = AssistantGUI(assistant)
    gui.render()
