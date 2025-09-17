import streamlit as st
import datetime
import json
import os
import re
from collections import defaultdict

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
for key in ["jours_absents_1", "jours_absents_2", "stock_manquant", "ajouts_manuels", "liste_courses"]:
    if key not in st.session_state:
        st.session_state[key] = []

# === Interface ===
st.title("🛒 Planificateur de courses")

# Choix manuel de la semaine
semaine_actuelle = st.radio("📆 Choisis la semaine :", ["Semaine 1", "Semaine 2"])

# Absences par semaine
with st.expander("🕒 Gérer les absences par semaine"):
    jours_semaine = ["lundi midi", "lundi soir", "mardi midi", "mardi soir", "mercredi midi", "mercredi soir",
                     "jeudi midi", "jeudi soir", "vendredi midi", "vendredi soir", "samedi midi", "samedi soir",
                     "dimanche midi", "dimanche soir"]

    st.subheader("Semaine 1")
    absents_1 = st.multiselect("Jours absents (Semaine 1)", jours_semaine)

    st.subheader("Semaine 2")
    absents_2 = st.multiselect("Jours absents (Semaine 2)", jours_semaine)

    if st.button("Valider les absences par semaine"):
        st.session_state.jours_absents_1 = absents_1
        st.session_state.jours_absents_2 = absents_2
        st.success("Absences enregistrées pour les deux semaines.")

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
    nom_normalisé = ajout.strip().lower()
    if nom_normalisé not in [i.lower() for i in st.session_state.ajouts_manuels]:
        st.session_state.ajouts_manuels.append(ajout)
        st.success(f"Ajouté : {ajout}")
    else:
        st.warning(f"🔁 {ajout} est déjà dans la liste.")

# Générer la liste
if st.button("📋 Générer la liste de courses"):
    quantites = defaultdict(int)
    recettes = planning.get(semaine_actuelle, [])
    jours = ["lundi midi", "lundi soir", "mardi midi", "mardi soir", "mercredi midi", "mercredi soir",
             "jeudi midi", "jeudi soir", "vendredi midi", "vendredi soir", "samedi midi",
             "samedi soir", "dimanche midi", "dimanche soir"]

    absents = st.session_state.get(f"jours_absents_{1 if semaine_actuelle == 'Semaine 1' else 2}", [])

    for i, recette in enumerate(recettes):
        try:
            jour_midi = jours[i * 2]
            jour_soir = jours[i * 2 + 1]
        except IndexError:
            continue
        if jour_midi in absents and jour_soir in absents:
            continue
        for ing in recettes_2repas.get(recette, []):
            match = re.match(r"(\d+)\s+(.*)", ing)
            quantite = int(match.group(1)) if match else 1
            nom = match.group(2).strip().lower() if match else ing.strip().lower()
            nom = normalisation.get(nom, nom)
            if nom not in stock_permanent:
                quantites[nom] += quantite

    # Ajout des ingrédients manuels et du stock, sans doublons ni quantité imposée
    ingredients_uniques = set(
        normalisation.get(item.lower(), item.lower())
        for item in st.session_state.stock_manquant + st.session_state.ajouts_manuels
    )

    for nom in ingredients_uniques:
        quantites[nom] += 0  # On initialise sans quantité

    # Construction de la liste finale
    st.session_state.liste_courses = [
        f"{nom}" if qte == 0 else f"{qte} {nom}"
        for nom, qte in sorted(quantites.items())
    ]

# Affichage liste
if "liste_courses" in st.session_state and st.session_state.liste_courses:
    st.subheader("📋 Liste de courses")

    suppression = st.multiselect("❌ Supprimer des éléments :", st.session_state.liste_courses)

    if st.button("Supprimer sélection") and suppression:
        st.session_state.liste_courses = [
            item for item in st.session_state.liste_courses if item not in suppression
        ]
        st.rerun()  # 🔁 Force le rafraîchissement de l'app après suppression

    # Affichage mis à jour après suppression
    liste_formatee = "\n".join([f"- {item}" for item in st.session_state.liste_courses])
    st.markdown(liste_formatee)
