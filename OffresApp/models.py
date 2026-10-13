from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.apps import apps


# Create your models here.

PLAGES_POIDS_PAR_TYPE_VEHICULE = {
    'camionnette': (Decimal(0), Decimal(1500)),
    'fourgon': (Decimal(1500), Decimal(3500)),
    'camion_porteur': (Decimal(3500), Decimal(19000)),
    'semi_remorque': (Decimal(19000), Decimal(26000)),
}
class Offer(models.Model):
    prix=models.DecimalField(max_digits=10,decimal_places=10,validators=[MinValueValidator(Decimal('0.01'), "Le prix doit être supérieur à 0.")])
    date_proposition=models.DateField(auto_now_add=True)
    delai_jours=models.PositiveIntegerField(validators=[MinValueValidator(1, "Le délai doit être supérieur à 0 jour.")])
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
    def clean(self):
        super().clean()
        if self.transporteur_id and self.transporteur.type_entreprise != 'transporteur':
            raise ValidationError(
                "Une offre ne peut être créée que par une entreprise dont type_entreprise = transporteur"
            )
        
        if self.vehicule_id and self.transporteur_id and self.vehicule.entreprise_id != self.transporteur_id:
            raise ValidationError({
                'vehicule': "Le véhicule doit appartenir à l'entreprise transporteur de l'offre."
            })

       
        if self.pk is None and self.expedition_id and self.expedition.statut != 'publiee':
            raise ValidationError({
                'expedition': "Cette expédition ne peut plus recevoir de nouvelles offres (statut différent de 'publiee')."
            })

        
        if self.statut == 'proposee' and self.transporteur_id and self.expedition_id:
            duplicate_exists = Offer.objects.filter(
                transporteur_id=self.transporteur_id,
                expedition_id=self.expedition_id,
                statut='proposee',
            ).exclude(pk=self.pk).exists()
            if duplicate_exists:
                raise ValidationError({
                    'statut': "Cette entreprise a déjà une offre 'proposee' active sur cette expédition."
                })

       
        if self.pk is None and self.vehicule_id and not self.vehicule.disponible:
            raise ValidationError({
                'vehicule': "Ce véhicule n'est pas disponible et ne peut pas être proposé sur une nouvelle offre."
            })

        
        if self.vehicule_id and self.expedition_id:
            plage = PLAGES_POIDS_PAR_TYPE_VEHICULE.get(self.vehicule.type_vehicule)
            poids_kg = self.expedition.poids_kg
            if plage and not (plage[0] < poids_kg <= plage[1]):
                raise ValidationError({
                    'vehicule': (
                        f"Le type de véhicule '{self.vehicule.type_vehicule}' n'est pas adapté "
                        f"au poids de l'expédition ({poids_kg} kg)."
                    )
                })
    def save(self, *args, **kwargs):
        self.full_clean()
        previous_statut = None
        if self.pk:
            previous_statut = Offer.objects.filter(pk=self.pk).values_list('statut', flat=True).first()

        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.statut == 'acceptee' and previous_statut != 'acceptee':
                self._appliquer_cascade_acceptation()

    def _appliquer_cascade_acceptation(self):
        Expedition = apps.get_model('ExpeditionsApp', 'Expedition')
        Expedition.objects.filter(pk=self.expedition_id).update(
            statut='attribuee', updated_at=timezone.now()
        )
        Offer.objects.filter(
            expedition_id=self.expedition_id,
            statut='proposee',
        ).exclude(pk=self.pk).update(statut='refusee', updated_at=timezone.now())