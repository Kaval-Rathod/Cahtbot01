from flask import Flask, request, jsonify, render_template
from document_parser import parse_document
import groq
import requests
import os

app = Flask(__name__)

# Initialize Groq client
client = groq.Groq(api_key="...")

# Define your LLaMA API endpoint and key
LLAMA_API_URL = "https://api.llama.com/summarize"
LLAMA_API_KEY = "your_llama_api_key"

# Function to save unresolved queries
def save_unresolved_query(query, response, file_path="query_to_solve.txt"):
    try:
        with open(file_path, 'a') as file:
            file.write(f"Query: {query}\n")
            file.write(f"Response: {response}\n")
            file.write("Resolution Status: Unresolved\n")
            file.write("\n")
        return "Your question has been sent to the higher authorities; it will be solved as soon as possible."
    except Exception as e:
        return f"An error occurred while saving your query. Please try again later."

# Function to resolve a query
def resolve_query(query, resolution, file_path="query_to_solve.txt"):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        with open(file_path, 'w') as file:
            skip = False
            for line in lines:
                if line.strip() == f"Query: {query}":
                    skip = True
                elif skip and line.strip() == "Resolution Status: Unresolved":
                    file.write(f"Query: {query}\n")
                    file.write(f"Resolution: {resolution}\n")
                    file.write("Resolution Status: Resolved\n")
                    skip = False
                else:
                    file.write(line)
        return "The query has been resolved."
    except Exception as e:
        return f"An error occurred while resolving the query. Please try again later."

# Function to get a chatbot response
def chatbot_response(document_text, query):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": document_text + "\n\n" + query}
            ],
            model="llama3-8b-8192",
            temperature=0.7,
            max_tokens=5000,
            top_p=1,
            stop=None
        )
        response_text = response.choices[0].message.content.strip()
        if "I don't know" in response_text or response_text == "" or "no mention of" in response_text:
            return save_unresolved_query(query, response_text)
        return response_text
    except Exception as e:
        return save_unresolved_query(query, f"An error occurred: {e}")

# Function to summarize a file using LLaMA
def summarize_file(filepath):
    try:
        document_text = parse_document(filepath)
        headers = {
            "Authorization": f"Bearer {LLAMA_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {"text": document_text}
        response = requests.post(LLAMA_API_URL, headers=headers, json=data)
        response.raise_for_status()
        summary = response.json().get('summary', 'No summary available.')
        return summary
    except Exception as e:
        return "An error occurred while summarizing the file."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        document_text = parse_document(file_path)
        query = request.form.get('query', '')
        response = chatbot_response(document_text, query)
        return jsonify({"response": response})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        summary = summarize_file(file_path)
        return jsonify({"summary": summary})

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
