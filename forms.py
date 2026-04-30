from django import forms
from .models import Classe, Etablissement, Etudiant, Matiere, Note
import datetime

current_year = datetime.date.today().year


class EtablissementForm(forms.ModelForm):
    class Meta:
        model = Etablissement
        fields = "__all__"
        labels = {
            "nom": "Nom de l'établissement",
        }
        widgets = {
            "nom": forms.TextInput(attrs={
                "placeholder": "ex : Lycée Général de la Réunion",
                "autocomplete": "off",
            }),
        }
        help_texts = {
            "nom": "Nom complet de l'école, du collège ou du lycée (max. 100 caractères).",
        }


class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = "__all__"
        labels = {
            "nom": "Nom de la classe",
            "etablissement": "Établissement",
            "annee_scolaire": "Année scolaire",
        }
        widgets = {
            "nom": forms.TextInput(attrs={
                "placeholder": "ex : Terminale S, 3ème A, CM2-B…",
                "autocomplete": "off",
            }),
            "annee_scolaire": forms.TextInput(attrs={
                "placeholder": f"ex : {current_year}-{current_year+1}",
                "pattern": r"\d{4}-\d{4}",
                "autocomplete": "off",
            }),
            "etablissement": forms.Select(attrs={
                "data-placeholder": "Choisir un établissement",
            }),
        }
        help_texts = {
            "nom": "Niveau et division de la classe.",
            "annee_scolaire": "Format attendu : AAAA-AAAA (ex : 2024-2025).",
            "etablissement": "Sélectionnez l'établissement auquel appartient cette classe.",
        }


class EtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = "__all__"
        labels = {
            "nom": "Nom de famille",
            "prenom": "Prénom",
            "date_naissance": "Date de naissance",
            "classe": "Classe",
        }
        widgets = {
            "nom": forms.TextInput(attrs={
                "placeholder": "ex : DUPONT",
                "autocomplete": "off",
            }),
            "prenom": forms.TextInput(attrs={
                "placeholder": "ex : Marie",
                "autocomplete": "off",
            }),
            "date_naissance": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "placeholder": "JJ/MM/AAAA",
                }
            ),
            "classe": forms.Select(attrs={
                "data-placeholder": "Choisir une classe",
            }),
        }
        help_texts = {
            "nom": "En majuscules de préférence.",
            "prenom": "Tel qu'il apparaît sur les documents officiels.",
            "date_naissance": "Optionnel — format JJ/MM/AAAA.",
            "classe": "Classe dans laquelle est inscrit l'élève.",
        }


class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = "__all__"
        labels = {
            "nom": "Nom de la matière",
            "coefficient": "Coefficient",
        }
        widgets = {
            "nom": forms.TextInput(attrs={
                "placeholder": "ex : Mathématiques, Français, Histoire-Géo…",
                "autocomplete": "off",
            }),
            "coefficient": forms.NumberInput(attrs={
                "placeholder": "ex : 3",
                "min": 1,
                "max": 20,
            }),
        }
        help_texts = {
            "nom": "Nom complet de la matière enseignée.",
            "coefficient": "Valeur entière ≥ 1 utilisée pour le calcul de la moyenne pondérée.",
        }


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = "__all__"
        labels = {
            "etudiant": "Élève",
            "matiere": "Matière",
            "valeur": "Note obtenue",
        }
        widgets = {
            "etudiant": forms.Select(attrs={
                "data-placeholder": "Choisir un élève",
            }),
            "matiere": forms.Select(attrs={
                "data-placeholder": "Choisir une matière",
            }),
            "valeur": forms.NumberInput(attrs={
                "placeholder": "ex : 13.5",
                "min": 0,
                "max": 20,
                "step": 0.5,
            }),
        }
        help_texts = {
            "etudiant": "Sélectionnez l'élève concerné.",
            "matiere": "Sélectionnez la matière évaluée.",
            "valeur": "Valeur entre 0 et 20 (décimales autorisées, ex : 13.5).",
        }
