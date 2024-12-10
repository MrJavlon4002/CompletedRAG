import gradio as gr
import uuid
import requests

API_URL = "http://0.0.0.0:8000/ask"

session_id = str(uuid.uuid4())
print(f"Session ID: {session_id}")

def chatbot_ui(input_text, history):
    """
    Handles user input and returns a response from the API.
    """
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
    return history, ""

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Ask a question")
    clear = gr.Button("Clear")

    msg.submit(chatbot_ui, [msg, chatbot], [chatbot, msg])
    clear.click(lambda: None, None, chatbot)

demo.launch(share=True)
