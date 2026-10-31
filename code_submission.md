## app.py

```python
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

    customer_data = get_user_data()
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

    llm = ChatGroq(
        model="openai/gpt-oss-20b"
    )

    assistant = Assistant(
        system_prompt=SYSTEM_PROMPT,
        llm=llm,
        message_history=st.session_state.messages,
        employee_information=st.session_state.customer,
        vector_store=vector_store
    )

    gui = AssistantGUI(assistant)
    gui.render()
```

## assistant.py

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class Assistant:
    def __init__(
        self,
        system_prompt,
        llm,
        message_history=[],
        vector_store=None,
        employee_information=None,
    ):
        self.system_prompt = system_prompt
        self.llm = llm
        self.messages = message_history
        self.vector_store = vector_store
        self.employee_information = employee_information

        self.chain = self._get_conversation_chain()

    def get_response(self, user_input):
        return self.chain.stream(user_input)

    def _get_conversation_chain(self):
        prompt = ChatPromptTemplate(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder("conversation_history"),
                ("human", "{user_input}"),
            ]
        )

        llm = self.llm
        output_parser = StrOutputParser()

        chain = (
            {
                "retrieved_policy_information": self.vector_store.as_retriever(),
                "employee_information": lambda x: self.employee_information,
                "user_input": RunnablePassthrough(),
                "conversation_history": lambda x: self.messages,
            }
            | prompt
            | llm
            | output_parser
        )
        return chain
```

## gui.py

```python
import streamlit as st


class AssistantGUI:
    def __init__(self, assistant):
        self.assistant = assistant
        self.messages = assistant.messages
        self.employee_information = assistant.employee_information

    def get_response(self, user_input):
        return self.assistant.get_response(user_input)

    def render_messages(self):
        messages = self.messages

        for message in messages:
            if message["role"] == "user":
                st.chat_message("human").markdown(message["content"])

            if message["role"] == "ai":
                st.chat_message("ai").markdown(message["content"])

    def set_state(self, key, value):
        st.session_state[key] = value

    def format_inr(self, amount):
        amount = str(int(amount))

        if len(amount) > 3:
            last_three = amount[-3:]
            remaining = amount[:-3]

            groups = []

            while len(remaining) > 2:
                groups.insert(0, remaining[-2:])
                remaining = remaining[:-2]

            if remaining:
                groups.insert(0, remaining)

            amount = ",".join(groups + [last_three])

        return f"₹{amount} per year (Annual CTC)"

    def render_user_input(self):
        user_input = st.chat_input("Ask Agraya Assistant...", key="input")

        if user_input and user_input != "":
            st.chat_message("human").markdown(user_input)

            response_generator = self.get_response(user_input)

            with st.chat_message("ai"):
                response = st.write_stream(response_generator)

            self.messages.append({
                "role": "user",
                "content": user_input
            })

            self.messages.append({
                "role": "ai",
                "content": response
            })

            self.set_state("messages", self.messages)

    def render(self):
        with st.sidebar:

            st.title("🧬 Agraya Corporation")
            st.caption("AI Employee Virtual Assistant")

            st.divider()

            st.subheader("Employee Information")

            employee_display = self.employee_information.copy()

            salary = employee_display.get("salary")

            if isinstance(salary, (int, float)):
                employee_display["salary"] = self.format_inr(salary)

            st.write(employee_display)

        self.render_messages()
        self.render_user_input()
```

## prompts.py

```python
SYSTEM_PROMPT = """
You are the official AI Virtual Assistant of Agraya Corporation,
a fictional Indian-headquartered multinational company operating
in the pharmaceutical, biotechnology, and life-sciences industries.

Your main responsibility is to assist employees with onboarding,
company policies, workplace guidelines, employee information,
and general workplace queries.

You have access to two information sources:

1. Employee Information:
   Details about the employee currently interacting with you.

2. Company Policies:
   Relevant information retrieved from Agraya Corporation's
   internal policy document using a vector database.

Current Employee Information:
{employee_information}

Retrieved Company Policy Information:
{retrieved_policy_information}

Follow these guidelines:

1. Communication:
    - Be friendly, professional, and respectful.
    - Use simple and understandable English.
    - Give clear and direct answers.
    - Maintain a natural conversational style.
    - Remember the context of the ongoing conversation.

2. Company Policy Questions:
    - Use the retrieved policy information to answer questions.
    - Do not invent company rules, policies, benefits, or procedures.
    - If the available policy information does not answer a question,
      clearly mention that the document does not specify it.
    - Suggest contacting HR or the relevant department when necessary.

3. Employee Information:
    - Use the current employee information when relevant.
    - Personalize answers using the employee's name, position,
      department, supervisor, and location.
    - Never reveal another employee's private information.

4. Basic Tasks:
    - Help employees draft leave request emails.
    - Help prepare onboarding checklists.
    - Draft professional workplace messages.
    - Explain company procedures step by step.
    - Help employees understand their responsibilities.
    - Do not claim that an email has been sent, leave has been
      approved, or any external action has been completed.

5. Accuracy:
    - Do not make up salary details, leave balances, approval status,
      or other employee records.
    - Clearly distinguish between information from company policies
      and general suggestions.
    - Do not present this fictional demo policy document as verified
      legal or regulatory advice.

6. Escalation:
    - For payroll questions, suggest contacting HR or Finance.
    - For technical problems, suggest contacting IT Support.
    - For security concerns, suggest contacting the Security Team.
    - For compliance concerns, suggest contacting the Compliance Team.

Your goal is to make employees' daily work easier by providing
accurate information, answering questions conversationally,
and assisting with basic workplace tasks.

Now answer the employee's question using the available context.
"""


WELCOME_MESSAGE = """
Welcome to Agraya Corporation!

Hello! I am your AI Virtual Assistant.

I can help you with:

- Company policies and guidelines
- Employee information
- Onboarding procedures
- HR and workplace-related queries
- Data security and compliance
- Leave request email drafts
- General workplace assistance

Feel free to ask me anything about your work at Agraya Corporation.

How can I help you today?
"""
```

## data/employees.py

```python
import random
import re
from faker import Faker
from datetime import datetime, timedelta


def generate_employee_data(num_employees=5):
    employees = []

    for _ in range(num_employees):

        locale = random.choices(
            ["en_IN", "en_US"],
            weights=[70, 30],
            k=1
        )[0]

        fake = Faker(locale)

        first_name = fake.first_name()
        last_name = fake.last_name()

        email_name = re.sub(
            r"[^a-z0-9.]",
            "",
            f"{first_name}.{last_name}".lower()
        )

        employee = {
            "employee_id": fake.uuid4(),
            "name": first_name,
            "lastname": last_name,
            "email": f"{email_name}@agrayacorp.in",
            "phone_number": fake.phone_number(),

            "position": random.choice([
                "Research Scientist",
                "Software Engineer",
                "Operations Manager",
                "HR Specialist",
                "Security Officer"
            ]),

            "department": random.choice([
                "R&D",
                "IT",
                "Operations",
                "HR",
                "Security"
            ]),

            "skills": random.sample([
                "Python",
                "Project Management",
                "Data Analysis",
                "Genetic Research",
                "Cybersecurity",
                "Machine Learning",
                "Leadership",
                "Database Management",
                "Public Speaking"
            ], k=random.randint(2, 5)),

            "location": random.choice([
                "New Delhi, India",
                "Mumbai, India",
                "Lucknow, India",
                "London, UK",
                "Singapore",
                "Toronto, Canada"
            ]),

            "hire_date": (
                datetime.now() - timedelta(
                    days=random.randint(1, 365 * 10)
                )
            ).strftime("%Y-%m-%d"),

            "supervisor": fake.name(),
            "salary": random.randint(650000, 3000000)
        }

        employees.append(employee)

    return employees
```

## requirements.txt

```pip
langchain==0.3.1
langchain-community==0.3.1
langchain-chroma==0.1.4
langchain-groq==0.2.0
langchain-openai==0.2.1
streamlit==1.38.0
pypdf==5.0.1
python-dotenv==1.0.1
Faker==30.0.0
langchain-huggingface==0.1.0
```

## .env.example

```dotenv
GROQ_API_KEY=your_groq_api_key
```
