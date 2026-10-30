
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
