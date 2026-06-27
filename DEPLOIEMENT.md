# Guide de déploiement de l'application

## Option 1 : Streamlit Community Cloud (recommandé, gratuit)

C'est la solution la plus simple. L'application sera accessible publiquement à une URL du type
`https://votre-app.streamlit.app`.

### Prérequis
- Un compte GitHub (gratuit) : https://github.com/signup
- Un compte Streamlit (gratuit) : https://share.streamlit.io

### Étapes

#### 1. Créer un dépôt GitHub

1. Connecte-toi à GitHub et clique sur "New repository" en haut à droite.
2. Nomme le dépôt par exemple `app-recettes-fiscales-minfi`.
3. Mets-le en **Public** (obligatoire pour le plan gratuit de Streamlit Cloud).
4. NE coche PAS "Initialize with README" (on a déjà tous les fichiers).
5. Clique sur "Create repository".

#### 2. Pousser le code vers GitHub

Depuis le dossier `app_recettes_fiscales` sur ta machine, ouvre une invite de commandes et exécute :

```bash
cd C:\Users\EMMANUELLE\Desktop\app_recettes_fiscales

git init
git add .
git commit -m "Initial commit : application MINFI Recettes Fiscales"
git branch -M main
git remote add origin https://github.com/TON_NOM_UTILISATEUR/app-recettes-fiscales-minfi.git
git push -u origin main
```

Remplace `TON_NOM_UTILISATEUR` par ton identifiant GitHub.

Si tu n'as jamais utilisé git auparavant, installe-le depuis https://git-scm.com/download/win
et configure-le une fois pour toutes :

```bash
git config --global user.name "Ton Nom"
git config --global user.email "ton.email@example.com"
```

#### 3. Déployer sur Streamlit Cloud

1. Va sur https://share.streamlit.io et connecte-toi avec ton compte GitHub.
2. Clique sur "New app" en haut à droite.
3. Sélectionne :
   - **Repository** : ton dépôt `app-recettes-fiscales-minfi`
   - **Branch** : `main`
   - **Main file path** : `app.py`
4. Clique sur "Deploy".

Le premier déploiement prend 3 à 5 minutes (installation de toutes les dépendances :
xgboost, plotly, reportlab, etc.). Une fois fini, l'application est en ligne.

#### 4. Partager le lien

Une fois déployée, l'URL est de la forme :
`https://app-recettes-fiscales-minfi-XXXXX.streamlit.app`

Tu peux la partager à n'importe qui.

### Mettre à jour l'application en ligne

À chaque modification locale du code, fais :

```bash
git add .
git commit -m "Description du changement"
git push
```

Streamlit Cloud redéploie automatiquement en moins d'une minute.

---

## Option 2 : Render (gratuit, plus de contrôle)

1. Crée un compte sur https://render.com (gratuit).
2. Pousse aussi ton code sur GitHub (cf. étapes 1-2 plus haut).
3. Dans Render, clique sur "New" puis "Web Service".
4. Connecte ton dépôt GitHub.
5. Configure :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
6. Clique sur "Create Web Service".

L'application sera accessible à l'URL `https://nom-du-service.onrender.com`.

Note : le plan gratuit de Render endort l'application après 15 minutes d'inactivité.
Le réveil prend environ 30 secondes lors de la prochaine visite.

---

## Option 3 : Hugging Face Spaces (gratuit, simple)

1. Crée un compte sur https://huggingface.co
2. Clique sur ton avatar puis "New Space".
3. Donne un nom au Space, choisis :
   - **SDK** : Streamlit
   - **Hardware** : CPU basic (gratuit)
4. Une fois créé, télécharge ton dossier complet via l'interface web ou via git :

```bash
git lfs install
git clone https://huggingface.co/spaces/TON_USER/nom-du-space
cd nom-du-space
# Copie tous les fichiers de app_recettes_fiscales/ ici
git add .
git commit -m "Initial commit"
git push
```

5. Pour les gros fichiers (modèles .pkl si > 10 Mo), utilise `git lfs track`.

L'application est accessible à `https://huggingface.co/spaces/TON_USER/nom-du-space`.

---

## Option 4 : Sur un serveur VPS (production)

Pour un déploiement institutionnel pérenne (recommandé pour usage MINFI), un VPS chez
DigitalOcean, OVH ou Scaleway (5 à 10 € / mois) est plus adapté.

Étapes générales :

1. Loue un VPS Ubuntu 22.04 (1 vCPU, 2 Go RAM suffisent).
2. Connecte-toi en SSH et installe Python 3.11, nginx, certbot.
3. Clone le projet, crée le venv, installe les dépendances.
4. Configure systemd pour faire tourner streamlit en service permanent :

```ini
# /etc/systemd/system/recettes-fiscales.service
[Unit]
Description=Application Recettes Fiscales MINFI
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/app_recettes_fiscales
ExecStart=/home/ubuntu/app_recettes_fiscales/venv/bin/streamlit run app.py --server.port=8501 --server.address=127.0.0.1
Restart=always

[Install]
WantedBy=multi-user.target
```

5. Configure nginx comme reverse proxy avec HTTPS (Let's Encrypt).
6. Active le service : `sudo systemctl enable --now recettes-fiscales`.

---

## Limites du plan gratuit Streamlit Cloud

- 1 Go de RAM par application
- Application publique (le code source est visible sur GitHub)
- Endormissement après 7 jours sans visite

Si tu as besoin de confidentialité ou de plus de ressources, le plan payant
Streamlit for Teams (20 $/mois) permet les applications privées, ou bien
choisis l'option VPS.

---

## Vérification avant déploiement

Avant de pousser, teste localement que tout fonctionne :

```bash
streamlit run app.py
```

Vérifie :
- L'application se lance sans erreur
- Toutes les pages s'affichent (Accueil, Importation, Tableau de bord, Rapport)
- La génération de rapport Word et PDF fonctionne
- Les graphiques s'affichent correctement
