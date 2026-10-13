from django.contrib import admin
from .models import Utilisateur,Entreprise
from django.contrib.auth.admin import UserAdmin
# Register your models here.
@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display=('user_id','username','role','first_name','last_name')
    list_filter=('user_id','created_at')
    search_fields=('telephone',)
    list_editable=('first_name','last_name')
    ordering=('-created_at',)
    date_hierarchy='created_at'
    list_per_page=1

#admin.site.register(Utilisateur,UtilisateurAdmin)

class EntrepriseAdmin(admin.ModelAdmin):
    pass
admin.site.register(Entreprise,EntrepriseAdmin)

