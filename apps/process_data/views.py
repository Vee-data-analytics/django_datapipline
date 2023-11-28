from django.http import HttpResponse
from django.shortcuts import render, redirect
from .data_processing import process_uploaded_files
from django.core.files.base import ContentFile
import chardet
from .forms import  UploadDataForm # DirtyTextUploadForm, DirtyExcelUploadForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.shortcuts import render
from .forms import UploadDataForm
import csv
from django.http import HttpResponse
from django.shortcuts import render
from .models import TextData_Picknplace, DirtyData_BOM
from .process_dme import process_data_and_merge
from .process_kaon import process_data_merge
from .process_landis import process_landis


#  the logic below will be used later when we create a Process data model
'''
def export_data_as_csv(request):
    # Fetch the data you want to export (in this case, fetching all rows)
    data = ProcessedData.objects.all()  # Adjust this query based on your model and data source
    # Create an HttpResponse with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'
    # Create a CSV writer and write the data to the response
    writer = csv.writer(response)
    # Write the header row based on your data
    writer.writerow(['Column1', 'Column2', 'Column3'])  # Replace with your column names
    # Write the data rows
    for row in data:
        writer.writerow([row.column1, row.column2, row.column3])  # Replace with your field names
    return response
def export_data_as_txt(request):
    # Fetch the data you want to export (in this case, fetching all rows)
    data = ProcessedData.objects.all()  # Adjust this query based on your model and data source
    # Create an HttpResponse with TXT content
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="data.txt"'
    # Write the data to the response
    for row in data:
        response.write(f"{row.column1}\t{row.column2}\t{row.column3}\n")  # Replace with your field names
    return response
    '''

def process_data(request):
    df_result = None
    export_path = None

    if request.method == 'POST':
        upload_form = UploadDataForm(request.POST, request.FILES)
        if upload_form.is_valid():
            dirty_text_file = upload_form.cleaned_data['dirty_txt_file']
            dirty_excel_file = upload_form.cleaned_data['dirty_excel_file']
            df_result, export_path = process_uploaded_files(dirty_text_file, dirty_excel_file)
            return render(request, 'result.html', {'df_result': df_result, 'export_path': export_path})

    else:
        upload_form = UploadDataForm()

    return render(request, 'process_data.html', {'upload_form': upload_form})

def process_data_page(request):
    return render(request, 'process_data_page.html')

def process_data_dme(request):
    df_result = None
    export_path = None

    if request.method == 'POST':
        upload_form = UploadDataForm(request.POST, request.FILES)
        if upload_form.is_valid():
            dirty_text_file = request.FILES['dirty_txt_file']
            dirty_excel_file = request.FILES['dirty_excel_file']

            # Process and merge the data
            df_result, export_path = process_data_and_merge(dirty_text_file, dirty_excel_file)

            return render(request, 'dme/result.html', {'df_result': df_result, 'export_path': export_path})

    else:
        upload_form = UploadDataForm()

    return render(request, 'dme/process_data.html', {'upload_form': upload_form})



def process_data_kaon(request):
    df_result = None
    export_path = None

    if request.method == 'POST':
        upload_form = UploadDataForm(request.POST, request.FILES)
        if upload_form.is_valid():
            dirty_text_file = request.FILES['dirty_txt_file']
            dirty_excel_file = request.FILES['dirty_excel_file']

            # Process and merge the data
            df_result, export_path = process_data_merge(dirty_text_file, dirty_excel_file)

            return render(request, 'kaon/result.html', {'df_result': df_result, 'export_path': export_path})

    else:
        upload_form = UploadDataForm()

    return render(request, 'kaon/process_data.html', {'upload_form': upload_form})


def process_data_landis(request):
    df_result = None
    export_path = None

    if request.method == 'POST':
        upload_form = UploadDataForm(request.POST, request.FILES)
        if upload_form.is_valid():
            dirty_text_file = request.FILES['dirty_txt_file']
            dirty_excel_file = request.FILES['dirty_excel_file']

            # Process and merge the data
            df_result, export_path = process_landis(dirty_text_file, dirty_excel_file)

            return render(request, 'landis/result.html', {'df_result': df_result, 'export_path': export_path})

    else:
        upload_form = UploadDataForm()

    return render(request, 'landis/process_data.html', {'upload_form': upload_form})







'''
def process_data(request):
    if request.method == 'POST':
        dirty_text_form = DirtyTextUploadForm(request.POST, request.FILES)
        dirty_excel_form = DirtyExcelUploadForm(request.POST, request.FILES)
        if dirty_text_form.is_valid() and dirty_excel_form.is_valid():
            dirty_text_file = dirty_text_form.cleaned_data['dirty_txt_file']
            dirty_excel_file = dirty_excel_form.cleaned_data['dirty_excel_file']
            df_result = process_uploaded_files(dirty_text_file, dirty_excel_file)
            return render(request, 'process_data.html', {'df_result': df_result})
    else:
        dirty_text_form = DirtyTextUploadForm()
        dirty_excel_form = DirtyExcelUploadForm()

    # Return the forms with crispy forms styling
    return render(request, 'process_data.html', {'dirty_text_form': dirty_text_form, 'dirty_excel_form': dirty_excel_form})
'''