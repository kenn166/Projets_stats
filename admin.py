from django.contrib import admin
from .models import Classe, Etablissement, Etudiant, Matiere, Note


@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
	list_display = ("nom",)
	search_fields = ("nom",)


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
	list_display = ("nom", "annee_scolaire", "etablissement")
	list_filter = ("annee_scolaire", "etablissement")
	search_fields = ("nom",)


@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
	list_display = ("prenom", "nom", "classe")
	list_filter = ("classe",)
	search_fields = ("prenom", "nom")


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
	list_display = ("nom", "coefficient")
	search_fields = ("nom",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
	list_display = ("etudiant", "matiere", "valeur")
	list_filter = ("matiere", "etudiant__classe")
	search_fields = ("etudiant__nom", "etudiant__prenom", "matiere__nom")
