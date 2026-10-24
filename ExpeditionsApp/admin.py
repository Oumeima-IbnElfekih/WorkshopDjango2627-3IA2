from django.contrib import admin,messages
from .models import Expedition
from django.utils import timezone
from django.core.exceptions import ValidationError
# Register your models here.
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
admin.site.register(Expedition,ExpeditionAdmin)