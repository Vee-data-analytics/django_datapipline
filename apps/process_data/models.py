from django.db import models

class TextData_Picknplace(models.Model):
    file = models.FileField(upload_to='picknplce_text_data/')  
    upload_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.file.name
          
class DirtyData_BOM(models.Model):
    file = models.FileField(upload_to='dirty_bom_data/') 
    upload_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.file.name 

