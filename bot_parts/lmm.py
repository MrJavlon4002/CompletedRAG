import openai
import api_keys
import json

FUNCTIONS = [
    {
        "name": "contextualize_question",
        "description": "Formulate a standalone question from chat history and the latest question.",
        "parameters": {
            "type": "object",
            "properties": {
                "chat_history": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of previous chat messages.",
                },
                "latest_question": {
                    "type": "string",
                    "description": "The latest user question to reformulate."
                }
            },
            "required": ["chat_history", "latest_question"]
        }
    },
    {
        "name": "answer_question",
        "description": "Answer a user question using the provided context as an polite assistent of the company.",
        "parameters": {
            "type": "object",
            "properties": {
                "context": {
                    "type": "string",
                    "description": "The relevant context for answering the question."
                },
                "user_question": {
                    "type": "string",
                    "description": "The user's question to answer."
                }
            },
            "required": ["context", "user_question"]
        }
    }
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
    messages = [
        {
            "role": "system",
            "content": "Given a chat history and the latest user question, "
                       "formulate a standalone question that can be understood "
                       "without the chat history. Do NOT answer the question, "
                       "just reformulate it if needed."
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
        model="gpt-4",
        messages=messages,
        functions=FUNCTIONS,
        api_key=api_keys.openai_api_key,
    )
    
    function_call = response.get("function_call")
    if function_call and function_call["name"] == "contextualize_question":
        arguments = json.loads(function_call["arguments"])
        return arguments.get("latest_question", "")
    return response.get("message", {}).get("content", "")


def answer_question(context: str, user_question: str) -> str:
    """
    Answer the user's question using the provided context.
    """
    messages = [
        {
            "role": "system",
            "content": "You are an assistant for UIC company that answers questions about the company and jobs. "
                       "If the question is relevant, use the retrieved context to answer the question. "
                       "If you don't know the answer, say that"
                       "If the user just greets you, respond politely. Otherwise, let the user know that you can only answer questions related to the company."
                       "Your answer has to be in Uzbek language."
        },
        {
            "role": "user",
            "content": f"Context: {context}\nUser Question: {user_question}"
        },
        {
            "role": "function",
            "name": "answer_question",
            "content": json.dumps({"context": context, "user_question": user_question})
        }
    ]
    response = call_openai_with_functions(
        model="gpt-4",
        messages=messages,
        functions=FUNCTIONS,
        api_key=api_keys.openai_api_key,
    )
    
    function_call = response.get("function_call")
    print(response)
    if function_call and function_call["name"] == "answer_question":
        arguments = json.loads(function_call["arguments"])
        return arguments.get("context", "")  
    return response.get("message", {}).get("content", "")