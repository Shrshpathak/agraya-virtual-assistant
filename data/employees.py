
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

            # Annual salary in INR
            "salary": random.randint(650000, 3000000)
        }

        employees.append(employee)

    return employees
