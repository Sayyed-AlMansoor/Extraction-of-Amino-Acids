import pdfplumber
import pandas as pd
import numpy as np
import scipy as sp
import camelot
import re
#import spacy
import os
import csv
from openpyxl import load_workbook

# Phase 1 : Processing research papers
# Helper function to process research papers (pdf formats) from a folder
def process_papers(folder_path):
    all_text = ""
    all_tables = []
    
    # Opening all files in the folder
    for filename in os.listdir(folder_path): 
        if filename.endswith(".pdf"):
            # Getting the full path of the file
            pdf_path = os.path.join(folder_path, filename)
            # Extract text and tables
            text, tables = extract_text_and_tables(pdf_path)
            all_text += text
            all_tables.extend(tables)  # Append tables to the global list

    return all_text, all_tables
# Function to extract text and tables from a page
def extract_text_and_tables(pdf_path):
    text = ""
    tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Ext ract text from the page
            text += page.extract_text() or ''  # In case text is None
            
        # Extract tables from all pages using Camelot
        # Set pages='all' to extract from all pages at once
        extracted_tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream', strip_text=" .\n")
        tables.extend(extracted_tables)
    
    return text, tables
# To clean the extracted tables from having the rows which contain string values as data
def clean_extracted_tables(extracted_tables):
    cleaned_tables = []  # To store cleaned tables

    for table in extracted_tables:
        table_start = table['table_start']
        header = table['header']
        rows = table['rows']
        cleaned_rows = []

        for row in rows:
            # Exclude the first column and check if all other values are numeric
            if all(isinstance(val, (int, float)) or val is None for val in row[1:]): 
                cleaned_rows.append(row)

        # Append the cleaned table to the result
        cleaned_tables.append({"table_start": table_start, "header": header, "rows": cleaned_rows})

    return cleaned_tables
# Function to print all tables including scrap
def get_alltables(tables):
    all_tables = []
    for i, table in enumerate(tables):    
        first_row = table.df.iloc[0]
        first_row_str = first_row.to_string(index=False)
        all_tables.append(table.df) # Collecting all the tables
        
    return all_tables  # Return the list of true tables
# Function to save the true tables to Excel
def save_tables_to_excel(tables, output_excel_path):
    with pd.ExcelWriter(output_excel_path) as writer:
        for i, table in enumerate(tables):
            # Save each table to a separate sheet in the Excel file
            sheet_name = f"Table_{i + 1}"
            table.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"\nTables saved to Excel file at: {output_excel_path}")
# Assigning the folder paths
folder_path = "D:\\3 SEM UWIN\\INTERNSHIP SHAFAQ\\Project\\Papers"
output_excel_path = "D:\\3 SEM UWIN\\INTERNSHIP SHAFAQ\\Project\\processed_files\\Extracted_All_Tables.xlsx"  # Path for Excel output
# Process papers and extract data
text, tables = process_papers(folder_path)
# Getting the Tabular Data
all_tables = get_alltables(tables)
# Saving all the tables to an Excel file
save_tables_to_excel(all_tables, output_excel_path)
# Function to filter amino acid tables using text density mask
def filter_dataframes(dataframes):
    filtered_dataframes = []
    
    for df in dataframes:
        # Condition 1: Check if the DataFrame has more than 3 columns
        if df.shape[1] <= 3:
            continue
        
        # Condition 2: Check if 70% or more rows contain at least one cell with >20 characters
        long_text_rows = df.applymap(lambda x: len(str(x)) > 20 if pd.notnull(x) else False).any(axis=1)
        if long_text_rows.sum() >= len(df) * 0.7:
            continue
        
        # If the DataFrame passes both conditions, add it to the result
        filtered_dataframes.append(df)
    
    return filtered_dataframes
# Getting the true tables by filtering all the tables using text density mask
true_dfs = filter_dataframes(all_tables)
# Saving the filtered tables to an excel sheet
check_excel_path = "D:\\3 SEM UWIN\\INTERNSHIP SHAFAQ\\Project\\processed_files\\Extracted_Tables_Camelot.xlsx"  # Path for Excel output
save_tables_to_excel(true_dfs, check_excel_path)
# Amino acid identifier lists

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
    
print(amino_acid_mapping)
# Combine all identifiers for matching
amino_acid_identifiers = set(amino_acid_symbols + amino_acid_shortforms + amino_acid_shortforms_uc + [name.upper() for name in amino_acid_full_names])
# Function to identify the header row
def identify_header(data_frame):
    for index, row in data_frame.iterrows():
        row_values = [str(cell).strip().upper() for cell in row if isinstance(cell, str)]  # Normalize row values
        match_count = sum(value in amino_acid_identifiers for value in row_values)
        if match_count > 5:  # Identify header if more than 5 matches
            # print(f"Header identified at row {index}: {row_values}")
            return index, row_values
    # print("No valid header found.")
    return None, None
# Function to remove rows before the header
def remove_rows_before_header(data_frame):
    header_index, header_row = identify_header(data_frame)
    if header_index is not None:
        # Slice the DataFrame to start from the header
        modified_data_frame = data_frame.iloc[header_index:].reset_index(drop=True)
        return modified_data_frame
    else:
        # print("No valid header found. Returning the original DataFrame.")
        return data_frame
# Function to remove rows starting from the first row with non-numeric value in the last column (excluding header)
def remove_invalid_rows_after_header(data_frame):
    for index, row in data_frame.iloc[1:].iterrows():  # Exclude header row from the check
        last_value = row.iloc[-1]  # Get the last column value
        try:
            float(last_value)  # Check if it's convertible to a float
        except (ValueError, TypeError):
            # print(f"Invalid row found at index {index}, removing all rows after this point.")
            return data_frame.iloc[:index].reset_index(drop=True)
    return data_frame
# Function to process values in rows after the header
def process_values_in_rows(data_frame):
    header_row = data_frame.iloc[0]  # Header row
    rows = data_frame.iloc[1:]  # Exclude the header row

    for index, row in rows.iterrows():
        for col in data_frame.columns[1:]:  # Skip the "Name" column
            try:
                value = float(row[col])  # Convert to float if possible
                if value > 20:
                    data_frame.at[index, col] = value / 100  # Divide by 100
            except (ValueError, TypeError):
                pass  # Ignore non-numeric or invalid values
    return data_frame
# Process the DataFrames
modified_dfs = []
for df in true_dfs:
    modified_data_frame = remove_rows_before_header(df)  # Remove rows before the header
    modified_data_frame = remove_invalid_rows_after_header(modified_data_frame)  # Remove invalid rows after header
    modified_data_frame = process_values_in_rows(modified_data_frame) # Modify large values
    modified_dfs.append(modified_data_frame) # Get modified dfs into a list
# Function to process multiple DataFrames into a single Excel sheet
def process_multiple_dataframes(dfs, header_index):
    # Initialize the Excel sheet with required columns
    sheet_columns = ["Name"] + list(amino_acid_mapping.values())
    final_df = pd.DataFrame(columns=sheet_columns)

    for data_frame in dfs:
        # Extract header and rows
        header_row = data_frame.iloc[header_index]
        rows = data_frame.iloc[header_index + 1:]
             
        # Map each header to its corresponding short form in the final sheet
        header_map = {}
        for col in header_row:
            col_upper = str(col).strip().upper()  # Use uppercase for comparison
            if col_upper in reverse_mapping:  # Map to the short form
                header_map[col] = reverse_mapping[col_upper]
             
        # Process each row in the current DataFrame
        for _, row in rows.iterrows():
            row_values = row.tolist()
            new_row = {col: None for col in sheet_columns}  # Initialize new row
            new_row["Name"] = row_values[0]  # Assign the "Name" column

            for value, col_name in zip(row_values[1:], header_row[1:]):
                col_name_upper = str(col_name).strip().upper()
                if col_name in header_map:  # Map column name to short form
                    mapped_column = header_map[col_name]
                    new_row[mapped_column] = value  # Directly assign the value

            # Append new_row as a DataFrame and use pd.concat
            new_row_df = pd.DataFrame([new_row])
            final_df = pd.concat([final_df, new_row_df], ignore_index=True)
    
    return final_df
# Extracting the amino acid data using camelot
final_df_cm = process_multiple_dataframes(modified_dfs, 0)
# Save the final DataFrame to an Excel file
output_path = "D:\\3 SEM UWIN\\INTERNSHIP SHAFAQ\\Project\\processed_files\\Extracted_Amino_Acids_Camelot.xlsx"
final_df_cm.to_excel(output_path, index=False)
print(f"Excel file created successfully: {output_path}")
# To process tables using REGEX pattern matcher and find table start lines
def process_text_for_tables(text):
    lines = text.strip().split("\n")  # Split text into lines
    table_start_pattern = re.compile(r"(?i)^table\s*[-:\s]\s*\d+")  # Pattern to match table starts
    extracted_tables = []  # To store the extracted tables

    i = 0
    while i < len(lines):
        line = lines[i]
        if table_start_pattern.match(line):  # Table start
            table_data = {"table_start": line, "header": [], "rows": []}  # Include table_start
            header = find_header(lines[i + 1:], table_start_pattern)  # Find header
            if header:
                if "Name" not in header:  # Ensure the header starts with "Name"
                    header.insert(0, "Name")
                table_data["header"] = header
                rows = process_table(lines[i + 2:], header, table_start_pattern)  # Get rows
                table_data["rows"] = rows
                extracted_tables.append(table_data)
            i += 1
        else:
            i += 1
    return extracted_tables
# To find headers for those regex tables
def find_header(lines, table_start_pattern):
    for line in lines:
        if table_start_pattern.match(line):  # New table start, stop looking
            return None
        columns = line.split()
        if len(columns) < 5:  # Skip lines with fewer than 5 columns
            continue
        processed_columns = []
        i = 0
        while i < len(columns):
            if columns[i] == "+":
                if i > 0 and i < len(columns) - 1:
                    merged_col = columns[i - 1] + "+" + columns[i + 1]
                    processed_columns.pop()
                    processed_columns.append(merged_col)
                    i += 1
                else:
                    processed_columns.append(columns[i])
            else:
                processed_columns.append(columns[i])
            i += 1
        if sum(col.upper() in amino_acid_symbols or col.upper() in amino_acid_shortforms_uc for col in processed_columns) >= 5:
            return processed_columns
    return None
# To process further lines and allocate rows to corresponding tables
def process_table(lines, header, table_start_pattern):
    rows = []
    for line in lines:  # Traverse rows until new table start or invalid row
        if table_start_pattern.match(line):  # Stop on encountering a new table
            break
        columns = line.split()
        if not columns or not re.match(r"^\d+(\.\d+)?$", columns[-1]):  # Stop if no float at end
            continue

        row = [None] * len(header)  # Initialize row with None
        name_parts = []
        header_index = len(header) - 1

        for col in reversed(columns):  # Traverse the row in reverse
            if header_index > 0:  # Assign values to columns other than "Name"
                row[header_index] = float(col) if re.match(r"^\d+(\.\d+)?$", col) else col
                header_index -= 1
            else:  # Remaining values are part of the name
                name_parts.insert(0, col)

        row[0] = " ".join(name_parts)  # Combine remaining parts into the "Name" column
        rows.append(row)

    return rows
# Using REGEX pattern matcher for any missed out tables in camelot extraction

# Process the text
extracted_tables = process_text_for_tables(text)
# print(extracted_tables)
# Clean the extracted tables
extracted_tables = clean_extracted_tables(extracted_tables)
# print(extracted_tables)
# Write to Excel with separate sheets
output_path_regex = "D:\\3 SEM UWIN\\INTERNSHIP SHAFAQ\\Project\\processed_files\\Extracted_Tables_Regex.xlsx"
with pd.ExcelWriter(output_path_regex, engine="openpyxl") as writer:
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

print(f"Excel file created successfully: {output_path_regex}")
# Write to Excel with separate sheets
output_path_regex = "D:\\3 SEM UWIN\\INTERNSHIP SHAFAQ\\Project\\processed_files\\Extracted_Tables.xlsx"
with pd.ExcelWriter(output_path_regex, engine="openpyxl") as writer:
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
        
print(f"Excel file created successfully: {output_path_regex}")
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
# Save the final extracted Amino acid values to an Excel file
output_path = "D:\\3 SEM UWIN\\INTERNSHIP SHAFAQ\\Project\\processed_files\\Extracted_Amino_Acids_Regex.xlsx"
final_df.to_excel(output_path, index=False)
print(f"Excel file created successfully: {output_path}")
output_path = "D:\\3 SEM UWIN\\INTERNSHIP SHAFAQ\\Project\\processed_files\\Extracted_Amino_Acids.xlsx"

combined_df = pd.concat([final_df_cm, final_df], ignore_index=True)
combined_df.to_excel(output_path, index=False)

print(f"Excel file created successfully: {output_path}")
