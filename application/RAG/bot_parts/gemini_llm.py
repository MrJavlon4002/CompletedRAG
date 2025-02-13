import google.generativeai as genai
from RAG import api_keys
from langdetect import detect_langs

gemini_model = "gemini-2.0-flash-exp"

def language_detection(query: str) -> str:
    """
    Detect language of input text and return standardized language code.
    Returns 'en' for English and similar languages,
    'ru' for Russian, and 'uz' as default.
    """
    lang_list = detect_langs(query)

    for lang in lang_list:
        lang_str = str(lang).split(':')[0]
        if lang_str in ['en', 'fi', 'nl','de',"no"]:
            return 'en'
        elif lang_str in ['ru', 'uk', 'mk']:
            return 'ru'
    return 'uz'

def check_uic_relevance(questions: str, user_question) -> bool:
    return True
    """
    Check if the question is relevant to UIC company and requires database access.
    """
    system_instruction = (
        "You are a classifier that determines if a question is related to UIC company.\n"
        "Output only 'true' if the Main question question is related UIC company, its services, staff, or operations.\n"
        "Output only 'false' for Main questions, greetings, or unrelated topics."
    )
    
    genai.configure(api_key=api_keys.gemini_api_key)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)
    response = model.generate_content(f"Documentory questions:{questions} \nMain question: {user_question}")
    try:
        return response.text.strip().lower() == 'true'
    except Exception as e:
        print(f"Error in relevance check: {e}")
        return False

def call_gemini_with_functions(model_name: str, messages: str, api_key: str, system_instruction: str)->list[str]:
    """
    Call the Gemini API with tools and handle responses or errors gracefully.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction
    )

    try:
        response = model.generate_content(
            contents=[messages],
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
            ),
        )

        return response.candidates[0].content.parts[0].text.split('\n'),

    except Exception as e:
        print(f"Error during Gemini call: {e}")
        return {"error": str(e)}

def contextualize_question(chat_history: list[str], latest_question: str, company_name:str) -> dict:
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

    result["text"] = list(call_gemini_with_functions(
        model_name=gemini_model,
        messages=messages,
        api_key=api_keys.gemini_api_key,
        system_instruction=system_instruction
    ))
    result["requires_db"] = check_uic_relevance(questions=str(result["text"]), user_question=latest_question)
    
    return result


def answer_question(context: str, reformulations: list[str], user_question: str, company_name:str):
    """
    Answer the user's question using the provided context.
    """
    lang = language_detection(user_question)
    system_instruction = (
        f"You must always respond in {lang} language as the user's Main question.\n"
        "As a defoult language you can use Uzbek."
        f"You are helpfull assistant for {company_name}, helping users with questions based on provided *Company Data*.\n\n"
        "1. Break down the user's question into smaller parts if necessary.\n"
        "2. Think step-by-step to ensure you understand the user's needs.\n"
        "3. When you do not know the answer, just say that."
        "4. Answer using the most relevant information from the *Company Data*.\n"
        "5. If user greets you, intraduce yourself, otherwise GIVE DIRECT ANSWER.\n"
        "6. If user seems satesfied from servece, say that you are happy to serve.\n"
        "7. Main question takes priority over documentary questions.\n"
        "8. Interact naturally as if responding to just the main question.\n"
        "9. Keep documentary questions as secondary context.\n\n"
    )

    print(f"Main question: {user_question}\nDocumentary questions:{reformulations}")

    messages = f"Company Data: {context}\nDocumentary questions: {reformulations}, Main question: {user_question}"
    genai.configure(api_key=api_keys.gemini_api_key)
    model = genai.GenerativeModel(model_name= gemini_model, tools=None, system_instruction=system_instruction)
    try:
        response_stream = model.generate_content(
            messages,
            stream=True,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
            ),
        )

        for response_chunk in response_stream:
            chunk_text = response_chunk.candidates[0].content.parts[0].text
            yield chunk_text

    except KeyError as e:
        print(f"KeyError: {e}")
        yield {}
    except Exception as e:
        print(f"An error occurred during streaming: {e}")
        yield {}
