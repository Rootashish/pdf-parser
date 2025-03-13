import pdfplumber
import re
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Regex patterns for emails & phone numbers
email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}'

@app.route("/")
def index():
    return render_template("index.html")

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text(x_tolerance=2, y_tolerance=2)  # Improved accuracy
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
        for email in emails:
            if email in line:
                names.append(line.split(email)[0].strip())  # Extract name before email

    phones = ["".join(phone) for phone in phones]  # Clean phone number formatting
    return list(zip(names, emails, phones))

@app.route("/upload", methods=["POST"])
def upload_pdfs():
    if "files" not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist("files")  # Get multiple files
    all_data = []

    for pdf_file in files:
        pdf_path = f"./{pdf_file.filename}"
        pdf_file.save(pdf_path)

        text = extract_text_from_pdf(pdf_path)
        data = parse_details(text)
        all_data.extend(data)  # Append all extracted data

    return jsonify({"message": "Files processed", "data": all_data})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render assigns a dynamic port
    app.run(host="0.0.0.0", port=port)
