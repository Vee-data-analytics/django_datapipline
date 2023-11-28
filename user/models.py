from django.db import models


class Programer(models.Model):
   user = models.PrimaryKey(User, CASCADE=on_delete)
   name = CharField(max_length=15)
   surname = CharField(max_length=15)

   def __str__(self):
      return self.name, surname

	
	
