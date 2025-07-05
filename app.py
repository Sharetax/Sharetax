from flask import Flask, render_template, request, send_file
import os
import pdfplumber
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['pdf_file']
    if file.filename == '':
        return "No file selected"

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    tables = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                tables.append(df)

    if tables:
        result_df = pd.concat(tables, ignore_index=True)
    else:
        return "No tables found in the PDF."

    output_path = os.path.join(OUTPUT_FOLDER, filename.replace('.pdf', '.xlsx'))
    result_df.to_excel(output_path, index=False)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
