import streamlit as st
import datetime
import json
import os
import re
from collections import defaultdict

# === Fichier JSON ===
FICHIER_JSON = "etat_courses.json"

def charger_etat():
    if os.path.exists(FICHIER_JSON):
        with open(FICHIER_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "semaine_actuelle": 1,
            "derniere_date": str(datetime.date.today())
        }

def sauvegarder_etat(etat):
    with open(FICHIER_JSON, "w", encoding="utf-8") as f:
        json.dump(etat, f, indent=4, ensure_ascii=False)

def mise_a_jour_semaine(etat):
    aujourd_hui = datetime.date.today()
    dernier_lundi = aujourd_hui - datetime.timedelta(days=aujourd_hui.weekday())
    derniere_date = datetime.datetime.strptime(etat["derniere_date"], "%Y-%m-%d").date()

    if derniere_date < dernier_lundi:
        etat["semaine_actuelle"] = 2 if etat["semaine_actuelle"] == 1 else 1
        etat["derniere_date"] = str(aujourd_hui)
        sauvegarder_etat(etat)

# === Données ===
stock_permanent = [
    "beurre", "huile d'olive", "persil", "thym", "sel",
    "pâtes", "gruyère", "riz", "oignon", "ail",
    "couscous", "pain de mie", "basilic", "échalote", "poivre", "farine"
]

planning = {
    "Semaine 1": [
        "Oeufs brouillés + riz et courgettes", "Pafeta", "Galette sandwich",
        "Patatouille", "Omelette et courgettes", "Toast avocat", "Pâtes et poulet"
    ],
    "Semaine 2": [
        "Red couscous", "Pâtes à la sauce", "Patates et œufs",
        "Galette au fromage et lardons", "Omelette aux champis", "Risofou", "Shakshuka"
    ]
}

recettes_2repas = {
    "Oeufs brouillés + riz et courgettes": ["4 œufs", "2 courgettes"],
    "Pafeta": ["2 fromage de brebis", "2 sauce tomate", "2 olives"],
    "Galette sandwich": ["6 patates", "4 tomates", "6 œufs"],
    "Patatouille": ["2 haricots rouges", "4 carottes", "4 patates", "2 sauce tomate"],
    "Omelette et courgettes": ["6 œufs", "2 courgettes"],
    "Toast avocat": ["4 œufs", "2 avocats"],
    "Pâtes et poulet": ["2 blancs de poulet", "2 champignons", "2 crème fraîche"],
    "Red couscous": ["2 haricots rouges", "2 sauce tomate"],
    "Pâtes à la sauce": ["2 concentré de tomate", "2 crème fraîche"],
    "Patates et œufs": ["2 œufs", "2 patates"],
    "Galette au fromage et lardons": ["4 patates", "2 crème fraîche", "lardons"],
    "Omelette aux champis": ["4 œufs", "2 champignons"],
    "Risofou": ["2 tofu assaisonné", "2 champignons", "2 crème fraîche"],
    "Shakshuka": ["4 œufs", "2 pulpes de tomate", "2 poivrons", "2 fromage de brebis"]
}

normalisation = {
    "oeufs": "œufs", "œuf": "œufs", "oeuf": "œufs",
    "crème fraiche": "crèmes fraîche", "sauce tomate": "sauces tomate",
    "pulpe de tomate": "sauces tomate", "concentré de tomate": "sauces tomate",
    "patate": "patates", "champignons": "champignons", "tomates": "tomates",
    "poivrons": "poivrons", "avocats": "avocats", "tofu assaisonné": "tofus"
}

# === Initialisation ===
etat = charger_etat()
mise_a_jour_semaine(etat)
semaine_actuelle = etat["semaine_actuelle"]

if "jours_absents" not in st.session_state:
    st.session_state.jours_absents = []
if "stock_manquant" not in st.session_state:
    st.session_state.stock_manquant = []
if "ajouts_manuels" not in st.session_state:
    st.session_state.ajouts_manuels = []
if "liste_courses" not in st.session_state:
    st.session_state.liste_courses = []

# === Interface ===
st.title("🛒 Planificateur de courses")
st.subheader(f"📆 Semaine actuelle : Semaine {semaine_actuelle}")

# Absences
with st.expander("🕒 Gérer les absences"):
    jours = ["lundi soir", "mardi midi", "mardi soir", "mercredi midi", "mercredi soir",
             "jeudi midi", "jeudi soir", "vendredi midi", "vendredi soir", "samedi midi",
             "samedi soir", "dimanche midi", "dimanche soir"]
    selection_absence = []
    for jour in jours:
        if st.checkbox(jour, key=f"absence_{jour}"):
            selection_absence.append(jour)
    if st.button("Valider les absences"):
        st.session_state.jours_absents = selection_absence
        st.success("Absences enregistrées.")

# Stock
with st.expander("📦 Ajouter du stock à racheter"):
    selection_stock = []
    for item in stock_permanent:
        if st.checkbox(item, key=f"stock_{item}"):
            selection_stock.append(item)
    if st.button("Valider le stock à racheter"):
        st.session_state.stock_manquant = selection_stock
        st.success("Stock mis à jour.")

# Ajout manuel
ajout = st.text_input("➕ Ajouter un ingrédient manuellement")
if ajout:
    st.session_state.ajouts_manuels.append(ajout)
    st.success(f"Ajouté : {ajout}")

# Vacances
if st.button("🏖️ Réinitialiser après vacances"):
    etat["semaine_actuelle"] = 1
    etat["derniere_date"] = str(datetime.date.today())
    sauvegarder_etat(etat)
    st.success("Planning réinitialisé à la semaine 1")

# Générer la liste
if st.button("📋 Générer la liste de courses"):
    quantites = defaultdict(int)
    recettes = planning.get(f"Semaine {semaine_actuelle}", [])
    jours = ["lundi soir", "mardi midi", "mardi soir", "mercredi midi", "mercredi soir",
             "jeudi midi", "jeudi soir", "vendredi midi", "vendredi soir", "samedi midi",
             "samedi soir", "dimanche midi", "dimanche soir", "lundi midi"]

    for i, recette in enumerate(recettes):
        try:
            jour_soir = jours[i * 2]
            jour_midi = jours[i * 2 + 1]
        except IndexError:
            continue
        if jour_soir in st.session_state.jours_absents and jour_midi in st.session_state.jours_absents:
            continue
        for ing in recettes_2repas.get(recette, []):
            match = re.match(r"(\d+)\s+(.*)", ing)
            quantite = int(match.group(1)) if match else 1
            nom = match.group(2).strip().lower() if match else ing.strip().lower()
            nom = normalisation.get(nom, nom)
            if nom not in stock_permanent:
                quantites[nom] += quantite

    # ✅ Correction : éviter les doublons dans les ajouts manuels et le stock
    ingredients_uniques = set(
        normalisation.get(item.lower(), item.lower())
        for item in st.session_state.stock_manquant + st.session_state.ajouts_manuels
    )

    for nom in ingredients_uniques:
        quantites[nom] += 1

    st.session_state.liste_courses = [f"{qte} {nom}" for nom, qte in sorted(quantites.items())]

# Affichage liste
if st.session_state.liste_courses:
    st.subheader("📋 Liste de courses")

    liste_formatee = "\n".join([f"- {item}" for item in st.session_state.liste_courses])
    st.markdown(liste_formatee)

    suppression = st.multiselect("❌ Supprimer des éléments :", st.session_state.liste_courses)
    if st.button("Supprimer sélection"):
        st.session_state.liste_courses = [
            item for item in st.session_state.liste_courses if item not in suppression
        ]
        st.success("Éléments supprimés.")


