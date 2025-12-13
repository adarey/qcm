import json
import random
import os
import glob
import streamlit as st

# -------------------------------------------------
# Chemin vers le dossier des leçons
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LESSONS_DIR = os.path.join(BASE_DIR, "lessons")

# -----------------------
# Scan des leçons
# -----------------------
@st.cache_data
def scan_lessons():
    pattern = os.path.join(LESSONS_DIR, "*.json")
    files = glob.glob(pattern)
    themes = {}

    for path in files:
        filename = os.path.basename(path)
        name = filename[:-5]  # enlever .json

        if " - " in name:
            theme, lecon = name.split(" - ", 1)
        else:
            theme, lecon = name, "Défaut"

        theme = theme.strip()
        lecon = lecon.strip()

        if theme not in themes:
            themes[theme] = {}
        themes[theme][lecon] = path

    return themes


lessons_map = scan_lessons()

# -----------------------
# Chargement d'une leçon
# -----------------------
@st.cache_data
def load_lesson(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("questions", [])

# -----------------------
# Initialisation session
# -----------------------
for key, default in [
    ("theme_nom", None),
    ("lecon_nom", None),
    ("question_index", 0),
    ("indices_questions", []),
    ("score", 0),
    ("total_repondu", 0),
    ("derniere_reponse", None),
    ("derniere_correcte", None),
    ("questions_courantes", []),
    ("nb_questions", None),
    ("etat_question", "en_cours"),   # "en_cours" ou "validee"
    ("reponses_utilisateur", {}),    # {idx_reel: {"reponse": "...", "correcte": bool}}
    ("afficher_correction", False),
    ("reponses_melangees", {}),      # {idx_reel: [reponses mélangées]}
]:
    if key not in st.session_state:
        st.session_state[key] = default

# -----------------------
# Fonctions utilitaires
# -----------------------
def reset_quiz():
    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.total_repondu = 0
    st.session_state.derniere_reponse = None
    st.session_state.derniere_correcte = None
    st.session_state.etat_question = "en_cours"
    st.session_state.reponses_utilisateur = {}
    st.session_state.afficher_correction = False
    st.session_state.reponses_melangees = {}

    theme = st.session_state.theme_nom
    lecon = st.session_state.lecon_nom
    if theme and lecon and theme in lessons_map and lecon in lessons_map[theme]:
        path = lessons_map[theme][lecon]
        questions = load_lesson(path)
        st.session_state.questions_courantes = questions

        n = len(questions)
        indices = list(range(n))
        random.shuffle(indices)
        st.session_state.indices_questions = indices

        if st.session_state.nb_questions is None:
            st.session_state.nb_questions = min(25, n)
        else:
            st.session_state.nb_questions = min(st.session_state.nb_questions, n)

        st.session_state.indices_questions = st.session_state.indices_questions[:st.session_state.nb_questions]
    else:
        st.session_state.questions_courantes = []
        st.session_state.indices_questions = []
        st.session_state.nb_questions = None


def question_courante():
    if not st.session_state.questions_courantes or not st.session_state.indices_questions:
        return None, 0, None
    idx_reel = st.session_state.indices_questions[st.session_state.question_index]
    total = len(st.session_state.indices_questions)
    return st.session_state.questions_courantes[idx_reel], total, idx_reel

# -----------------------
# Fonctions d'affichage
# -----------------------
def afficher_qcm(question, total_questions, idx_reel):
    idx_affiche = st.session_state.question_index + 1

    st.subheader(f"{st.session_state.theme_nom} — {st.session_state.lecon_nom}")
    st.progress(idx_affiche / total_questions)

    st.markdown(
        f"<p class='question-text'>Question {idx_affiche} / {total_questions}</p>",
        unsafe_allow_html=True,
    )
    st.write(question["question"])

    # Réponses mélangées par question réelle
    if idx_reel not in st.session_state.reponses_melangees:
        st.session_state.reponses_melangees[idx_reel] = random.sample(
            question["reponses"], k=len(question["reponses"])
        )
    reponses_affichees = st.session_state.reponses_melangees[idx_reel]

    radio_key = f"q_{idx_reel}"
    choix = st.radio(
        "Choix de réponse",
        reponses_affichees,
        key=radio_key,
    )

    label_bouton = "✅ Valider" if st.session_state.etat_question == "en_cours" else "➡️ Question suivante"

    if st.button(label_bouton, use_container_width=True, key=f"btn_qcm_{idx_reel}"):
        if st.session_state.etat_question == "en_cours":
            st.session_state.derniere_reponse = choix
            bonne = question["bonne_reponse"]
            correcte = (choix == bonne)
            st.session_state.derniere_correcte = correcte
            st.session_state.total_repondu += 1
            if correcte:
                st.session_state.score += 1

            st.session_state.reponses_utilisateur[idx_reel] = {
                "reponse": choix,
                "correcte": correcte,
            }

            st.session_state.etat_question = "validee"
        else:
            if st.session_state.question_index < len(st.session_state.indices_questions) - 1:
                st.session_state.question_index += 1
                st.session_state.derniere_reponse = None
                st.session_state.derniere_correcte = None
                st.session_state.etat_question = "en_cours"
            else:
                st.warning("Tu es arrivé à la fin des questions de cette leçon.")

    if st.session_state.etat_question == "validee":
        bonne = question["bonne_reponse"]
        if st.session_state.derniere_correcte:
            st.success(f"Bonne réponse ! ✅ ({bonne})")
        else:
            st.error(f"Mauvaise réponse ❌. La bonne réponse était : {bonne}")
        if "explication" in question and question["explication"]:
            st.info(question["explication"])

    if st.session_state.total_repondu > 0:
        st.markdown(
            f"**Score :** {st.session_state.score} / {st.session_state.total_repondu} "
            f"({round(100*st.session_state.score/max(1, st.session_state.total_repondu))} %)"
        )


def afficher_carte(question, total_questions, idx_reel):
    idx_affiche = st.session_state.question_index + 1

    st.subheader(f"{st.session_state.theme_nom} — {st.session_state.lecon_nom}")
    st.progress(idx_affiche / total_questions)

    st.markdown(
        f"<p class='question-text'>Carte {idx_affiche} / {total_questions}</p>",
        unsafe_allow_html=True,
    )
    st.write(question["question"])

    key_show = f"show_answer_{idx_reel}"

    # Initialisation de l'état d'affichage selon la checkbox globale
    if key_show not in st.session_state:
        st.session_state[key_show] = bool(st.session_state.get("auto_show_answer", False))

    show = st.session_state[key_show]

    # Bouton manuel pour basculer
    if st.button("👀 Afficher / cacher la réponse", use_container_width=True, key=f"btn_show_{idx_reel}"):
        show = not show
        st.session_state[key_show] = show

    if show:
        st.success(f"Réponse : {question['bonne_reponse']}")
        if question.get("explication"):
            st.info(question["explication"])

    if st.button("➡️ Carte suivante", use_container_width=True, key=f"btn_next_card_{idx_reel}"):
        if st.session_state.question_index < len(st.session_state.indices_questions) - 1:
            st.session_state.question_index += 1
        else:
            st.warning("Tu es arrivé à la fin des cartes de cette leçon.")

# -----------------------
# UI - Config générale
# -----------------------
st.set_page_config(
    page_title="QCM par leçon",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# CSS: dark-like + mobile friendly
st.markdown(
    """
    <style>
    /* Corps général en mode sombre */
    body {
        background-color: #0E1117;
        color: #FAFAFA;
    }

    .main {
        max-width: 700px;
        margin: 0 auto;
        padding: 0.5rem;
    }

    .question-text {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    /* Boutons full width et adaptés au tactile */
    button[kind="primary"], button[kind="secondary"], .stButton>button {
        width: 100% !important;
        padding: 0.7rem 1.2rem;
        font-size: 1rem;
    }

    /* Réduction de l'espace entre options radio pour mobile */
    .stRadio > div {
        gap: 0.25rem;
    }

    /* Media query simple pour écrans étroits */
    @media (max-width: 600px) {
        .question-text {
            font-size: 1.05rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📚 QCM par thème et leçon")
st.caption(f"Dossier des leçons : `{LESSONS_DIR}`")

st.sidebar.header("Configuration")

# Mode d'apprentissage : QCM ou Cartes
mode = st.sidebar.radio(
    "Mode d'apprentissage",
    ["QCM", "Cartes"],
    index=0,
)

# Paramètre global : afficher la réponse automatiquement (mode Cartes)
auto_show_answer = st.sidebar.checkbox(
    "Afficher la réponse automatiquement",
    value=False,
    key="auto_show_answer",
)
# auto_show_answer est stocké dans st.session_state["auto_show_answer"] automatiquement.[web:33][web:39]

# -----------------------
# Logique principale
# -----------------------
if not lessons_map:
    st.error(f"Aucune leçon trouvée dans le dossier '{LESSONS_DIR}'.")
else:
    themes = sorted(lessons_map.keys())
    theme_nom = st.sidebar.selectbox("Thème", ["-- Choisir --"] + themes)

    if theme_nom != "-- Choisir --":
        if theme_nom != st.session_state.theme_nom:
            st.session_state.theme_nom = theme_nom
            st.session_state.lecon_nom = None
            reset_quiz()

        lecons = sorted(lessons_map[theme_nom].keys())
        lecon_nom = st.sidebar.selectbox("Leçon", ["-- Choisir --"] + lecons)

        if lecon_nom != "-- Choisir --":
            if lecon_nom != st.session_state.lecon_nom:
                st.session_state.lecon_nom = lecon_nom
                reset_quiz()

            questions = st.session_state.questions_courantes
            total_dispo = len(questions)

            if total_dispo == 0:
                st.info("Aucune question dans cette leçon.")
            else:
                st.sidebar.markdown(f"**Questions disponibles : {total_dispo}**")

                options_nb_base = [25, 50, 75, 100]
                options_nb = [n for n in options_nb_base if n <= total_dispo]
                if not options_nb:
                    options_nb = [total_dispo]

                if (
                    st.session_state.nb_questions is None
                    or st.session_state.nb_questions > total_dispo
                    or st.session_state.nb_questions not in options_nb
                ):
                    st.session_state.nb_questions = options_nb[0] if options_nb[0] == total_dispo and total_dispo < 25 else min(25, total_dispo)
                    if st.session_state.nb_questions not in options_nb:
                        st.session_state.nb_questions = options_nb[0]

                nb_questions = st.sidebar.selectbox(
                    "Nombre de questions",
                    options_nb,
                    index=options_nb.index(st.session_state.nb_questions),
                )

                if nb_questions != st.session_state.nb_questions:
                    st.session_state.nb_questions = nb_questions

                    n = len(st.session_state.questions_courantes)
                    indices = list(range(n))
                    random.shuffle(indices)
                    st.session_state.indices_questions = indices[:st.session_state.nb_questions]

                    st.session_state.question_index = 0
                    st.session_state.etat_question = "en_cours"
                    st.session_state.derniere_reponse = None
                    st.session_state.derniere_correcte = None
                    st.session_state.reponses_utilisateur = {}
                    st.session_state.reponses_melangees = {}

                st.session_state.indices_questions = st.session_state.indices_questions[:st.session_state.nb_questions]

                question, total_questions, idx_reel = question_courante()

                if question is None:
                    st.info("Aucune question dans cette leçon.")
                else:
                    if mode == "QCM":
                        afficher_qcm(question, total_questions, idx_reel)
                    else:
                        # En mode carte, pas de score/validation, juste navigation + affichage selon auto_show_answer
                        st.session_state.etat_question = "en_cours"
                        afficher_carte(question, total_questions, idx_reel)

                    st.divider()
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("🔁 Recommencer cette leçon"):
                            reset_quiz()
                    with col_b:
                        if st.button("📋 Afficher toutes les questions"):
                            st.session_state.afficher_correction = not st.session_state.afficher_correction

                    if st.session_state.afficher_correction:
                        st.markdown("## 📋 Correction de la leçon")
                        for i_affiche, idx_reel_all in enumerate(st.session_state.indices_questions, start=1):
                            q = st.session_state.questions_courantes[idx_reel_all]
                            bonne = q["bonne_reponse"]
                            rep_user = st.session_state.reponses_utilisateur.get(idx_reel_all)

                            st.markdown(f"**{i_affiche}. {q['question']}**")
                            st.write(f"Bonne réponse : **{bonne}**")

                            if rep_user is not None:
                                if rep_user["correcte"]:
                                    st.success(f"Ta réponse : {rep_user['reponse']} ✅")
                                else:
                                    st.error(f"Ta réponse : {rep_user['reponse']} ❌")
                            else:
                                st.info("Pas encore répondu à cette question.")

                            if q.get("explication"):
                                st.caption(q["explication"])
                            st.markdown("---")

        else:
            st.info("Choisis une leçon dans la barre latérale.")
    else:
        st.info("Choisis d'abord un thème dans la barre latérale.")
