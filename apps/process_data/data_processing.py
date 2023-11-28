import pandas as pd
import chardet
from django.core.files.base import ContentFile
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from io import BytesIO
import io
import csv
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render, HttpResponse
import pandas as pd
from .forms import UploadDataForm
from .models import TextData_Picknplace, DirtyData_BOM 
from sklearn.preprocessing import LabelEncoder
import os
import pandas as pd
from django.http import FileResponse
from django.conf import settings


def detect_encoding(file_content):
    result = chardet.detect(file_content)
    return result['encoding']

'''

def process_text_file(file_content, encoding):
    lines = file_content.decode(encoding).splitlines()
    data = [line.strip().split('|') for line in lines]
    df = pd.DataFrame(data, columns=['Column1', 'Designators', 'Column3', 'X-Column', 'Y-Column', 'Rotations', 'Column7', 'Column8', 'Column9', 'Column10', 'Column11'])
    df.dropna(how='any', inplace=True)
    output_file = 'processed_text_data.xlsx'  # Specify the output file name
    df.to_excel(output_file, index=False)  # Save the DataFrame to an Excel file'''




def process_text_file(file_content, encoding):
    bytes_content = file_content.read()
    decoded_content = bytes_content.decode(encoding)
    lines = decoded_content.splitlines()
    data = [line.strip().split('|') for line in lines]
    df = pd.DataFrame(data, columns=['Column1', 'Designators', 'Column3', 'X-Column', 'Y-Column', 'Rotations', 'Column7', 'Column8', 'Column9', 'Column10', 'Column11'])
    df.dropna(how='any', inplace=True)
    output_file = 'processed_text_data.xlsx' 
    df.to_excel(output_file, index=False)



def process_excel(input_file, output_file):
    df = pd.read_excel(input_file)
    df.set_index('Designators', inplace=True)
    columns_to_display = ['X-Column', 'Y-Column', 'Rotations']
    display_df = df[columns_to_display]
    display_df.to_excel(output_file, index=True)

def train_cleaning_model(cleaned_data_file, dirty_data_file):
    df_cleaned = pd.read_excel(cleaned_data_file)
    df_dirty = pd.read_excel(dirty_data_file)
    df_cleaned['label'] = 1 
    df_dirty['label'] = 0    
    df_combined = pd.concat([df_cleaned, df_dirty], ignore_index=True)
    if 'Designators' not in df_combined.columns:
        raise ValueError("The 'Designators' column is missing in the combined dataset.")
    df_combined['Designators'] = df_combined['Designators'].astype(str)
    df_combined['Parent Description'] = df_combined['Parent Description'].astype(str)
    df_combined['Child'] = df_combined['Child'].astype(str)
    X = df_combined.drop(columns=['label'])
    y = df_combined['label']
    label_encoder = LabelEncoder()
    for column in ['Designators', 'Child', 'Parent Description' ]:
        if column in X.columns:
            X[column] = label_encoder.fit_transform(X[column])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    print(f"Model Accuracy: {accuracy:.2f}")
    return model


def clean_data(input_file, output_file):
    df = pd.read_excel(input_file)
    df['Designators'] = df['Designators'].astype(str)
    sorted_df = df.sort_values(by='Designators')
    sorted_df['Designators'] = sorted_df['Designators'].str.split(',')
    exploded_df = sorted_df.explode('Designators')
    columns_to_keep = ['Child', 'Parent Description', 'Designators']
    filtered_df = exploded_df[columns_to_keep]
    filtered_df = filtered_df.drop_duplicates(subset='Designators')
    filtered_df = filtered_df[~filtered_df['Parent Description'].str.contains('BPR Insert PCB Assembly', na=False)]
    filtered_df = filtered_df[~filtered_df['Parent Description'].str.contains('Commercial', case=False, na=False)]
    filtered_df = filtered_df[~filtered_df['Designators'].str.contains('nan', case=False, na=False)]
    filtered_df = filtered_df[~filtered_df['Parent Description'].str.contains('Package Assembly', na=False)]
    filtered_df['Designators'] = filtered_df['Designators'].apply(lambda x: 'R' + str(x) if (str(x).isnumeric() or (isinstance(x, str) and x.replace('.', '').isnumeric())) else x)
    filtered_df = filtered_df.dropna(subset=['Designators'])
    filtered_df['Designators'] = filtered_df['Designators'].apply(lambda x: ','.join(pd.Series(x).drop_duplicates()))
    filtered_df = filtered_df[['Designators', 'Child', 'Parent Description']]
    filtered_df.to_excel(output_file, index=False)



def process_uploaded_files(dirty_text_file, dirty_excel_file, output_format='csv'):
    dirty_data_content = dirty_text_file.read()
    dirty_data_encoding = detect_encoding(dirty_data_content)
    process_text_file(BytesIO(dirty_data_content), dirty_data_encoding) 

    cleaned_bom_file_path = 'cleaned_bom.xlsx'
    clean_data(dirty_excel_file, cleaned_bom_file_path)
    trained_model = train_cleaning_model(cleaned_bom_file_path, cleaned_bom_file_path)
    input_excel_file_path = 'processed_text_data.xlsx'
    output_excel_file_path = 'manip_datav3.3.xlsx'
    process_excel(input_excel_file_path, output_excel_file_path)
    
    # Merge the cleaned BOM with the mapping data
    df_cleaned_bom = pd.read_excel(cleaned_bom_file_path)
    df_mapping = pd.read_excel(output_excel_file_path, usecols=['Designators', 'X-Column', 'Y-Column', 'Rotations'])
    df_result = df_cleaned_bom.merge(df_mapping, on='Designators', how='left')
    display_columns = ['Designators', 'Child', 'X-Column', 'Y-Column', 'Rotations']
    df_result = df_result[display_columns]

    export_path = None
    if output_format == 'csv':
        export_path = 'data_storage/exports/processed_data.csv'
        df_result.to_csv(export_path, index=False)
    elif output_format == 'txt':
        export_path = 'data_storage/exports/processed_data.txt'
        df_result.to_csv(export_path, index=False, sep='\t')
    

    
    return df_result, export_path

