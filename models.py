from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Etablissement(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Classe(models.Model):
    nom = models.CharField(max_length=100)
    etablissement = models.ForeignKey(
        Etablissement,
        on_delete=models.CASCADE,
        related_name="classes",
    )
    annee_scolaire = models.CharField(max_length=9)

    def __str__(self):
        return f"{self.nom} ({self.annee_scolaire})"


class Etudiant(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Matiere(models.Model):
    nom = models.CharField(max_length=100)
    coefficient = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.nom} (coef. {self.coefficient})"


class Note(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="notes")
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name="notes")
    valeur = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(20)])

    class Meta:
        unique_together = ("etudiant", "matiere")

    def __str__(self):
        return f"{self.etudiant} - {self.matiere}: {self.valeur}/20"

