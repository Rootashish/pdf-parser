import pdfplumber
import re
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

# Regex patterns for email and phone numbers
email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}'

@app.route("/")
def home():
    return "Welcome to the PDF Parser API! Use the /upload endpoint to upload a PDF."

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text

def parse_details(text):
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    
    # Extract names (assumed before email occurrences)
    lines = text.split("\n")
    names = []

    for line in lines:
        if any(email in line for email in emails):
            names.append(line.split(email)[0].strip())  # Extract name before email

    phones = ["".join(phone) for phone in phones]
    return list(zip(names, emails, phones))

@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    pdf_file = request.files["file"]
    pdf_path = f"./{pdf_file.filename}"
    pdf_file.save(pdf_path)

    text = extract_text_from_pdf(pdf_path)
    data = parse_details(text)

    df = pd.DataFrame(data, columns=["Name", "Email", "Phone"])
    df.to_csv("extracted_data.csv", index=False)  

    return jsonify({"message": "File processed", "data": data})

if __name__ == "__main__":
    app.run(debug=True)
