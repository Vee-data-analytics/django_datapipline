from django.urls import path
from . import views
from . import data_table


app_name = 'processing_data'

urlpatterns = [
    path('process-data/lg/', views.process_data, name='process_data'),
    path('process-data/dme/', views.process_data_dme, name = 'process_dme'),
    path('process-data/kaon/',views.process_data_kaon, name='process_kaon'),
    path('process-data/landis/',views.process_data_landis, name='process_landis'),
    path('process-data-page/', views.process_data_page, name='process_data_page'),
   
]


