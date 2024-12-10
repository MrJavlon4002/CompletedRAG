import openai
import api_keys
import json
from bot_parts.query_database import save_job_application_to_csv

FUNCTIONS = [
    {
        "name": "job_apply",
        "description":  "when user has an interest in a job, get information about job application"
                        "for example: job title, Full name, years of experience, then skills related to that job application. "
                        "If any of the details are missing in the job application, ask them from user, after generating completed job application return it as given format"
                        "return json format with the job application details the following <<<>>> /n"
                        "<<< {'job_title': 'Job Title', full_name': 'John Doe', experience: 7, skills: ['HTML','CSS','Javacipt','Vue js']} >>>",
        "parameters": {
            "type": "object",
            "properties": {
                "job_title": {
                    "type": "string",
                    "description": "job title that user wants to apply",
                },
                "full_name": {
                    "type": "string",
                    "description": "User's full name"
                },
                "years_of_experience": {
                    "type": "integer",
                    "description": "years of experience for job application that user has an interest in"
                },
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "skills related to the job application that user has an interest in"
                }
            },
            "required": ["chat_history", "latest_question"]
        }
    },
]

def call_openai_with_functions(model: str, messages: list[dict], functions: list[dict], api_key: str) -> dict:
    """
    Call OpenAI's function-calling API and return the function call result or message.
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        functions=functions,
        function_call="auto",
        api_key=api_key,
    )
    return response["choices"][0]

def contextualize_question(chat_history: list[str], latest_question: str) -> str:
    """
    Reformulate a standalone question from chat history and the latest question.
    """
    chat_history = chat_history if len(chat_history) < 4 else chat_history[-3:]

    messages = [
        {
            "role": "system",
            "content":  "Reformulate user's request like it was spoken by user, based on the chat history and the latest question."
                        "/n Do not answer the question! /n"
                        "If the user question a new question or not related to the chat history, no need to reformulate the question, just return the question itself."
                        "Your response need to be in the language that user gave last question in"
        },
        {
            "role": "user",
            "content": f"Chat History: {chat_history}\nLatest Question: {latest_question}"
        },
        {
            "role": "function",
            "name": "contextualize_question",
            "content": json.dumps({"chat_history": chat_history, "latest_question": latest_question})
        }
    ]
    response = call_openai_with_functions(
        model="gpt-4o",
        messages=messages,
        functions=FUNCTIONS,
        api_key=api_keys.openai_api_key,
    )
    return response.get("message", {}).get("content", "")

def answer_question(context: str, user_question: str) -> str:
    """
    Answer the user's question using the provided context.
    """
    messages = [
        {
            "role": "system",
            "content": (
               "You are an assistant of UIC and help people to answer based on the context information. "
               "If user's question is not about UIC, ask him/her either to give questions about UIC or make his/her question clear and specific so that you can retrieve relevant information in a given language. "
               "If user asks something outside the scope of the chat history or context, say that I don't know the answer in a given language."
               "If user asks something without greets, aswer the question."
               "If user greets with you, respond in a given language and introduce yourself."
            )
        },
        {
            "role": "user",
            "content": f"Context: {context}\nUser Question: {user_question}"
        },
    ]
    response = call_openai_with_functions(
        model="gpt-4o",
        messages=messages,
        functions=FUNCTIONS,
        api_key=api_keys.openai_api_key,
    )

    function_call = response.get("message", {}).get("function_call")
    if function_call:
        arguments = json.loads(function_call.get("arguments", "{}"))
        save_job_application_to_csv(arguments)
        print(f"---- {arguments} ----")
        return "Sizning malumotlaringiz saqlab qo'yildi."
    return response.get("message", {}).get("content", "")

