from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import io
import os
import pikepdf
from pathlib import Path
app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', status_message="")

@app.route('/decrypt', methods=['POST'])
def decrypt():
    uploaded_file = request.files['file']
    password = request.form.get('password', '')

    if not uploaded_file or not uploaded_file.filename.endswith('.pdf'):
        return render_template('index.html', error_message='Please select a valid PDF file.')

    try:
        pdf = pikepdf.Pdf.open(uploaded_file, password=password)
        decrypted_file = io.BytesIO()
        pdf.save(decrypted_file)
        decrypted_file.seek(0)
        

        # Extract the original filename using secure_filename
        original_filename = secure_filename(uploaded_file.filename)

        return send_file(
                decrypted_file,
                as_attachment=True,
                download_name=f'{Path(uploaded_file.filename).stem}_unlocked.pdf',
                mimetype='application/pdf'
            )
    except pikepdf.PdfError as e:
        error_message = f"Error: {str(e)}"
        return render_template('index.html', error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
