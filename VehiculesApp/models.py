from django.db import models

# Create your models here.
class Vehicule(models.Model):
    immatriculation=models.CharField(max_length=10,unique=True)
    type_vehicule=models.CharField(max_length=50,choices=
                                   [('camionnette','camionnette'),
                                    ('fourgon','fourgon'),
                                    ('camion_porteur','Camion Porteur'),
                                    ('semi_remorque','Semi-remorque.')])
    capacite_kg=models.PositiveIntegerField()
    disponible=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    entreprise=models.ForeignKey('EntrepriseApp.Entreprise',on_delete=models.CASCADE,related_name='vehicules')
    