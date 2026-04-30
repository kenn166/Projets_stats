from django.test import TestCase
from django.urls import reverse

from .models import Classe, Etablissement, Etudiant, Matiere, Note
from .views import calculer_statistiques_descriptives


class StatistiquesDescriptivesTests(TestCase):
	def test_statistiques_sur_serie(self):
		stats = calculer_statistiques_descriptives([8, 10, 12, 14, 16])

		self.assertEqual(stats["effectif"], 5)
		self.assertEqual(stats["moyenne"], 12)
		self.assertEqual(stats["mediane"], 12)
		self.assertEqual(stats["minimum"], 8)
		self.assertEqual(stats["maximum"], 16)
		self.assertEqual(stats["q1"], 10)
		self.assertEqual(stats["q3"], 14)

	def test_statistiques_sur_serie_vide(self):
		stats = calculer_statistiques_descriptives([])
		self.assertEqual(stats["effectif"], 0)
		self.assertIsNone(stats["moyenne"])


class TableauBordViewTests(TestCase):
	def setUp(self):
		etab = Etablissement.objects.create(nom="Lycee Horizon")
		classe = Classe.objects.create(
			nom="Terminale A",
			etablissement=etab,
			annee_scolaire="2025-2026",
		)
		etudiant = Etudiant.objects.create(
			nom="Diallo",
			prenom="Aicha",
			classe=classe,
		)
		math = Matiere.objects.create(nom="Mathematiques", coefficient=2)
		fr = Matiere.objects.create(nom="Francais", coefficient=1)
		Note.objects.create(etudiant=etudiant, matiere=math, valeur=15)
		Note.objects.create(etudiant=etudiant, matiere=fr, valeur=12)

	def test_tableau_bord_repond(self):
		response = self.client.get(reverse("tableau-bord-statistiques"))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, "etudes/tableau_bord.html")
		self.assertEqual(response.context["nombre_eleves"], 1)
		self.assertEqual(response.context["nombre_notes"], 2)


class CrudViewsTests(TestCase):
	def test_pages_crud_accessibles(self):
		self.assertEqual(self.client.get(reverse("gestion-index")).status_code, 200)
		self.assertEqual(self.client.get(reverse("etablissement-liste")).status_code, 200)
		self.assertEqual(self.client.get(reverse("classe-liste")).status_code, 200)
		self.assertEqual(self.client.get(reverse("etudiant-liste")).status_code, 200)
		self.assertEqual(self.client.get(reverse("matiere-liste")).status_code, 200)
		self.assertEqual(self.client.get(reverse("note-liste")).status_code, 200)

	def test_creation_etablissement(self):
		response = self.client.post(
			reverse("etablissement-ajouter"),
			data={"nom": "College Atlantique"},
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Etablissement.objects.count(), 1)
