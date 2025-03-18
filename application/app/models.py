from django.db import models

# Create your models here.
class Model(models.Model):
    company_name = models.TextField(null=True, blank=True)
    session_id = models.TextField(null=True, blank=True)
    user_input = models.TextField(null=True, blank=True)
    def __str__(self):
        return "Model"
    