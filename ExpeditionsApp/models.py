from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
# Create your models here.
class Expedition(models.Model):
    reference=models.CharField(max_length=20,unique=True,editable=False) # EXP-26-00003 99999
    ville_depart=models.CharField(max_length=100)
    ville_arrive=models.CharField(max_length=100)
    date_souhaitee=models.DateField()
    poids_kg=models.DecimalField(max_digits=300,decimal_places=3)
    description=models.TextField()
    statut=models.CharField(choices=[
        ( 'publiee','publiee'),
        ( 'attribuee','attribuee'),
        ( 'en_cours','en_cours'),
        ( 'livree','livree'),
         ( 'annulee','annulee')],default='publiee')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    entreprise=models.ForeignKey('EntrepriseApp.Entreprise',
                                 on_delete=models.CASCADE,
                                 related_name='expeditions')
    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
            raise ValidationError({
                'entreprise': "Une expédition ne peut être créée que par une entreprise de type chargeur."
            })
    def save(self,*args,**kwargs ):
        if not self.reference:
            self.reference=self._generate_ref()
        self.full_clean()
        super().save(*args,**kwargs )
    
    @classmethod
    def _generate_ref(cls):
        annee=timezone.now().strftime('%y')
        prefixe= f"EXP-{annee}-"
        last_value= (
            cls.objects
            .filter(reference__startswith=prefixe)
            .order_by('-reference')
            .first()
        )
        c=int(last_value.reference[-5:])+1 if last_value else 1
        if c >99999:
            raise ValidationError( f'limite de 99999 expéditions atteinte pour annee {annee}')
        return f"{prefixe}{c:05d}"
    def __str__(self):
        return f"Expedition {self.reference} from {self.ville_depart} to {self.ville_arrive}"
        

