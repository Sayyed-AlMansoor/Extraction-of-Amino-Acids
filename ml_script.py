import pdfplumber
import pandas as pd
import camelot
import re
import os

# Helper function to process research papers (pdf formats) from a folder
def process_papers(folder_path):
    all_text = ""
    all_tables = []
    
    for filename in os.listdir(folder_path): 
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            text, tables = extract_text_and_tables(pdf_path)
            all_text += text
            all_tables.extend(tables)

    return all_text, all_tables

# Function to extract text and tables from a page
def extract_text_and_tables(pdf_path):
    text = ""
    tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ''
            
        extracted_tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
        tables.extend(extracted_tables)
    
    return text, tables

# Regex filter to identify valid table headers
def filter_actual_tables(text):
    pattern = r'^\s*Table\s+([1-9]\d*)\s*'
    return bool(re.match(pattern, text))

# Function to filter and collect true tables
def get_truetables(tables):
    true_tables = []
    all_tables = []
    for i, table in enumerate(tables):    
        first_row = table.df.iloc[0]
        first_row_str = first_row.to_string(index=False)
        if filter_actual_tables(first_row_str):
            true_tables.append(table.df)
        all_tables.append(table.df)
    return true_tables, all_tables

# Function to filter DataFrames based on custom conditions
def filter_dataframes(dataframes):
    filtered_dataframes = []
    for df in dataframes:
        if df.shape[1] <= 3:
            continue
        long_text_rows = df.applymap(lambda x: len(str(x)) > 20 if pd.notnull(x) else False).any(axis=1)
        if long_text_rows.sum() >= len(df) * 0.5:
            continue
        filtered_dataframes.append(df)
    return filtered_dataframes

# Function to save tables to an Excel file
def save_tables_to_excel(tables, output_excel_path):
    with pd.ExcelWriter(output_excel_path) as writer:
        for i, table in enumerate(tables):
            sheet_name = f"Table_{i + 1}"
            table.to_excel(writer, sheet_name=sheet_name, index=False)
