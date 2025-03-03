import openai
from langdetect import detect_langs
from django.conf import settings

# Assuming you have your OpenAI API key in settings
openai.api_key = settings.OPENAI_API_KEY
openai_model = "gpt-4o"  # You can change this to your preferred OpenAI model

def language_detection(query: str) -> str:
    """
    Detect language of input text and return standardized language code.
    Returns 'en' for English and similar languages,
    'ru' for Russian, and 'uz' as default.
    """
    lang_list = detect_langs(query)

    for lang in lang_list:
        lang_str = str(lang).split(':')[0]
        if lang_str in ['en', 'fi', 'nl', 'de', "no"]:
            return 'en'
        elif lang_str in ['ru', 'uk', 'mk']:
            return 'ru'
    return 'uz'

def call_openai_with_functions(model_name: str, messages: str, api_key: str, system_instruction: str) -> list[str]:
    """
    Call the OpenAI API and handle responses or errors gracefully.
    """
    client = openai.OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": messages}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.split('\n')
    
    except Exception as e:
        print(f"Error during OpenAI call: {e}")
        return {"error": str(e)}

def contextualize_question(chat_history: list[str], latest_question: str, company_name: str) -> dict:
    """
    Reformulate a standalone question using chat history.
    """
    chat_history = chat_history[-3:] if len(chat_history) > 3 else chat_history

    result = {}
    result["lang"] = language_detection(query=latest_question)
    system_instruction = (
        "Reformulate user request as follows:\n\n"
        "1. If not connected to history logically:\n"
        f"   - Reformulate to make it related to {company_name} company.\n\n"
        f"2. For {company_name} Company-related queries:\n"
        f"   - Use chat history and the latest question to create **2 reformulations** connection to {company_name} company.\n"
        "   - Make sure questions focus on different aspect of user's Latest question.\n\n"
        "Always:\n"
        f"- Reformulations have to be in {result['lang']} language as the user's *Latest question*.\n"
        "- Provide only reformulations`.\n"
        "- Avoid answering or explaining; only reformulate.\n"
    )

    messages = f"Chat history: {chat_history}\nLatest question: {latest_question}"

    result["text"] = list(call_openai_with_functions(
        model_name=openai_model,
        messages=messages,
        api_key=settings.OPENAI_API_KEY,
        system_instruction=system_instruction
    ))
    
    return result

def answer_question(context: str, reformulations: list[str], user_question: str, company_name: str):
    """
    Answer the user's question using the provided context.
    """
    lang = language_detection(user_question)
    system_instruction = (
        f"You must always respond in {lang} language as the user's Main question.\n"
        "As a default language you can use Uzbek."
        f"You are a sales manager for {company_name}, assisting users with questions based on provided *Company Data*.\n\n"
        "1. Break down the user's question into smaller parts if necessary.\n"
        "2. Think step-by-step to ensure you understand the user's needs.\n"
        "3. When you do not know the answer, just say that."
        "4. Answer using the most relevant information from the *Company Data*.\n"
        "5. If user greets you, introduce yourself as a sales manager for {company_name}, otherwise GIVE DIRECT ANSWER.\n"
        "6. If user seems satisfied with the service, say that you are happy to assist them.\n"
        "7. Main question takes priority over documentary questions.\n"
        "8. Interact naturally as if responding to just the main question.\n"
        "9. Keep documentary questions as secondary context.\n\n"
    )

    print(f"Main question: {user_question}\nDocumentary questions:{reformulations}")

    messages = f"Company Data: {context}\nDocumentary questions: {reformulations}, Main question: {user_question}"
    
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    try:
        response_stream = client.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": messages}
            ],
            temperature=0.3,
            stream=True
        )

        for chunk in response_stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        print(f"An error occurred during streaming: {e}")
        yield {}
