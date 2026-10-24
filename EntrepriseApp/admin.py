from django.contrib import admin
from .models import Utilisateur,Entreprise
from django.contrib.auth.admin import UserAdmin
from VehiculesApp.models import Vehicule
admin.site.site_header ='TransConnect -Administration'
admin.site.site_title='TransConnect'
admin.site.index_title ='Tableau de bord'
# Register your models here.
@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display=('user_id','username','role','first_name','last_name')
    list_filter=('user_id','created_at')
    search_fields=('telephone',)
    list_editable=('first_name','last_name')
    ordering=('-created_at',)
    date_hierarchy='created_at'
    list_per_page=1
    readonly_fields = ('user_id', 'date_joined', 'last_login', 'created_at', 'updated_at')
    fieldsets = (
        ('Identité', {
            'fields': ('user_id', 'username', 'email', 'telephone')
        }),
        ('Rôle et permissions', {
            'fields': ('role', 'password', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Horodatage', {
            'fields': ('date_joined', 'last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

#admin.site.register(Utilisateur,UtilisateurAdmin)
class VehiculeInline(admin.TabularInline):
    model= Vehicule
    fields=('immatriculation','type_vehicule', 'capacite_kg')
    extra=1
class EntrepriseAdmin(admin.ModelAdmin):
    inlines = [VehiculeInline]
    list_display = ('raison_social', 'matricule_fiscal', 'type_entreprise', 'gerant', 'created_at')
    list_filter = ('type_entreprise', 'created_at')
    search_fields = ('raison_social', 'matricule_fiscal', 'gerant__username', 'gerant__email')
    list_select_related = ('gerant',)
    list_editable = ('type_entreprise',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    fieldsets = (
        ('Identité entreprise' , {
            'fields' :('raison_social','matricule_fiscal','type_entreprise')
            
        }),
        ('Contact', {
            'fields':('adresse','gerant'),
        }), 
        ('date systeme', {
            'fields' :('created_at','updated_at')
        })
    )
    readonly_fields=('created_at','updated_at')
admin.site.register(Entreprise,EntrepriseAdmin)

