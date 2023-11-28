import pandas as pd 



def text_manip(dirty_text_file):
    # Read the content of the text file
    content = dirty_text_file.read().decode('ascii')

    # Split the content into a list of lines
    lines = content.strip().split('\n')

    # Split each line by the appropriate delimiter (e.g., whitespace)
    data = [line.split() for line in lines]

    # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=['Location', 'Column2', 'Column-X', 'Column-Y', 'Rotation', 'Column6'])
    columns_to_display = ['Location', 'Column-X', 'Column-Y', 'Rotation']
    df = df[columns_to_display]

    # Save the DataFrame as a CSV file
    df.to_excel('kaon_output_data1.xlsx', index=False)
    return df
 

   
def  bom_manip(input_excel_file):
     df = pd.read_excel(input_excel_file)

     sorted_df = df.sort_values(by='Location')
     sorted_df['Location'] = sorted_df['Location'].str.split(',')
     sorted_df=sorted_df.explode('Location')

     columns_to_keep = ['Location','Component' ,'Sort String' ,'Description', ]
     sorted_df = sorted_df[columns_to_keep]
     filtered_df = sorted_df.loc[~sorted_df['Sort String'].str.contains('ASSY')]
     columns_to_keep = ['Location','Component', 'Description']
     filtered_df =  filtered_df[columns_to_keep]
     return  filtered_df
   
   
   
def merge_kaon(df1, df2):
    # Create a dictionary to map 'Location' from df1 to columns from df2
    mapping_dict = df1.set_index('Location').to_dict()

    # Map the values from df2 to df1 based on 'Location'
    df2['X-Column'] = df2['Location'].map(mapping_dict['Column-X'])
    df2['Y-Column'] = df2['Location'].map(mapping_dict['Column-Y'])
    df2['Rotation'] = df2['Location'].map(mapping_dict['Rotation'])

    # Reorder the columns in df2 to match the desired order
    display_columns = ['Location', 'Component', 'Description', 'X-Column', 'Y-Column', 'Rotation']
    df2 = df2[display_columns]

    return df2

def process_data_merge(dirty_text_file, input_excel_file, output_format='csv'):
    # Process input files
    df_text_processed = text_manip(dirty_text_file)
    df_excel_processed = bom_manip(input_excel_file)

    # Merge data
    df_result = merge_kaon(df_text_processed, df_excel_processed)

    export_path = None
    if output_format == 'csv':
        export_path = 'data_storage/exports/processed_data.csv'
        df_result.to_csv(export_path, index=False)
    elif output_format == 'txt':
        export_path = 'data_storage/exports/processed_data.txt'
        df_result.to_csv(export_path, index=False, sep='\t')

    return df_result, export_path

   