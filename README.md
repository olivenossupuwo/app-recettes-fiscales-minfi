# Système d'Analyse et de Prévision des Recettes Fiscales du Cameroun

Application Streamlit pour le Ministère des Finances (MINFI) du Cameroun.

Outil d'aide à la décision construit sur la base d'un mémoire portant sur la
prévision des recettes fiscales par les méthodes de Machine Learning
(XGBoost, Random Forest, SVR, Elastic Net, Lasso, Ridge).

## Lancement

```bash
cd app_recettes_fiscales
python -m venv venv

# Windows :   venv\Scripts\activate
# Linux/Mac : source venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

L'application s'ouvre sur http://localhost:8501.

## Structure du projet

```
app_recettes_fiscales/
├── app.py                 Application Streamlit (interface)
├── utils.py               Logique métier (modèles, KPIs, rapports)
├── requirements.txt       Dépendances Python
├── README.md
├── assets/
│   └── minfi_logo.jpeg    Logo officiel MINFI
└── data/
    ├── modeles/           Modèles XGBoost (.pkl) pour H3, H6, H12
    ├── excel/             Données du mémoire + prévisions précalculées
    └── figures/           Graphiques SHAP et feature importance
```

## Onglets

1. **Accueil** : présentation, objectifs, tableau récapitulatif des modèles
2. **Importation** : chargement CSV/Excel avec aperçu interactif
3. **Tableau de bord** :
   - *Visualisation historique* : KPIs (dernière valeur, total annuel,
     moyenne 12 mois, coefficient de variation), évolution mensuelle/annuelle,
     heatmap année×mois, cumul YTD par année, profil saisonnier
   - *Prévision* : sélection de l'horizon (3, 6 ou 12 mois), choix de 1, 2 ou
     3 ans pour l'annuel, KPIs (total prévu, croissance attendue, précision,
     incertitude), graphique avec IC 95%, validation 2024, graphes SHAP
4. **Rapport** : génération Word ou PDF avec en-tête institutionnel MINFI,
   sections à inclure, niveau de détail adaptatif

## Modèles retenus

| Horizon | Modèle | RMSE (Mds) | MAE | MAPE | R² |
|---------|--------|------------|-----|------|-----|
| 3 mois  | XGBoost | 25.58 | 20.42 | 6.04 % | 0.853 |
| 6 mois  | XGBoost | 25.58 | 20.42 | 6.04 % | 0.853 |
| 12 mois | XGBoost | 23.32 | 18.19 | 5.44 % | 0.877 |

XGBoost domine simultanément sur les quatre métriques pour les trois horizons,
ce qui justifie sa sélection systématique.

## Format des données importées

- Fichier du mémoire (`Base_de_Travail_modelisation.xlsx`) reconnu automatiquement
- Ou tout CSV/Excel avec :
  - Une colonne de date (`Date`, `Mois`, `period`, ...)
  - Une colonne `Recettes_fiscales` (en Mds FCFA)
  - Optionnellement les 14 variables exogènes du mémoire

## Dépendances principales

- streamlit, streamlit-option-menu
- pandas, numpy, plotly, matplotlib
- xgboost, scikit-learn
- python-docx, reportlab (génération de rapports)
- joblib, openpyxl

## Notes de design

Interface inspirée du design Acme dashboard : palette navy/violet,
typographie Plus Jakarta Sans, icônes line-style Bootstrap, cartes KPI
avec carrés colorés et accents.
