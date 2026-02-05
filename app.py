import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Title
st.set_page_config(page_title="Streamlit Azure Demo", layout="wide")
st.title("🎓 Système Universitaire - Démo Azure")

# Health check rapide
st.text("✅ App running")

# Configuration
CSV_PATH = "db.csv"

# Fonctions CRUD
def load_data():
    """Charger les données depuis le CSV"""
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    else:
        # Créer un DataFrame vide avec la structure attendue
        return pd.DataFrame(columns=[
            'id', 'nom', 'prenom', 'specialite', 'moyenne_generale',
            'age', 'date_inscription', 'email'
        ])

def save_data(df):
    """Sauvegarder les données dans le CSV"""
    df.to_csv(CSV_PATH, index=False)

# Initialisation des données
df = load_data()

# Sidebar pour les opérations CRUD
with st.sidebar:
    st.header("📝 Opérations CRUD")
    
    crud_operation = st.selectbox(
        "Choisir une opération",
        ["Afficher", "Créer", "Lire", "Mettre à jour", "Supprimer", "Rechercher"]
    )
    
    # Recherche rapide
    st.subheader("🔍 Recherche rapide")
    search_term = st.text_input("Rechercher un étudiant", placeholder="Nom, spécialité...")

# Afficher le DataFrame principal
st.subheader("📊 Données des étudiants")

if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    # Statistiques rapides
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Nombre d'étudiants", len(df))
    with col2:
        st.metric("Spécialités uniques", df['specialite'].nunique() if 'specialite' in df.columns else 0)
    with col3:
        st.metric("Moyenne générale", f"{df['moyenne_generale'].mean():.2f}" if 'moyenne_generale' in df.columns else "N/A")
    with col4:
        st.metric("Âge moyen", f"{df['age'].mean():.1f}" if 'age' in df.columns else "N/A")
    
    # Exemple graphique : moyenne par filière
    if 'specialite' in df.columns and 'moyenne_generale' in df.columns:
        fig = px.bar(df.groupby('specialite')['moyenne_generale'].mean().reset_index(),
                     x='specialite', y='moyenne_generale',
                     title="📈 Moyenne générale par filière")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucune donnée disponible. Commencez par ajouter des étudiants.")

# Opérations CRUD
st.divider()

if crud_operation == "Créer":
    st.subheader("➕ Ajouter un nouvel étudiant")
    
    with st.form("create_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            specialite = st.selectbox(
                "Spécialité",
                ["Informatique", "Mathématiques", "Physique", "Chimie", "Biologie", "Économie"]
            )
        
        with col2:
            moyenne = st.slider("Moyenne générale", 0.0, 20.0, 12.0, 0.5)
            age = st.number_input("Âge", 18, 40, 20)
            email = st.text_input("Email")
        
        submitted = st.form_submit_button("Ajouter l'étudiant")
        
        if submitted:
            if nom and prenom:
                new_id = df['id'].max() + 1 if 'id' in df.columns and len(df) > 0 else 1
                new_student = {
                    'id': new_id,
                    'nom': nom,
                    'prenom': prenom,
                    'specialite': specialite,
                    'moyenne_generale': moyenne,
                    'age': age,
                    'date_inscription': datetime.now().strftime("%Y-%m-%d"),
                    'email': email if email else f"{prenom.lower()}.{nom.lower()}@univ.fr"
                }
                
                # Ajouter le nouvel étudiant
                new_df = pd.DataFrame([new_student])
                df = pd.concat([df, new_df], ignore_index=True)
                save_data(df)
                
                st.success(f"Étudiant {prenom} {nom} ajouté avec succès !")
                st.rerun()
            else:
                st.error("Le nom et prénom sont obligatoires")

elif crud_operation == "Mettre à jour":
    st.subheader("✏️ Mettre à jour un étudiant")
    
    if not df.empty:
        # Sélectionner un étudiant
        student_names = df.apply(lambda x: f"{x['id']} - {x['prenom']} {x['nom']}", axis=1)
        selected_student = st.selectbox(
            "Sélectionner un étudiant à modifier",
            student_names
        )
        
        if selected_student:
            student_id = int(selected_student.split(" - ")[0])
            student_data = df[df['id'] == student_id].iloc[0]
            
            with st.form("update_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nom = st.text_input("Nom", value=student_data['nom'])
                    prenom = st.text_input("Prénom", value=student_data['prenom'])
                    specialite = st.selectbox(
                        "Spécialité",
                        ["Informatique", "Mathématiques", "Physique", "Chimie", "Biologie", "Économie"],
                        index=["Informatique", "Mathématiques", "Physique", "Chimie", "Biologie", "Économie"].index(student_data['specialite'])
                        if student_data['specialite'] in ["Informatique", "Mathématiques", "Physique", "Chimie", "Biologie", "Économie"]
                        else 0
                    )
                
                with col2:
                    moyenne = st.slider("Moyenne générale", 0.0, 20.0, float(student_data['moyenne_generale']), 0.5)
                    age = st.number_input("Âge", 18, 40, int(student_data['age']))
                    email = st.text_input("Email", value=student_data['email'])
                
                submitted = st.form_submit_button("Mettre à jour")
                
                if submitted:
                    # Mettre à jour les données
                    df.loc[df['id'] == student_id, 'nom'] = nom
                    df.loc[df['id'] == student_id, 'prenom'] = prenom
                    df.loc[df['id'] == student_id, 'specialite'] = specialite
                    df.loc[df['id'] == student_id, 'moyenne_generale'] = moyenne
                    df.loc[df['id'] == student_id, 'age'] = age
                    df.loc[df['id'] == student_id, 'email'] = email
                    
                    save_data(df)
                    st.success(f"Étudiant {prenom} {nom} mis à jour avec succès !")
                    st.rerun()
    else:
        st.info("Aucun étudiant à mettre à jour")

elif crud_operation == "Supprimer":
    st.subheader("🗑️ Supprimer un étudiant")
    
    if not df.empty:
        # Sélectionner un étudiant
        student_names = df.apply(lambda x: f"{x['id']} - {x['prenom']} {x['nom']} ({x['specialite']})", axis=1)
        selected_student = st.selectbox(
            "Sélectionner un étudiant à supprimer",
            student_names
        )
        
        if selected_student:
            student_id = int(selected_student.split(" - ")[0])
            student_data = df[df['id'] == student_id].iloc[0]
            
            st.warning(f"Vous allez supprimer : **{student_data['prenom']} {student_data['nom']}**")
            
            if st.button("Confirmer la suppression", type="primary"):
                # Supprimer l'étudiant
                df = df[df['id'] != student_id]
                save_data(df)
                
                st.success("Étudiant supprimé avec succès !")
                st.rerun()
    else:
        st.info("Aucun étudiant à supprimer")

elif crud_operation == "Rechercher" or search_term:
    st.subheader("🔍 Résultats de recherche")
    
    if search_term:
        search_term_lower = search_term.lower()
        # Rechercher dans toutes les colonnes textuelles
        mask = pd.Series(False, index=df.index)
        for col in df.select_dtypes(include=['object']).columns:
            mask = mask | df[col].astype(str).str.lower().str.contains(search_term_lower, na=False)
        
        results = df[mask]
        
        if not results.empty:
            st.write(f"**{len(results)}** résultat(s) trouvé(s) pour '{search_term}'")
            st.dataframe(results, use_container_width=True)
        else:
            st.info(f"Aucun résultat trouvé pour '{search_term}'")

elif crud_operation == "Lire":
    st.subheader("👁️ Détails d'un étudiant")
    
    if not df.empty:
        # Sélectionner un étudiant
        student_names = df.apply(lambda x: f"{x['id']} - {x['prenom']} {x['nom']}", axis=1)
        selected_student = st.selectbox(
            "Sélectionner un étudiant pour voir les détails",
            student_names
        )
        
        if selected_student:
            student_id = int(selected_student.split(" - ")[0])
            student_data = df[df['id'] == student_id].iloc[0]
            
            # Afficher les détails
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**ID :** {student_data['id']}")
                st.info(f"**Nom complet :** {student_data['prenom']} {student_data['nom']}")
                st.info(f"**Spécialité :** {student_data['specialite']}")
            
            with col2:
                st.info(f"**Moyenne générale :** {student_data['moyenne_generale']}")
                st.info(f"**Âge :** {student_data['age']}")
                st.info(f"**Email :** {student_data['email']}")
            
            if 'date_inscription' in student_data:
                st.info(f"**Date d'inscription :** {student_data['date_inscription']}")

# Bouton pour exporter les données
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Exporter les données (CSV)"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Télécharger CSV",
            data=csv,
            file_name=f"etudiants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("🔄 Rafraîchir les données"):
        df = load_data()
        st.rerun()

with col3:
    if st.button("🗑️ Supprimer toutes les données"):
        if st.checkbox("Je confirme vouloir supprimer TOUTES les données"):
            df = pd.DataFrame()
            save_data(df)
            st.warning("Toutes les données ont été supprimées !")
            st.rerun()

# Affichage des données brutes
with st.expander("🔧 Afficher les données brutes"):
    st.write(df)
    
    # Télécharger un nouveau fichier
    uploaded_file = st.file_uploader("Télécharger un nouveau fichier CSV", type=['csv'])
    if uploaded_file is not None:
        try:
            new_df = pd.read_csv(uploaded_file)
            df = new_df
            save_data(df)
            st.success("Fichier téléchargé et données mises à jour !")
            st.rerun()
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")