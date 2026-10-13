from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator,MinLengthValidator
from django.utils import timezone
def email_validate(value):
    if not value:
        raise ValidationError("Email est obligatoire")
    if not value.endswith("@gmail.com"):
        raise ValidationError("Seuls les emails appartenant au domaine gmail.com sont acceptés")

matricule_fiscal_validator=RegexValidator(
    regex=r'^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$',
    message="matricule fiscale doit respecter un pattern bien déterminé"
)
# Create your models here.
class Utilisateur(AbstractUser):
    user_id=models.CharField(max_length=8,
                             editable=False,
                             primary_key=True)
    email=models.EmailField(unique=True,validators=[email_validate])
    role=models.CharField(max_length=20,choices=[
        ('chargeur','chargeur'),
        ('transporteur','transporteur'),
        ('administrateur','administrateur')],default="chargeur")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    telephone=models.CharField(max_length=8)
    REQUIRED_FIELDS = ['email', 'telephone']
    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self._generate_user_id()
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_user_id(cls):
        annee = timezone.now().strftime('%y')
        prefixe = f"{annee}user"

        dernier = (
            cls.objects
            .filter(user_id__startswith=prefixe)
            .order_by('-user_id')
            .first()
        )
        compteur = int(dernier.user_id[-2:]) + 1 if dernier else 0

        if compteur > 99:
            raise ValueError(
                f"Limite de 100 utilisateurs atteinte pour l'année 20{annee}."
            )

        return f"{prefixe}{compteur:02d}"
class Entreprise(models.Model):
    raison_social=models.CharField(max_length=100)
    matricule_fiscal=models.CharField(
        max_length=17,unique=True, validators= [matricule_fiscal_validator]
    )
    type_entreprise=models.CharField(max_length=15,choices=
                                     [
                                         ('chargeur','chargeur'),
                                         ('transporteur','transporteur')
                                     ])
    adresse=models.TextField(validators=[MinLengthValidator(20,"Un minimum de 20 caractères pour accepter l’adresse ")])
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    gerant=models.OneToOneField(Utilisateur,on_delete=models.CASCADE,related_name='entreprise')
    def __str__(self):
        return self.raison_social

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)