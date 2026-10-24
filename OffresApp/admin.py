from django.contrib import admin
from .models import Offer
# Register your models here.
import csv
from django.http import HttpResponse
from django.utils.html import format_html

from .models import Offer

# Couleur du badge par statut (gris par défaut si un nouveau statut est ajouté et oublié ici).
STATUT_COLORS = {
    'proposee': '#fd7e14',
    'acceptee': '#198754',
    'refusee': '#dc3545',
    'retiree': '#6c757d',
}


@admin.register(Offer)
class OffreAdmin(admin.ModelAdmin):
    actions = ['exporter_csv']
    list_display = ('expedition', 'transporteur', 'vehicule', 'prix', 'delai_jours', 'statut_badge', 'statut', 'date_proposition')
    list_filter = ('statut', 'date_proposition')
    search_fields = ('expedition__reference', 'transporteur__raison_sociale', 'vehicule__immatriculation')
    list_select_related = ('expedition', 'transporteur', 'vehicule')
    # Accepter/refuser une offre depuis la liste : chaque ligne passe par Offre.save(),
    # donc full_clean() et la cascade de la règle 5 s'appliquent normalement.
    list_editable = ('statut',)
    # Remplace les 3 menus déroulants par un champ de recherche (nécessite search_fields
    # sur ExpeditionAdmin, EntrepriseAdmin et VehiculeAdmin, déjà défini).
    autocomplete_fields = ('expedition', 'transporteur', 'vehicule')
    ordering = ('-date_proposition',)
    date_hierarchy = 'date_proposition'
    list_per_page = 25
    readonly_fields = ('statut_badge', 'date_proposition', 'created_at', 'updated_at')
    fieldsets = (
        ('Parties prenantes', {
            'fields': ('expedition', 'transporteur', 'vehicule')
        }),
        ('Conditions commerciales', {
            'fields': ('prix', 'delai_jours', 'statut', 'statut_badge')
        }),
        ('Horodatage', {
            'fields': ('date_proposition', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        # Une offre acceptée engage le transporteur : ses conditions ne bougent plus.
        base = list(self.readonly_fields)
        if obj and obj.statut == 'acceptee':
            return base + ['prix', 'delai_jours']
        return base

    @admin.display(description='Statut', ordering='statut')
    def statut_badge(self, obj):
        color = STATUT_COLORS.get(obj.statut, '#6c757d')
        return format_html(
            '<span style="background-color:{}; color:#fff; padding:2px 10px; '
            'border-radius:10px; font-size:12px; font-weight:600;">{}</span>',
            color, obj.get_statut_display(),
        )

    @admin.action(description="Exporter les offres sélectionnées en CSV")
    def exporter_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="offres.csv"'
        # BOM UTF-8 : sans lui, Excel affiche mal les caractères accentués (é, è...).
        response.write('﻿')

        writer = csv.writer(response)
        writer.writerow([
            'Référence expédition', 'Transporteur', 'Véhicule', 'Prix (TND)',
            'Délai (jours)', 'Statut', 'Date de proposition',
        ])
        for offre in queryset.select_related('expedition', 'transporteur', 'vehicule'):
            writer.writerow([
                offre.expedition.reference,
                offre.transporteur.raison_sociale,
                offre.vehicule.immatriculation,
                offre.prix,
                offre.delai_jours,
                offre.get_statut_display(),
                offre.date_proposition,
            ])
        return response