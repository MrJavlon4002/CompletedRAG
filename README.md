# CompletedRAG
CompletedRAG is the project to making a chatbot that can communicate with with user and asnwer the questions about spesific company. Chat bot can provide detailed information about the company and get job applicant's information.
 - Chat bot works with *Qdrant vector database* for chunks of company information.
 - *SQLite* is used for to save chat history
 - On a purpose of storing job applications used store is *CSV file* 

## Installation
### Docker
Installation starts with downloading `Qdrant image` from **Dockerhub**
```bash
docker pull qdrant/qdrant
```
Run the *Docker* service
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```
Active usage of Qdrant service:

 - REST API: localhost:6333
 - Web UI: localhost:6333/dashboard // You can monipulate Vector DB in a dashboard
 - GRPC API: localhost:6334


### Environment
Let's configure the environment for the application.
```bash
python3 -m venv .venv
```
```bash
souurce .venv/bin/aactivate // for Mac and Linux
```
```bash
pip install -r requirements.txt
```

## Usage
Let make an `API` to actual usage of servece.
```bash
python api.py
``` 
To use service of the Projet these cofiguration are important.
 - Request type `http`
 - Request method `POST`
 - Request port `:8000`

 - Request URL `http://0.0.0.0:8000/ask`

Request parameters are should be sent in the `Json` format.
```json
{
    "session_id": "123",
    "query": "Salom"
}
```
Client required to provide both `session_id` and `query` parameter in `str` type to use service.

### Response
Response comes in `json` formaat.
```json
    "answer": "Assalomu alaykuum"
```
`answer` is the response that coming from an application.
### Gradio (optional)
If you want to real experiment of using service, you can use `gradio` for communication with *chatbot*.
```bash
pip install gradio requests
```
Now let's create chtbot with visualisation enabled.
```bash
python app.py
```
Then you can open up the hyperlink system provided (mostly http://127.0.0.1:7860).
