import io
from pathlib import Path
import os
from flask import Flask, render_template, request, send_file
import PyPDF2, pikepdf

app = Flask(__name__, template_folder="Templates")

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encrypt_pdf(input_path, password):
    with open(input_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        pdf_writer = PyPDF2.PdfWriter()

        for page_num in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        pdf_writer.encrypt(password)

        encrypted_file = io.BytesIO()
        pdf_writer.write(encrypted_file)
        encrypted_file.seek(0)

        return encrypted_file

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
        # Decrypt the PDF
        pdf = pikepdf.Pdf.open(uploaded_file, password=password)
        decrypted_file = io.BytesIO()
        pdf.save(decrypted_file)
        decrypted_file.seek(0)

        return send_file(
            decrypted_file,
            as_attachment=True,
            download_name=f'{Path(uploaded_file.filename).stem}_unlocked.pdf',
            mimetype='application/pdf'
        )
    except pikepdf.PdfError as e:
        error_message = f"Error: {str(e)}"
        return render_template('index.html', error_message=error_message)

@app.route('/encrypt', methods=['POST'])
def encrypt():
    uploaded_file = request.files['file']
    password = request.form.get('password', '')

    if not uploaded_file or not allowed_file(uploaded_file.filename):
        return render_template('index.html', error_message='Please select a valid PDF file.')

    # Specify the directory for temporary files
    temp_dir = 'temp'

    # Ensure the temporary directory exists
    os.makedirs(temp_dir, exist_ok=True)

    input_path = os.path.join(temp_dir, 'input.pdf')

    try:
        # Save the uploaded file temporarily
        uploaded_file.save(input_path)

        # Encrypt the PDF
        encrypted_file = encrypt_pdf(input_path, password)

        # Send the encrypted PDF as a downloadable file
        return send_file(
            encrypted_file,
            as_attachment=True,
            download_name=f'{Path(uploaded_file.filename).stem}_encrypted.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return render_template('index.html', error_message=error_message)
    finally:
        # Clean up temporary files
        if os.path.exists(input_path):
            os.remove(input_path)

if __name__ == '__main__':
    app.run(debug=True)
