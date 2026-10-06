from django.db import models

# Create your models here.
class Offer(models.Model):
    prix=models.DecimalField(max_digits=10,decimal_places=10)
    date_proposition=models.DateField(auto_now_add=True)
    delai_jours=models.PositiveIntegerField()
    statut=models.CharField(max_length=20,choices=
                            [
                                ('proposee','proposee'),
                                 ('acceptee','acceptee'),
                                  ('refusee','refusee'),
                                   ('retiree','retiree')
                            ],default='proposee')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    transporteur=models.ForeignKey('EntrepriseApp.Entreprise',on_delete=models.CASCADE,related_name='offres')
    expedition=models.ForeignKey('ExpeditionsApp.Expedition',on_delete=models.CASCADE,related_name='offres')
    vehicule=models.ForeignKey('VehiculesApp.Vehicule',on_delete=models.CASCADE,related_name='offres')
