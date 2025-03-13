import openai
from django.conf import settings
from langdetect import detect_langs

openai.api_key = settings.OPENAI_API_KEY
openai_model = "gpt-4o"

def language_detection(query: str) -> str:
    """
    Detect language of input text and return standardized language code.
    Returns 'en' for English and similar languages,
    'ru' for Russian, and 'uz' as default.
    """
    lang_list = detect_langs(query)

    for lang in lang_list[:1]:
        lang_str = str(lang).split(':')[0]
        lang_num = float(str(lang).split(':')[1])
        #if lang_str in ['en', 'fi']:
        #    return 'en'
        if (lang_str in ['ru'] and lang_num > 0.80) or (lang_str in ['mk'] and lang_num > 0.80): 
            return 'ru'
    return 'uz'

def call_openai_with_functions(model_name: str, messages: str, api_key: str, system_instruction: str) -> list[str]:
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
        return ["Error occurred"]

def contextualize_question(chat_history: list, latest_question: str, company_name: str) -> dict:
    chat_history = chat_history[-3:] if len(chat_history) > 3 else chat_history
    result = {}
    system_instruction = (
        f"Your role is to reformulate user requests with precision for a sales assistant bot at {company_name}, adapting them based on their clarity and relevance, in the exact language of the *Latest question*. All reformulations must be phrased as questions, text, or requests from the user to the assistant bot. Follow these steps:\n\n"
        "1. **General Conversational Questions**:\n"
        "   - If the *Latest question* is a greeting, casual remark, or general conversation (e.g., 'Hi there', 'How you doing?', 'Nice day'), do not broaden it; instead, output **1 grammatically corrected version** of the original text as a user request to the bot, without tying it to {company_name}.\n"
        "   - Example: 'Hi' becomes 'Hi!' (in the *Latest question*’s language).\n"
        "   - Example: 'How you doing?' becomes 'How are you doing?' (in the *Latest question*’s language).\n"
        "   - Example: 'nice day' becomes 'Isn’t it a nice day?' (in the *Latest question*’s language).\n\n"
        "2. **Abstract or Unrelated Questions**:\n"
        "   - If the *Latest question* is vague, abstract, or unrelated to {company_name} (e.g., 'What’s this?' or 'How does it work?'), reformulate it into **1 broader, grammatically correct question or request** to the bot, without forcing a connection to {company_name}.\n"
        "   - Example: 'What’s this?' becomes 'What can you explain to me?' (in the *Latest question*’s language).\n"
        "   - Example: 'How does it work?' becomes 'How do things operate here?' (in the *Latest question*’s language).\n\n"
        "3. **Relevant but Imprecise Questions About {company_name}**:\n"
        "   - If the *Latest question* is somewhat clear and related to {company_name} but can be sharpened, create **2 distinct reformulations** in the language of the *Latest question*, phrased as user questions or requests to the bot, to make it more precise and actionable, explicitly tying it to {company_name}.\n"
        "   - Focus each on a different aspect (e.g., price vs. features), using chat history for context.\n"
        f"   - Example: 'Is Excel good?' becomes:\n"
        f"     - 'Is {company_name}’s Excel course worth trying?'\n"
        f"     - 'What does {company_name}’s Excel course teach me?'\n\n"
        "Rules:\n"
        "- Output only reformulated questions, text, or requests in the exact language of the *Latest question*—no answers, explanations, or bot responses.\n"
        "- Default to Uzbek if the *Latest question*’s language is unclear or mixed.\n"
        "- Keep phrasing natural, concise, and specific, as if the user is addressing a sales assistant bot.\n"
        "- Use chat history to avoid course mix-ups and maintain relevance for company-related questions.\n"
        "- Do not offer language courses—focus on Excel, Figma, Marketing, etc., for company-related cases.\n"
        "- For general conversational questions, correct grammar only without broadening or tying to {company_name}; for abstract/unrelated questions, broaden and correct grammar without {company_name}; for relevant questions about {company_name}, refine with a clear {company_name} connection.\n"
    )

    messages = f"Chat history: {chat_history}\nLatest question: {latest_question}"
    result["text"] = list(call_openai_with_functions(
        model_name=openai_model,
        messages=messages,
        api_key=settings.OPENAI_API_KEY,
        system_instruction=system_instruction
    ))

    result["lang"] = language_detection(query=result["text"][0])
    
    return result

def answer_question(context: list, reformulations: list[str], user_question: str, company_name: str, chat_history: list):
    chat_history = chat_history[-3:] if len(chat_history) > 3 else chat_history

    lang = language_detection(query=reformulations[0])
    system_instruction = f"""
You are a professional sales manager for {company_name}, assisting users primarily in {lang}. If {lang} is undefined or invalid, use the exact language of the *Main question*. Default to Uzbek if both {lang} and the *Main question*'s language are unclear. Your role is to assist with product details, pricing, availability, and sales-related queries, delivering warm, concise, human-like responses with a friendly vibe.

The current date is **March 06, 2025**. Your knowledge is continuously updated.

#### Response Guidelines
1. **Interaction Steps**:
   - **Greeting**: Use a short, warm greeting (e.g., "Hey! Great question—happy to help!") *only if the user greets first*. Otherwise, jump into the answer with a friendly tone.
   - **Inquiry**: Let the customer ask naturally.
   - **Information Gathering**: Ask casually for details if needed (e.g., "Which course are you into?").
   - **Career Guidance**: If user seems uncertain about course choice or career direction, suggest skill testing at https://osnovaedu.uz/kasbga-yonaltirish
   - **Response Preparation**: 
     - Pull specs, pricing, and availability from *Company Data* in {lang}.
     - If unclear, ask briefly (e.g., "Which one's on your mind?").
     - Redirect off-topic questions nicely (e.g., "Let's chat about our stuff—what's up?").
     - Use kind and friendly imojies.
   - **Presenting Information**: Start with a catchy, human-like intro, then share key details concisely using light symbols (e.g., 📌, 🔹, →) instead of lists. Add a touch of excitement and a raw URL.
   - **Closing**: End with a quick, upbeat note and emoji (e.g., "Ready to start? Let me know! 🚀").

2. **Structure**:
   - Keep it short and flowing—start with a friendly hook, add a compact details block with symbols, and wrap up naturally. No numbered lists unless asked.

3. **Answer Logic**:
   - Use the user's question and history to tailor the reply.
   - Answer from *Company Data* in {lang}, embedding raw URLs (e.g., "See more at https://example.com").
   - For uncertain users, recommend skill testing before course selection.
   - Focus on courses like Excel, Figma, Marketing (no language courses unless specified).

4. **Special Cases**:
   - **Career Uncertainty**: "Not sure which path to take? Try our skill test at https://osnovaedu.uz/kasbga-yonaltirish"
   - **Unknown Info**: "Not sure on pricing yet—what course are you curious about?"
   - **Free Courses/Products**: "No free ones, but we've got intros—want details?"
   - **No Language Courses**: "No language stuff, but Excel, Figma, and more—interested?"
   - **Registration Issues**: "No forms—just hit me up or check https://contactlink.com. What's next?"
   - **Death Penalty Questions**: "Can't go there—let's talk courses instead!"

#### Tone
- Warm, concise, and chatty—like a friendly nudge.
- Add a sprinkle of excitement with emojis (e.g., 🚀, 📌).
- Keep it short and fresh.

#### Output Format
- Catchy intro, brief details with symbols, and a lively close with a URL.
- Example: "Master cool skills with us! 📌 Details: 🔹 5 lessons, 🔹 500k sum—join at https://example.com! 🚀" (or with greeting: "Salom! Master cool skills...").
"""
    print(f"Main question: {user_question}\nDocumentary questions: {reformulations}\n Language: {lang}")
    messages = f"Company Data: {context}\nDocumentary questions: {reformulations}, Main question: {user_question}, Chat history: {chat_history}."
    
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
        yield "Sorry, something went wrong. Please try again!"
