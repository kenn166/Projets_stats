from statistics import median, pvariance, pstdev
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView
import json

from .models import Classe, Etablissement, Etudiant, Matiere, Note
from .forms import EtablissementForm, ClasseForm, EtudiantForm, MatiereForm, NoteForm


def _quantile(sorted_values, q):
    if not sorted_values:
        return None
    idx = (len(sorted_values) - 1) * q
    lower = int(idx)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = idx - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def calculer_statistiques_descriptives(valeurs):
    if not valeurs:
        return {"effectif": 0, "moyenne": None, "mediane": None, "variance": None,
                "ecart_type": None, "minimum": None, "maximum": None, "q1": None, "q3": None}
    triees = sorted(valeurs)
    return {
        "effectif": len(triees),
        "moyenne": round(sum(triees) / len(triees), 2),
        "mediane": round(median(triees), 2),
        "variance": round(pvariance(triees), 2),
        "ecart_type": round(pstdev(triees), 2),
        "minimum": triees[0],
        "maximum": triees[-1],
        "q1": round(_quantile(triees, 0.25), 2),
        "q3": round(_quantile(triees, 0.75), 2),
    }


def _moyenne_ponderee_etudiant(etudiant):
    notes = etudiant.notes.select_related("matiere")
    total_coef = sum(note.matiere.coefficient for note in notes)
    if total_coef == 0:
        return None
    return sum(note.valeur * note.matiere.coefficient for note in notes) / total_coef


def _repartition(notes):
    r = {"[0-10[": 0, "[10-12[": 0, "[12-14[": 0, "[14-16[": 0, "[16-20]": 0}
    for note in notes:
        if note < 10: r["[0-10["] += 1
        elif note < 12: r["[10-12["] += 1
        elif note < 14: r["[12-14["] += 1
        elif note < 16: r["[14-16["] += 1
        else: r["[16-20]"] += 1
    return r


def tableau_bord_statistiques(request):
    classe_id = request.GET.get("classe_id", "")
    matiere_id = request.GET.get("matiere_id", "")

    classes = Classe.objects.select_related("etablissement").all()
    matieres = Matiere.objects.all()

    notes_qs = Note.objects.select_related("etudiant__classe", "matiere")
    if classe_id:
        notes_qs = notes_qs.filter(etudiant__classe_id=classe_id)
    if matiere_id:
        notes_qs = notes_qs.filter(matiere_id=matiere_id)

    notes = list(notes_qs.values_list("valeur", flat=True))
    statistiques = calculer_statistiques_descriptives(notes)
    repartition = _repartition(notes)

    etudiants_qs = Etudiant.objects.select_related("classe").prefetch_related("notes__matiere")
    if classe_id:
        etudiants_qs = etudiants_qs.filter(classe_id=classe_id)

    meilleurs_etudiants = []
    for etudiant in etudiants_qs:
        if matiere_id:
            note_obj = etudiant.notes.filter(matiere_id=matiere_id).first()
            if note_obj:
                meilleurs_etudiants.append({"etudiant": etudiant, "moyenne": round(note_obj.valeur, 2)})
        else:
            moyenne = _moyenne_ponderee_etudiant(etudiant)
            if moyenne is not None:
                meilleurs_etudiants.append({"etudiant": etudiant, "moyenne": round(moyenne, 2)})
    meilleurs_etudiants.sort(key=lambda x: x["moyenne"], reverse=True)
    top5 = meilleurs_etudiants[:5]

    stats_par_matiere = []
    if not matiere_id:
        for mat in matieres:
            nq = Note.objects.filter(matiere=mat)
            if classe_id:
                nq = nq.filter(etudiant__classe_id=classe_id)
            vals = list(nq.values_list("valeur", flat=True))
            if vals:
                stats_par_matiere.append({"nom": mat.nom, "moyenne": round(sum(vals)/len(vals), 2), "effectif": len(vals)})

    stats_par_classe = []
    if not classe_id:
        for cl in classes:
            nq = Note.objects.filter(etudiant__classe=cl)
            if matiere_id:
                nq = nq.filter(matiere_id=matiere_id)
            vals = list(nq.values_list("valeur", flat=True))
            if vals:
                stats_par_classe.append({"nom": cl.nom, "moyenne": round(sum(vals)/len(vals), 2), "effectif": len(vals)})

    titre_filtre = "Vue globale"
    if classe_id and matiere_id:
        cl_obj = classes.filter(id=classe_id).first()
        mat_obj = matieres.filter(id=matiere_id).first()
        titre_filtre = f"{cl_obj.nom if cl_obj else '?'} — {mat_obj.nom if mat_obj else '?'}"
    elif classe_id:
        cl_obj = classes.filter(id=classe_id).first()
        titre_filtre = f"Classe : {cl_obj.nom if cl_obj else '?'}"
    elif matiere_id:
        mat_obj = matieres.filter(id=matiere_id).first()
        titre_filtre = f"Matière : {mat_obj.nom if mat_obj else '?'}"

    contexte = {
        "statistiques": statistiques,
        "repartition": repartition,
        "meilleurs_etudiants": top5,
        "nombre_eleves": etudiants_qs.count(),
        "nombre_notes": len(notes),
        "classes": classes,
        "matieres": matieres,
        "classe_id_selected": classe_id,
        "matiere_id_selected": matiere_id,
        "titre_filtre": titre_filtre,
        "graph_intervalles_labels": json.dumps(list(repartition.keys())),
        "graph_intervalles_data": json.dumps(list(repartition.values())),
        "graph_top_labels": json.dumps([f"{i['etudiant'].prenom} {i['etudiant'].nom}" for i in top5]),
        "graph_top_data": json.dumps([i["moyenne"] for i in top5]),
        "graph_matiere_labels": json.dumps([s["nom"] for s in stats_par_matiere]),
        "graph_matiere_data": json.dumps([s["moyenne"] for s in stats_par_matiere]),
        "graph_classe_labels": json.dumps([s["nom"] for s in stats_par_classe]),
        "graph_classe_data": json.dumps([s["moyenne"] for s in stats_par_classe]),
        "show_radar": len(stats_par_matiere) >= 3,
        "show_classe_chart": len(stats_par_classe) >= 1,
    }
    return render(request, "etudes/tableau_bord.html", contexte)


class GestionIndexView(TemplateView):
    template_name = "etudes/gestion_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.urls import reverse
        context["entities"] = [
            {"label": "Établissements", "icon": "🏫", "url": reverse("etablissement-liste"), "desc": "Gérer les établissements scolaires"},
            {"label": "Classes", "icon": "🎓", "url": reverse("classe-liste"), "desc": "Gérer les classes et années"},
            {"label": "Étudiants", "icon": "👤", "url": reverse("etudiant-liste"), "desc": "Gérer les élèves"},
            {"label": "Matières", "icon": "📚", "url": reverse("matiere-liste"), "desc": "Gérer les matières et coefficients"},
            {"label": "Notes", "icon": "📝", "url": reverse("note-liste"), "desc": "Saisir et modifier les notes"},
        ]
        return context

class BaseListView(ListView):
    template_name = "etudes/crud_list.html"
    context_object_name = "objets"
    entite = ""
    titre = ""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entite"] = self.entite
        context["titre"] = self.titre
        return context

class BaseCreateView(CreateView):
    template_name = "etudes/crud_form.html"
    fields = "__all__"
    entite = ""
    titre = ""
    def get_success_url(self):
        return reverse_lazy(f"{self.entite}-liste")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entite"] = self.entite
        context["titre"] = self.titre
        context["action"] = "Ajouter"
        return context

class BaseUpdateView(UpdateView):
    template_name = "etudes/crud_form.html"
    fields = "__all__"
    entite = ""
    titre = ""
    def get_success_url(self):
        return reverse_lazy(f"{self.entite}-liste")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entite"] = self.entite
        context["titre"] = self.titre
        context["action"] = "Modifier"
        return context

class BaseDeleteView(DeleteView):
    template_name = "etudes/crud_confirm_delete.html"
    entite = ""
    titre = ""
    def get_success_url(self):
        return reverse_lazy(f"{self.entite}-liste")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entite"] = self.entite
        context["titre"] = self.titre
        return context

class EtablissementListView(BaseListView):
    model = Etablissement; entite = "etablissement"; titre = "Etablissements"
class EtablissementCreateView(BaseCreateView):
    model = Etablissement; form_class = EtablissementForm; fields = None; entite = "etablissement"; titre = "Etablissements"
class EtablissementUpdateView(BaseUpdateView):
    model = Etablissement; form_class = EtablissementForm; fields = None; entite = "etablissement"; titre = "Etablissements"
class EtablissementDeleteView(BaseDeleteView):
    model = Etablissement; entite = "etablissement"; titre = "Etablissements"

class ClasseListView(BaseListView):
    model = Classe; entite = "classe"; titre = "Classes"
class ClasseCreateView(BaseCreateView):
    model = Classe; form_class = ClasseForm; fields = None; entite = "classe"; titre = "Classes"
class ClasseUpdateView(BaseUpdateView):
    model = Classe; form_class = ClasseForm; fields = None; entite = "classe"; titre = "Classes"
class ClasseDeleteView(BaseDeleteView):
    model = Classe; entite = "classe"; titre = "Classes"

class EtudiantListView(BaseListView):
    model = Etudiant; entite = "etudiant"; titre = "Etudiants"
class EtudiantCreateView(BaseCreateView):
    model = Etudiant; form_class = EtudiantForm; fields = None; entite = "etudiant"; titre = "Etudiants"
class EtudiantUpdateView(BaseUpdateView):
    model = Etudiant; form_class = EtudiantForm; fields = None; entite = "etudiant"; titre = "Etudiants"
class EtudiantDeleteView(BaseDeleteView):
    model = Etudiant; entite = "etudiant"; titre = "Etudiants"

class MatiereListView(BaseListView):
    model = Matiere; entite = "matiere"; titre = "Matieres"
class MatiereCreateView(BaseCreateView):
    model = Matiere; form_class = MatiereForm; fields = None; entite = "matiere"; titre = "Matieres"
class MatiereUpdateView(BaseUpdateView):
    model = Matiere; form_class = MatiereForm; fields = None; entite = "matiere"; titre = "Matieres"
class MatiereDeleteView(BaseDeleteView):
    model = Matiere; entite = "matiere"; titre = "Matieres"

class NoteListView(BaseListView):
    model = Note; entite = "note"; titre = "Notes"
class NoteCreateView(BaseCreateView):
    model = Note; form_class = NoteForm; fields = None; entite = "note"; titre = "Notes"
class NoteUpdateView(BaseUpdateView):
    model = Note; form_class = NoteForm; fields = None; entite = "note"; titre = "Notes"
class NoteDeleteView(BaseDeleteView):
    model = Note; entite = "note"; titre = "Notes"
