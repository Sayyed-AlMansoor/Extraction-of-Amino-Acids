from flask import Flask, request, render_template, send_file
import os
from werkzeug.utils import secure_filename
from ml_script import process_papers, get_truetables, save_tables_to_excel, filter_dataframes

app = Flask(__name__)

# Set upload and processed folder paths
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed_files'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Render the main page for uploading files."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Handle file uploads, processing, and extraction."""
    # Clear the uploads folder before saving new files
    for old_file in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], old_file))

    # Check for uploaded files
    if 'files' not in request.files:
        return "No file part in the request", 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return "No file selected", 400

    for file in files:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    # Process the uploaded files
    folder_path = app.config['UPLOAD_FOLDER']
    output_excel_path = os.path.join(app.config['PROCESSED_FOLDER'], 'Extracted_Tables.xlsx')
    filtered_excel_path = os.path.join(app.config['PROCESSED_FOLDER'], 'Filtered_Tables.xlsx')

    # Extract and process tables
    text, tables = process_papers(folder_path)
    true_tables, all_tables = get_truetables(tables)
    filtered_tables = filter_dataframes(all_tables)
    
    # Save results to Excel
    save_tables_to_excel(filtered_tables, filtered_excel_path)

    # Provide the download link
    return render_template('result.html', download_link='/download')

@app.route('/download', methods=['GET'])
def download():
    """Provide the filtered Excel file for download."""
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], 'Filtered_Tables.xlsx')
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
