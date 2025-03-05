import openai
from langdetect import detect_langs
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY
openai_model = "gpt-4o"

def language_detection(query: str) -> str:
    """
    Detect language of input text and return standardized language code.
    Returns 'en' for English and similar languages,
    'ru' for Russian, and 'uz' as default.
    """
    lang_list = detect_langs(query)

    for lang in lang_list:
        lang_str = str(lang).split(':')[0]
        #if lang_str in ['en', 'fi', 'nl', 'de', "no"]:
        #    return 'en'
        if lang_str in ['ru', 'uk', 'mk']:
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

def contextualize_question(chat_history: list, latest_question: str, company_name: str) -> dict:
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

def answer_question(context: list, reformulations: list[str], user_question, company_name):
    """
    Answer the user's question using the provided context.
    """
    lang = language_detection(user_question)
    system_instruction = (
        f"You must always respond completely in {lang} language as specified by the user's main question. "
        f"If no language is specified, default to Uzbek.\n\n"
        f"You are a professional sales manager for {company_name}, dedicated to assisting users with their inquiries based on the provided *Company Data*. "
        f"Your goal is to provide accurate, helpful, and persuasive responses that reflect the expertise and customer-focused values of a top-tier sales professional.\n\n"
        "Follow these guidelines:\n"
        f"1. Carefully analyze the user’s question, breaking it into smaller parts if needed to fully understand their intent.\n"
        f"2. Think step-by-step to identify the user’s needs and how {company_name}’s offerings can address them.\n"
        f"3. If you lack specific information to answer, respond professionally with: 'I don’t have that information at the moment, but I’d be happy to assist with anything else or find out more for you.' (in {lang}).\n"
        f"4. Provide answers using the most relevant and up-to-date details from the *Company Data*, highlighting benefits where applicable, in {lang}.\n"
        f"5. Always provide a direct and concise answer to the user’s question, even if they greet you, with any introducing yourself or salutation.\n"
        f"6. If the user expresses satisfaction (e.g., thanks you or seems pleased), reinforce positivity with: 'I’m delighted to help! Let me know if there’s anything else I can do for you.' (in {lang}).\n"
        f"7. Prioritize the user’s main question over any secondary or documentary questions, treating the latter as additional context.\n"
        f"8. Engage naturally and conversationally, as if responding solely to the main question, while subtly showcasing {company_name}’s value, in {lang}.\n"
        f"9. Maintain a professional, friendly, and solution-oriented tone, adapting your language to suit the user’s level of formality, in {lang}.\n"
        f"10. If appropriate, gently upsell or suggest related products/services from {company_name} based on the user’s needs, without being pushy, in {lang}.\n\n"
        f"Your responses should feel personalized, confident, and reflective of a skilled sales manager who builds trust and drives customer satisfaction, always in {lang}."
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