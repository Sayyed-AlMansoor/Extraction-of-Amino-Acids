from flask import Flask, request, render_template, send_file
import os
from werkzeug.utils import secure_filename
from ml_script import process_papers, save_tables_to_excel, filter_dataframes, clean_extracted_tables, get_alltables, identify_header, remove_rows_before_header, remove_invalid_rows_after_header, process_values_in_rows, process_multiple_dataframes, process_text_for_tables, find_header, process_table

import pdfplumber
import pandas as pd
import numpy as np
import camelot
import re
#import spacy
import os
import csv
from openpyxl import load_workbook


# Amino acid symbols
amino_acid_symbols = ["A", "R", "N", "D", "C", "E", "Q", "G", "H", "I", "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V"]

# Amino acid shortforms
amino_acid_shortforms = ["Ala", "Arg", "Asn", "Asp", "Cys", "Glu", "Gln", "Gly", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Pro", "Ser", "Thr", "Trp", "Tyr", "Val"]

# Amino acid names
amino_acid_names = [
    "Alanine", "Arginine", "Asparagine", "Aspartic acid", "Cysteine",
    "Glutamic acid", "Glutamine", "Glycine", "Histidine", "Isoleucine",
    "Leucine", "Lysine", "Methionine", "Phenylalanine", "Proline", "Serine",
    "Threonine", "Tryptophan", "Tyrosine", "Valine"
]

# Amino acid short forms in Upper Case
amino_acid_shortforms_uc = [
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLU", "GLN", "GLY", "HIS",
    "ILE", "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL"
]

# Amino acid names in Upper Case
amino_acid_names_uc = [
    "ALANINE", "ARGININE", "ASPARAGINE", "ASPARTIC ACID", "CYSTEINE",
    "GLUTAMIC ACID", "GLUTAMINE", "GLYCINE", "HISTIDINE", "ISOLEUCINE",
    "LEUCINE", "LYSINE", "METHIONINE", "PHENYLALANINE", "PROLINE", "SERINE",
    "THREONINE", "TRYPTOPHAN", "TYROSINE", "VALINE"
]
# Amino acid identifier mappings (short form, full name)
amino_acid_mapping = {
    "A": "ALA",
    "R": "ARG",
    "N": "ASN",
    "D": "ASP",
    "C": "CYS",
    "E": "GLU",
    "Q": "GLN",
    "G": "GLY",
    "H": "HIS",
    "I": "ILE",
    "L": "LEU",
    "K": "LYS",
    "M": "MET",
    "F": "PHE",
    "P": "PRO",
    "S": "SER",
    "T": "THR",
    "W": "TRP",
    "Y": "TYR",
    "V": "VAL",
}

# Reverse mapping for short forms and full names
amino_acid_full_names = {
    "ALA": "Alanine",
    "ARG": "Arginine",
    "ASN": "Asparagine",
    "ASP": "Aspartic acid",
    "CYS": "Cysteine",
    "GLU": "Glutamic acid",
    "GLN": "Glutamine",
    "GLY": "Glycine",
    "HIS": "Histidine",
    "ILE": "Isoleucine",
    "LEU": "Leucine",
    "LYS": "Lysine",
    "MET": "Methionine",
    "PHE": "Phenylalanine",
    "PRO": "Proline",
    "SER": "Serine",
    "THR": "Threonine",
    "TRP": "Tryptophan",
    "TYR": "Tyrosine",
    "VAL": "Valine",
}

reverse_mapping = {}
for short, full in amino_acid_full_names.items():
    reverse_mapping[short.upper()] = short
    reverse_mapping[full.upper()] = short
    
# print(amino_acid_mapping)
# Combine all identifiers for matching
amino_acid_identifiers = set(amino_acid_symbols + amino_acid_shortforms + amino_acid_shortforms_uc + [name.upper() for name in amino_acid_full_names])



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
    output_table_path = os.path.join(app.config['PROCESSED_FOLDER'], 'Extracted_Tables.xlsx')
    output_data_path = os.path.join(app.config['PROCESSED_FOLDER'], 'Extracted_Data.xlsx')

    # Process papers
    text, tables = process_papers(folder_path)
    all_tables = get_alltables(tables)
    true_dfs = filter_dataframes(all_tables)


    modified_dfs = []
    for df in true_dfs:
        modified_data_frame = remove_rows_before_header(df)  # Remove rows before the header
        modified_data_frame = remove_invalid_rows_after_header(modified_data_frame)  # Remove invalid rows after header
        modified_data_frame = process_values_in_rows(modified_data_frame) # Modify large values
        modified_dfs.append(modified_data_frame) # Get modified dfs into a list
    
    final_df_cm = process_multiple_dataframes(modified_dfs, 0)

    extracted_tables = process_text_for_tables(text)

    extracted_tables = clean_extracted_tables(extracted_tables)

    with pd.ExcelWriter(output_table_path, engine="openpyxl") as writer:
        for i, table in enumerate(extracted_tables):
            sheet_name = f"Table {i+1}"

            # Create DataFrame for the table start line
            table_start_line_df = pd.DataFrame([[table["table_start"]]], columns=["Table Start Line"])

            # Create DataFrame for headers and rows
            table_data_df = pd.DataFrame(table["rows"], columns=table["header"])

            # Write the table start line
            table_start_line_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False, startrow=0)

            # Write the headers and rows below the table start line
            table_data_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2)

        temp = i+1
        for j, df in enumerate(true_dfs):
            sheet_name = f"Table {temp+j+1}"
            df.to_excel(writer, sheet_name=sheet_name, index=False)


    # Initialize the DataFrame with required columns
    sheet_columns = ["Name"] + list(amino_acid_mapping.values())
    final_df = pd.DataFrame(columns=sheet_columns)
    # Process each extracted table
    for table in extracted_tables:
        header = table["header"]
        rows = table["rows"]

        # Map each header to its corresponding short form in the final sheet
        header_map = {}
        for col in header:
            col_upper = col.upper()  # Use uppercase for comparison
            if col_upper in reverse_mapping:  # Map to the short form
                header_map[col] = reverse_mapping[col_upper]

        for row in rows:
            # Initialize a new row with NaN for non-matching headers
            new_row = {col: None for col in sheet_columns}
            new_row["Name"] = row[0]

            for header_name, value in zip(header, row):
                if header_name in header_map:  # Map header to its short form
                    mapped_column = header_map[header_name]
                    new_row[mapped_column] = value

            # Append new_row as a DataFrame and use pd.concat
            new_row_df = pd.DataFrame([new_row])
            final_df = pd.concat([final_df, new_row_df], ignore_index=True)
    
    combined_df = pd.concat([final_df_cm, final_df], ignore_index=True)
    combined_df.to_excel(output_data_path, index=False)

    return render_template('result.html', download_link='/download')

@app.route('/download', methods=['GET'])
def download():
    """Provide the final combined Excel file for download."""
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], 'Extracted_Data.xlsx')
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
