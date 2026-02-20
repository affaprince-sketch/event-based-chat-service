------ Set up instruction ------

1. Assume Python 3.11+ installed. If not please install Python 3.11+ first.

2. Unzip the zip file to local file system

3. Create and activate a virtual environment, go to the mvp_chat folder in CMD
Run the following line in CMD:
    python -m venv .venv
    .\.venv\Scripts\activate.bat

4. Install dependencies
Run the following in CMD (assuming pip is installed):
    pip install -r requirements.txt

5. Running server
Execute run.bat
Or Run directly with uvicorn
    uvicorn app:app --host 0.0.0.0 --port 8000

6. Once running, the server will be available at:
    http://localhost:8000

7. Using the simple_client.py (CLI client)
In a new CMD terminal (with venv activated):
    python client_example.py john default

Multiple clients can be run at once using different usernames.

8. Or Send direct REST API request, for example:
    POST http://localhost:8000/messages
    Content-Type: application/json
    {
        "user": "john",
        "room": "default",
        "text": "hello"
    }


9. More details about the implementation are in file: "Implementation notes.txt"