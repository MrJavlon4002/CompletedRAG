import gradio as gr
import uuid
import requests

API_URL = "http://0.0.0.0:8000/ask"

def chatbot_ui(input_text, history, session_id):
    if session_id == "":
        session_id = str(uuid.uuid4())
    
    payload = {
        "session_id": session_id,
        "query": input_text
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            output = response.json().get("answer", "Sorry, I don't know the answer.")
        else:
            output = f"Failed to get a response. Status code: {response.status_code}. Response: {response.text}"
    except requests.RequestException as e:
        output = f"An error occurred: {str(e)}"
    
    history.append((input_text, output))
    return history, history, session_id, ""

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Ask a question")
    session_id = gr.State("")
    clear = gr.Button("Clear")

    msg.submit(chatbot_ui, [msg, chatbot, session_id], [chatbot, chatbot, session_id, msg])
    clear.click(lambda: None, None, chatbot)

demo.launch(share=True)
