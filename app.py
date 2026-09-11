import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuration de la page Streamlit
st.set_page_config(page_title="Or Guinée-Dubaï Dash", page_icon="📊", layout="wide")

DB_FILE = "historique_operations.csv"
ONCE_EN_GRAMMES = 31.1035

# ==========================================
# SÉCURITÉ : CONFIGURATION DU MOT DE PASSE
# ==========================================
MOT_DE_PASSE_CORRECT = "Sobemetal2026"  # Vous pouvez modifier ce mot de passe ici

if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

# Écran de connexion si l'utilisateur n'est pas connecté
if not st.session_state["authentifie"]:
    st.title("🔒 Accès Sécurisé - Sobemetal")
    st.markdown("---")
    
    col_login, _ = st.columns(2)  # CORRIGÉ ICI
    with col_login:
        mot_de_passe_saisi = st.text_input("Entrez le mot de passe de l'entreprise :", type="password")
        if st.button("Se connecter", use_container_width=True):
            if mot_de_passe_saisi == MOT_DE_PASSE_CORRECT:
                st.session_state["authentifie"] = True
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect. Veuillez réessayer.")
    st.stop()

# ==========================================
# FONCTIONS DE GESTION DE LA BASE DE DONNÉES
# ==========================================
def charger_historique():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        columns = [
            "Date/Heure", "Poids Pur (g)", "transport", "melting", "testing", "cjv",
            "Cout d'achat Global(USD)", "Coût Total (USD)", "Chiffre Affaires (USD)", 
            "Profit Net (USD)", "Marge (%)"
        ]
        return pd.DataFrame(columns=columns)

def sauvegarder_operation(donnees):
    df_actuel = charger_historique()
    df_nouvel = pd.DataFrame([donnees])
    df_final = pd.concat([df_actuel, df_nouvel], ignore_index=True)
    df_final.to_csv(DB_FILE, index=False)

def effacer_historique():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

# INITIALISATION DE LA MÉMOIRE INTERNE (Session State) pour bloquer le gel
if "cours_manuel" not in st.session_state:
    st.session_state["cours_manuel"] = 2500.0
if "prix_achat_in" not in st.session_state:
    st.session_state["prix_achat_in"] = 64000.0
if "poids_brut_in" not in st.session_state:
    st.session_state["poids_brut_in"] = 1000.0

# ==========================================
# CONTENU PRINCIPAL DE L'APPLICATION (SOBEMETAL)
# ==========================================
with st.sidebar:
    st.image("https://icons8.com", width=50)
    st.markdown("### **Espace Sobemetal**")
    if st.button("🔒 Se déconnecter", use_container_width=True):
        st.session_state["authentifie"] = False
        st.rerun()

st.title("🌟 Système de Pilotage Data : Achat Or Guinée ➡️ Vente Dubaï")
st.caption("Toutes les valeurs financières sont exprimées en Dollars Américains ($ USD).")
st.markdown("---")

# 1. ZONE DE SAISIE MANUELLE DU COURS DE L'OR
st.subheader("🎛️ Configuration du Marché")

cours_or_usd_oz = st.number_input(
    "📈 Entrez le cours mondial de l'Or (USD / once)", 
    min_value=0.0, 
    value=float(st.session_state["cours_manuel"]), 
    step=10.0,
    key="cours_input"
)
st.session_state["cours_manuel"] = cours_or_usd_oz

# Calcul dynamique du prix par gramme
cours_or_usd_gramme = round(cours_or_usd_oz / ONCE_EN_GRAMMES, 2)

# AFFICHAGE DES INDICATEURS CLÉS EN TEMPS RÉEL
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"### 📊 Cours de l'Or Saisi : **{cours_or_usd_oz:,.2f} $ / once**")
with col2:
    st.markdown(f"### 🧪 Équivalent Gramme 24K : **{cours_or_usd_gramme:,.2f} $ / g**")

st.markdown("---")

# 2. SIMULATEUR DE MARGE ET D'ARBITRAGE
st.subheader("💡 Simulateur de Marge par Opération")

c1, c2 = st.columns(2)

with c1:
    st.markdown("### 🇬🇳 Phase 1 : Achat(Guinée)")
    cout_achat_pur_usd = st.number_input(
        "💰 Cout d'Achat Global (USD)", 
        min_value=0.0, 
        value=float(st.session_state["prix_achat_in"]), 
        step=1000.0, 
        key="prix_achat_widget"
    )
    st.session_state["prix_achat_in"] = cout_achat_pur_usd

with c2:
    st.markdown("### 🇦🇪 Phase 2 : Service & Vente (Dubaï)")
    transport_intl_usd = st.number_input("✈️ Transport international sécurisé (Brinks/DHL en USD)", min_value=0.0, value=1200.0, key="trans_in")
    testing_dubai_usd = st.number_input("🧪 Testing / Contre-expertise au DMCC Dubaï (en USD)", min_value=0.0, value=150.0, key="test_in")
    melting_dubai_usd = st.number_input("🔥 Frais de fusion / raffinage à Dubaï (en USD)", min_value=0.0, value=50.0, key="melt_in")
    cjv_dubai_usd = st.number_input("💎 CJV / Certification & Assurance Dubaï (en USD)", min_value=0.0, value=100.0, key="cjv_in")
    
    poids_pur_attendu = st.number_input(
        "Poids d'or pur Vendu (en grammes)", 
        min_value=0.0, 
        value=float(st.session_state["poids_brut_in"]), 
        step=100.0, 
        key="poids_brut_widget"
    )
    st.session_state["poids_brut_in"] = poids_pur_attendu
    
    st.info(f"📈 **Prix de revente appliqué à Dubaï : {cours_or_usd_gramme:,.2f} $ / g pur**")

# CALCULS FINANCIERS SANS VERROU
chiffre_affaires_usd = poids_pur_attendu * cours_or_usd_gramme
total_couts_operation_usd = transport_intl_usd + testing_dubai_usd + melting_dubai_usd + cout_achat_pur_usd + cjv_dubai_usd
profit_net_usd = chiffre_affaires_usd - total_couts_operation_usd
marge_pourcent = (profit_net_usd / chiffre_affaires_usd) * 100 if chiffre_affaires_usd > 0 else 0.0

st.markdown("---")

# 3. PANNEAU DE RÉSULTATS VISUELS (CARTES INTERACTIVES)
st.subheader("📊 Rapport Financier de l'Opération")

col_res1, col_res2, col_res3, col_res4 = st.columns(4)

card_style = """
<div style="
    background-color: #1e293b; 
    padding: 20px; 
    border-radius: 10px; 
    border-left: 5px solid {bordure_couleur};
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    margin-bottom: 10px;">
    <p style="margin:0; font-size:14px; color:#94a3b8; font-weight:bold;">{label}</p>
    <h2 style="margin:5px 0 0 0; font-size:24px; color:#f8fafc;">{valeur}</h2>
    <p style="margin:5px 0 0 0; font-size:13px; color:{delta_color};">{delta}</p>
</div>
"""

with col_res1:
    st.markdown(card_style.format(
        label="⚖️ POIDS PUR ATTENDU", 
        valeur=f"{poids_pur_attendu:,.2f} g", 
        delta=f"Poids traité : {poids_pur_attendu:,.2f} g", 
        delta_color="#94a3b8",
        bordure_couleur="#3b82f6"
    ), unsafe_allow_html=True)

with col_res2:
    st.markdown(card_style.format(
        label="💸 TOTAL DES COÛTS", 
        valeur=f"{total_couts_operation_usd:,.2f} $", 
        delta=f"Total charges engagées", 
        delta_color="#94a3b8",
        bordure_couleur="#f59e0b"
    ), unsafe_allow_html=True)

with col_res3:
    couleur_profit = "#22c55e" if profit_net_usd > 0 else "#ef4444"
    st.markdown(card_style.format(
        label="📈 MARGE COMMERCIALE", 
        valeur=f"{marge_pourcent:,.2f} %", 
        delta=f"{profit_net_usd:+,.2f} $ (Net)", 
        delta_color=couleur_profit,
        bordure_couleur=couleur_profit
    ), unsafe_allow_html=True)

with col_res4:
    st.markdown(card_style.format(
        label="💰 CHIFFRE D'AFFAIRES", 
        valeur=f"{chiffre_affaires_usd:,.2f} $", 
        delta=f"CA Récupéré à Dubaï",
        delta_color="#94a3b8",
        bordure_couleur="#8b5cf6"
    ), unsafe_allow_html=True)

if profit_net_usd > 0:
    st.success(f"🚀 **Bénéfice Net Estimé : {profit_net_usd:,.2f} $**")
else:
    st.error(f"⚠️ **Alerte Perte Estimée : {profit_net_usd:,.2f} $**")

# 4. ACTION DE SAUVEGARDE
st.markdown("### 💾 Sauvegarde dans l'historique")
col_date, col_save = st.columns(2)  # CORRIGÉ ICI (Ajout du chiffre 2)

with col_date:
    date_choisie = st.date_input("🗓️ Sélectionner la date de l'opération", datetime.now())

with col_save:
    st.write("") 
    st.write("") 
    if st.button("Enregistrer cette simulation dans la base de données", use_container_width=True):
        heure_actuelle = datetime.now().strftime("%H:%M:%S")
        nouvelle_entree = {
            "Date/Heure": f"{date_choisie.strftime('%Y-%m-%d')} {heure_actuelle}",
            "Poids Pur (g)": round(poids_pur_attendu, 2),
            "transport": round(transport_intl_usd, 2),
            "melting": round(melting_dubai_usd, 2),
            "testing": round(testing_dubai_usd, 2),
            "cjv": round(cjv_dubai_usd, 2),
            "Cout d'achat Global(USD)": cout_achat_pur_usd,
            "Coût Total (USD)": round(total_couts_operation_usd, 2),
            "Chiffre Affaires (USD)": round(chiffre_affaires_usd, 2),
            "Profit Net (USD)": round(profit_net_usd, 2),
            "Marge (%)": round(marge_pourcent, 2)
        }
        sauvegarder_operation(nouvelle_entree)
        st.success("✅ L'opération a été enregistrée avec succès dans le fichier Excel/CSV !")
        st.rerun()

st.markdown("---")

# 5. GRAPH_VISUAL ET HISTORIQUE COMPLET
df_historique = charger_historique()

if not df_historique.empty:
    st.subheader("📈 Évolution des Profits Nets cumulés ($ USD)")
    df_graph = df_historique.copy()
    df_graph = df_graph.set_index("Date/Heure")
    st.line_chart(df_graph["Profit Net (USD)"])
    
    st.markdown("---")
    
    col_table, col_clear = st.columns([4, 1])
    with col_table:
        st.subheader("📋 Historique des Lots Enregistrés")
        
    with col_clear:
        confirmer_effacement = st.checkbox("⚠️ Activer la suppression")
        if st.button("❌ Effacer l'historique", disabled=not confirmer_effacement, type="primary"):
            effacer_historique()
            st.success("Base de données réinitialisée !")
            st.rerun()

    st.dataframe(df_historique.iloc[::-1], use_container_width=True)
    
    csv_data = df_historique.to_csv(index=False).encode('utf-8')
