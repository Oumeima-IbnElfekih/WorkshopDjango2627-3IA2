from django.contrib import admin,messages
from .models import Expedition
from django.utils import timezone
from django.core.exceptions import ValidationError
from OffresApp.models import Offer
from django.utils.html import format_html
# Register your models here.
# Couleur du badge par statut (gris par défaut si un nouveau statut est ajouté et oublié ici).
STATUT_COLORS = {
    'publiee': '#0d6efd',
    'en_cours': '#fd7e14',
    'attribuee': '#6f42c1',
    'livree': '#198754',
    'annulee': '#dc3545',
} 

class OffreInline(admin.TabularInline):
    # Lecture seule : une offre se crée/évolue via les règles métier d'OffresApp,
    # pas en la modifiant à la main depuis la fiche de l'expédition.
    model = Offer
    fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut', 'date_proposition')
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class OffreInlineStacked(admin.StackedInline):
    # exactement le même comportement qu'OffreInline (lecture seule, pas d'ajout), seule la mise en forme change (StackedInline = un bloc vertical par offre, au lieu d'une ligne de tableau). 
    model = Offer
    fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut', 'date_proposition')
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False
class EnRetard(admin.SimpleListFilter):
    title ='en_retard'
    parameter_name ='en_retard'
    def lookups(self, request, model_admin):
        return [('oui', 'Oui'), ('non', 'Non')]
    def queryset(self, request, q):
        if  self.value() == 'oui':
            return q.filter(statut='publiee', date_souhaitee__lt=timezone.now().date())
        if self.value() == 'non':
             return q.exclude(statut='publiee', date_souhaitee__lt=timezone.now().date())
        return q

    
class ExpeditionAdmin(admin.ModelAdmin):
    inlines = [OffreInline, OffreInlineStacked]
    list_display =('ville_depart', 'ville_arrive')
    list_filter =(EnRetard,'ville_depart', 'ville_arrive')
    @admin.action(description=" Clôturer les expéditions sélectionnées")
    def make_it_livree(self,request,queryset):
        liste=queryset.filter(statut='en_cours')
        liste_ignored_nbr=queryset.exclude(statut='en_cours').count()
        compteur=0
        errors=[]
        for exp in liste:
            exp.statut='livree'
            try:
                exp.save()
                compteur+=1
            except ValidationError as error:
                errors.append(f"{exp.reference} : erreur lors de modification status avec erreur {error.messages}")
        if compteur:
            self.message_user(request," expéditions ont été cloturé", messages.SUCCESS)
        if liste_ignored_nbr:
            self.message_user(request,"expédition ignorés",messages.WARNING)
        for e in errors:
            self.message_user(request, e,messages.ERROR)
    actions = ['make_it_livree']
    search_fields = ('reference', 'ville_depart', 'ville_arrive', 'entreprise__raison_sociale')
    readonly_fields = ('reference', 'created_at', 'updated_at')
    fieldsets = (
        ('Expédition', {
            'fields': ('reference', 'entreprise', 'description')
        }),
        ('Itinéraire et poids', {
            'fields': ('ville_depart', 'ville_arrive', 'poids_kg', 'date_souhaitee')
        }),
        ('Statut et horodatage', {
            'fields': ('statut', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    @admin.display(description='Statut', ordering='statut')
    def statut_badge(self, obj):
        color = STATUT_COLORS.get(obj.statut, '#6c757d')
        return format_html(
            '<span style="background-color:{}; color:#fff; padding:2px 10px; '
            'border-radius:10px; font-size:12px; font-weight:600;">{}</span>',
            color, obj.get_statut_display(),
        )
admin.site.register(Expedition,ExpeditionAdmin)