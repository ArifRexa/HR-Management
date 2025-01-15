import json
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

prompt_template = """
    You are a project management assistant. Your task is to process the following daily report and format it into a highly detailed and structured weekly development update in JSON format.

    **Instructions:**
    1. First divide given report into features.
    2. Organize the report by Feature.
    3. For each Feature, list related tasks using bullet points.
    4. For each task accomplished, provide a detailed description of what was done.
    5. Include a "Links for Review" section with relevant links and descriptions. If no links are provided, keep this section completely empty mentioning "- No links provided.".
    6. Add a "Looking Ahead" section to outline future tasks with detailed descriptions.
    7. Use a professional tone and ensure the output is concise yet highly detailed.
    8. Use hyphens (-) for bullet points instead of Unicode characters.
    9. Return the output in JSON format.

    **Daily Report:**
    {daily_report}

    **Expected Output Format (JSON):**
    {{
        "tasks": [
            {{
                "feature": "<Feature Name 1>",
                "subtasks": [
                    "<Detailed description of subtasks if any>"
                ]
            }},
            {{
                "feature": "<Feature Name 2>",
                "subtasks": [
                    "<Detailed description of subtasks if any>"
                ]
            }}
        ],
        "links_for_review": [
            {{
                "description": "<Description of the functionality or page>",
                "link": "<Link>"
            }}
        ],
        "looking_ahead": [
            {{
                "description": "<Detailed description of the planned task>"
            }}
        ]
    }}

    Please format the daily report accordingly, ensuring the output is as detailed as possible.
    """


class ClientWeeklyUpdate:
    def __init__(self, update):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.open_ai_model = "gpt-4o-2024-08-06"
        self.open_ai_embedding_model = "text-embedding-3-large"
        self.prompt = """
            You are a project management assistant. Your task is to process the following daily report and format it into a highly detailed and structured weekly development update in JSON format.

            **Instructions:**
            1. First divide given report into features.
            2. Organize the report by Feature.
            3. For each Feature, list related tasks using bullet points.
            4. For each task accomplished, provide a detailed description of what was done.
            5. Include a "Links for Review" section with relevant links and descriptions. If no links are provided, keep this section completely empty mentioning "- No links provided.".
            6. Add a "Looking Ahead" section to outline future tasks with detailed descriptions.
            7. Use a professional tone and ensure the output is concise yet highly detailed.
            8. Use hyphens (-) for bullet points instead of Unicode characters.
            9. Return the output in JSON format.

            **Daily Report:**
            {daily_report}

            **Expected Output Format (JSON):**
            {{
                "tasks": [
                    {{
                        "feature": "<Feature Name 1>",
                        "subtasks": [
                            "<Detailed description of subtasks if any>"
                        ]
                    }},
                    {{
                        "feature": "<Feature Name 2>",
                        "subtasks": [
                            "<Detailed description of subtasks if any>"
                        ]
                    }}
                ],
                "links_for_review": [
                    {{
                        "description": "<Description of the functionality or page>",
                        "link": "<Link>"
                    }}
                ],
                "looking_ahead": [
                    {{
                        "description": "<Detailed description of the planned task>"
                    }}
                ]
            }}

            Please format the daily report accordingly, ensuring the output is as detailed as possible.
        """
        self.update = update
        self.llm = ChatOpenAI(
            model="gpt-4", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.prompt_template = PromptTemplate(
            input_variables=["daily_report"], template=prompt_template
        )

    def create_chain(self):
        return RunnablePassthrough() | self.prompt_template | self.llm

    def chat(self):
        try:
            chain = self.create_chain()
            res = chain.invoke({"daily_report": self.update})
            return json.loads(res.content)
        except json.JSONDecodeError:
            return None
