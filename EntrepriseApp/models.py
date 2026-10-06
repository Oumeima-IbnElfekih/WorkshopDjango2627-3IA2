from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class Utilisateur(AbstractUser):
    user_id=models.CharField(max_length=8,
                             editable=False,
                             primary_key=True)
    email=models.EmailField(unique=True)
    role=models.CharField(max_length=20,choices=[
        ('chargeur','chargeur'),
        ('transporteur','transporteur'),
        ('administrateur','administrateur')],default="chargeur")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    telephone=models.CharField(max_length=8)

class Entreprise(models.Model):
    raison_social=models.CharField(max_length=100)
    matricule_fiscal=models.CharField(
        max_length=8,unique=True
    )
    type_entreprise=models.CharField(max_length=15,choices=
                                     [
                                         ('chargeur','chargeur'),
                                         ('transporteur','transporteur')
                                     ])
    adresse=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    gerant=models.OneToOneField(Utilisateur,on_delete=models.CASCADE,related_name='entreprise')
