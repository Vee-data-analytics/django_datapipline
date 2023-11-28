import pandas as pd
import spacy
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import csv  # Import the csv module
import io
import re

def process_and_save_txt_file(txt_file):
    nlp = spacy.load("en_core_web_sm")
    
    start_reading = False  # Initialize start_reading
    data = []  # Initialize data as an empty list
    

    for line in txt_file:
        # Check if the line contains "Designator" to start reading data
        if "Designator" in line.decode('latin1'):
            start_reading = True

        if start_reading:
            data.append(line.strip().decode('latin1'))
    # Recognize entities using spaCy NER
    recognized_entities = []
    for line in data:
        doc = nlp(line)
        entities = [ent.text for ent in doc.ents]
        recognized_entities.append(entities)
    
    # Organize the recognized entities into structured data
    structured_data = []
    for line, entities in zip(data, recognized_entities):
        parts = csv.reader([line], delimiter=' ', quotechar='"', skipinitialspace=True).__next__()  # Change this line
        # Pad entities with empty strings to match the length of parts
        entities += [''] * (len(parts) - len(entities))
        structured_data.append(parts + entities)
    
    # Ensure consistent column count
    max_columns = max(len(row) for row in structured_data)
    structured_data = [row + [''] * (max_columns - len(row)) for row in structured_data]
    
    # Create a DataFrame
    df = pd.DataFrame(structured_data, columns=[f"Col_{i}" for i in range(max_columns)])
    
    # Select relevant columns and rename them
    df = df[['Col_0', 'Col_2', 'Col_4', 'Col_5', 'Col_6']]
    df.columns = ['Designator', 'Layer', 'Center-X', 'Center-Y', 'Rotation']
    df = df.drop(df.index[0])
    # Clean the "Designator" column to handle the issue with single space
    df['Designator'] = df['Designator'].apply(lambda x: re.sub(r'\s(?=[A-Z])', '', x))
    
    # Filter out rows where the "Designator" column contains the string "Comment"
    df = df[~df['Designator'].str.contains('Comment')]
    return df




# Define a function to extract size and voltage information from the 'Description' column
def extract_size_and_voltage(description):
    # Use regular expressions to find size and voltage information
    size_match = re.search(r'\d+(\.\d+)?[^\d]+(\d+(\.\d+)?)?[^\d]+', description)
    voltage_match = re.search(r'\d+(\.\d+)?[^\d]*V', description)
    
    if size_match and voltage_match:
        size = size_match.group(0).strip()
        voltage = voltage_match.group(0).strip()
        return size, voltage
    else:
        return None, None

def extract_size_and_voltage_2(description):
    # Use regular expressions to find size and voltage information
    size_match = re.search(r'(\d{4})', description)  # Match 4-digit size (e.g., 0402)
    voltage_match = re.search(r'(\d+(\.\d+)?V)', description)  # Match voltage (e.g., 6.3V)
    
    if size_match and voltage_match:
        size = size_match.group(0)
        voltage = voltage_match.group(0)
        return size, voltage
    else:
        return None, None




def extract_resistor_component_size(description):
    size_match = re.search(r'\b\d{4}\b', description)  # Match 4-digit size (e.g., 0402 or 0201)
    if size_match:
        return size_match.group(0)
    else:
        return None, None

def extract_and_remove_voltage(value):
    value_without_voltage = re.sub(r'\d+(\.\d+)?[^\d]*V', '', value).strip()
    return value_without_voltage

def fb_in_value_with_blm(row):
    if 'FB' in row['Designator']:
        return row['1st Vendor Part No']
    else:['Value']   

def replace_nh_with_vendor_part(row):
    if 'NH' in row['Value'] or 'UH' in row['Value']:
        return row['1st Vendor Part No']
    else:
        return row['Value']


def process_xlsx_file(input_file):
    # Read the XLSX file
    df = pd.read_excel(input_file, header=None)
    df = df.dropna(how='all')

    header_row = None
    for index, row in df.iterrows():
        if 'Designator' in row.values:
            header_row = index
            break

    if header_row is not None:
        df = pd.read_excel(input_file, header=header_row)
    else:
        # Handle the case where the header row is not found
        print("Header row not found.")
        return

    # Sort the values
    sorted_df = df.sort_values(by='Designator')

    # Split them into rows by ","
    sorted_df['Designator'] = sorted_df['Designator'].str.split(",")
    #sorted_df = sorted_df[~sorted_df['DNF'].str.contains('DNF')]
    sorted_df = sorted_df.explode('Designator')

    # Select the columns you want to keep in the df
    columns_to_keep = ['Designator','DNF','Value', '1st Vendor Part No', 'Component Class', 'Description', 'Footprint']
    sorted_df = sorted_df[columns_to_keep]

    # Filter the df by dropping duplicates
    filtered_df = sorted_df.drop_duplicates('Designator')

    # Capitalize the values in the 'Value' column
    filtered_df['Value'] = filtered_df['Value'].str.upper()

    # Fill NaN values in the 'Value' column with an empty string
    filtered_df['Value'].fillna('', inplace=True)

    # Convert the 'Component Class' column into a string
    filtered_df['Component Class'] = filtered_df['Component Class'].astype(str)

    # Delete the rows if they contain the string 'Mechanical' or 'Electro-mechanical'
    filtered_df = filtered_df[~filtered_df['Component Class'].str.contains('Mechanical')]
    filtered_df = filtered_df[~filtered_df['Component Class'].str.contains('Electro-mechanical')]

    filtered_df = filtered_df[filtered_df['Description'].apply(lambda x: isinstance(x, str))]

    # Filter data for Resistors and return them, then add a hyphen to the 'Size_R' column
    resistor_indices = filtered_df[filtered_df['Description'].str.contains('Chip Resistor', case=False)].index

    filtered_df.loc[resistor_indices, 'Size_R'] = filtered_df.loc[resistor_indices, 'Description'].apply(extract_resistor_component_size)
    filtered_df.loc[resistor_indices, 'Size_R'] = '-' + filtered_df.loc[resistor_indices, 'Size_R']

    # Apply the extraction function to the 'Description' column
    filtered_df['Size_C'], filtered_df['Voltage_M'] = zip(*filtered_df['Description'].apply(extract_size_and_voltage_2))

    # Add a hyphen to the 'Size_C' column
    filtered_df['Size_C'] = '-' + filtered_df['Size_C'] + '-'
    filtered_df['Size_C'] = filtered_df['Size_C'] + filtered_df['Voltage_M']

    # Apply the extraction function to the 'Description' column
    filtered_df['Size'], filtered_df['Voltage'] = zip(*filtered_df['Description'].apply(extract_size_and_voltage))

    # Clean up the 'Size' column
    filtered_df['Size'] = filtered_df['Size'].str.replace(', ', '-')
    filtered_df['Size'] = filtered_df['Size'].str.replace('V C', 'V')
    filtered_df['Size'] = filtered_df['Size'].str.replace('V X', 'V')
    filtered_df['Size_combined'] = filtered_df['Size_R'].fillna('') + filtered_df['Size_C'].fillna('')
    filtered_df = filtered_df[~filtered_df['Designator'].str.contains('Tape', case=False)]
    filtered_df = filtered_df[~filtered_df['Designator'].str.contains('Warn', case=False)]
    filtered_df = filtered_df[~filtered_df['Designator'].str.contains('Overpack Label', case=False)]
    filtered_df = filtered_df[~filtered_df['Designator'].str.contains('Ribbon', case=False)]
    filtered_df = filtered_df[~filtered_df['Designator'].str.contains('Box', case=False)]
    filtered_df = filtered_df[~filtered_df['Designator'].str.contains('Serial', case=False)] 
    filtered_df = filtered_df[~filtered_df['Value'].str.contains('DNF')]
    filtered_df = filtered_df[~filtered_df['DNF'].fillna('').astype(str).str.contains('DNF')]

    # Filter the data through in the value column and strip voltage from the value
    filtered_df['Value'] = filtered_df['Value'].apply(extract_and_remove_voltage)

    # Merge 'Size_combined' and 'Value' columns and fill NaN values with empty strings
    filtered_df['Value'] = filtered_df['Value'].fillna('') + filtered_df['Size_combined'].fillna('')
    filtered_df['Value'] = filtered_df.apply(replace_nh_with_vendor_part, axis=1)

    filtered_df['Value'] = df.apply(lambda row: row['1st Vendor Part No'] if pd.isna(row['Value']) or row['Value'] == '' and 'ANT' in row['Designator'].upper() else row['Value'], axis=1)

    filtered_df['Value'] = filtered_df.apply(lambda row: row['1st Vendor Part No'] if 'FB' in row['Designator'] else row['Value'], axis=1)
    filtered_df['Value'] = filtered_df.apply(lambda row: row['1st Vendor Part No'] if pd.isna(row['Value']) or row['Value'] == '' else row['Value'], axis=1)

    filtered_df['Value'] = filtered_df['Value'].str.replace('_', '-')
    filtered_df['Value'] = filtered_df['Value'].str.replace('/', '-')
    filtered_df['Value'] = filtered_df['Value'].str.replace('220UF', '220UF-6.3V')
    filtered_df['Value'] = filtered_df['Value'].str.split(',').str[0]
    filtered_df['Value'] = filtered_df['Value'].str.split('--').str[0]
    filtered_df['Value'] = filtered_df['Value'].str.split('  ').str[0]
    filtered_df['Value'] = filtered_df['Value'].str.replace(' ', '-')
    filtered_df['Value'] = filtered_df['Value'].str.split('+').str[0]
    filtered_df['Value'] = filtered_df['Value'].str.split('=').str[0]
    filtered_df['Value'] = filtered_df.apply(lambda row: row['1st Vendor Part No'] if pd.isna(row['Value']) or row['Value'] == '' else row['Value'], axis=1)
    filtered_df.drop(columns=['Size_combined'], inplace=True)
    columns_to_keep = ['Designator', 'Value']
    filtered_df['Value'] = filtered_df['Value'].str.split('--').str[0]
    filtered_df = filtered_df[columns_to_keep]

    return filtered_df
    
    


def map_data(df1, df2):
    # Strip whitespace from the 'Designator' column in both DataFrames
    mapping_dict = df1.set_index('Designator').to_dict()

    
    df1['Designator'] = df1['Designator'].str.strip()
    df2['Designator'] = df2['Designator'].str.strip()

    # Map the 'Center-X(mm)', 'Center-Y(mm)', and 'Rotation' columns using the provided mapping dictionary
    df2['Center-X'] = df2['Designator'].map(mapping_dict['Center-X'])
    df2['Center-Y'] = df2['Designator'].map(mapping_dict['Center-Y'])
    df2['Rotation'] = df2['Designator'].map(mapping_dict['Rotation'])

    return df2
    


def process_data_and_merge(txt_file, excel_file, output_format='csv'):
    
    df_text_processed = process_and_save_txt_file(txt_file)
    df_excel_processed = process_xlsx_file(excel_file)

    df_result = map_data(df_text_processed, df_excel_processed)
    display_columns = ['Designator', 'Value', 'Center-X', 'Center-Y', 'Rotation']
    df_result = df_result[display_columns]


    export_path = None
    if output_format == 'csv':
        export_path = 'data_storage/exports/processed_data_dme.csv'
        df_result.to_csv(export_path, index=False)
    elif output_format == 'txt':
        export_path = 'data_storage/exports/processed_data_dme.txt'
        df_result.to_csv(export_path, index=False, sep='\t')

    return df_result, export_path



