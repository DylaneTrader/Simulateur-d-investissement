# Guide de Test - Simulateur d'Investissement CGF GESTION

## Fonctionnalités Implémentées

### ✅ 1. Exportation PDF
- **Génération automatique de rapports PDF professionnels**
- **Contenu du PDF:**
  - En-tête CGF GESTION
  - Informations commerciales (date, interlocuteur, client, pays)
  - Paramètres de simulation (tableau)
  - Résultats financiers détaillés (tableau avec métriques)
  - Équivalents de versements (mensuel, trimestriel, semestriel, annuel)
  - Graphiques:
    - Évolution du portefeuille (courbe)
    - Distribution du capital (camembert)
  - Analyse et commentaires automatiques
  - Pied de page avec informations CGF GESTION

### ✅ 2. Envoi par Email
- **Format de l'objet:** `CGF GESTION - Simulation d'investissement au {date}`
- **Expéditeur:** Email de l'interlocuteur (commercial)
- **Destinataire:** Email du client
- **Contenu:**
  - Résumé des résultats de la simulation
  - Commentaire personnalisé (optionnel)
  - PDF en pièce jointe
- **Configuration:** Support SMTP via variables d'environnement (.env)

---

## Comment Tester

### Prérequis

1. **Installer les dépendances:**
   ```bash
   cd /home/runner/work/Simulateur-d-investissement/Simulateur-d-investissement
   pip install -r requirements.txt
   ```

2. **Vérifier l'installation:**
   ```bash
   python -c "import reportlab; import matplotlib; print('OK')"
   ```

---

### Test 1: Téléchargement PDF (Ne nécessite AUCUNE configuration)

#### Étape par étape:

1. **Lancer l'application:**
   ```bash
   streamlit run app.py
   ```

2. **Remplir les informations dans la barre latérale:**
   - **Interlocuteur:** Votre nom (ex: "Jean Dupont")
   - **Nom du client:** Nom test (ex: "Marie Martin")
   - **Pays:** Sélectionnez un pays UEMOA

3. **Naviguer vers "Simulation"** (menu latéral)

4. **Configurer les paramètres:**
   - Choisir le mode de calcul (ex: "Montant Final")
   - Remplir les champs nécessaires:
     - Montant Initial: 100 000 FCFA
     - Versement Mensuel: 50 000 FCFA
     - Rendement Annuel: 5%
     - Horizon: 10 ans

5. **Cliquer sur "Lancer la simulation"**

6. **Vérifier l'affichage:**
   - ✅ Résultats affichés (cartes avec métriques)
   - ✅ Graphiques interactifs visibles
   - ✅ Section "📤 Exporter le rapport" en bas

7. **Télécharger le PDF:**
   - Cliquer sur "📥 Télécharger le rapport PDF"
   - Le fichier se télécharge automatiquement
   - Nom du fichier: `Simulation_CGF_GESTION_YYYYMMDD_HHMMSS.pdf`

8. **Vérifier le contenu du PDF:**
   - ✅ En-tête "CGF GESTION"
   - ✅ Informations commerciales (interlocuteur, client, pays)
   - ✅ Tableau des paramètres
   - ✅ Tableau des résultats financiers
   - ✅ Tableau des équivalents de versements
   - ✅ Graphique d'évolution (courbe)
   - ✅ Graphique en camembert (distribution)
   - ✅ Commentaire automatique
   - ✅ Pied de page avec date/heure

**Résultat attendu:** ✅ PDF généré et téléchargé sans erreur, contenu complet et professionnel

---

### Test 2: Envoi par Email (Nécessite configuration SMTP)

#### Configuration préalable (Gmail)

1. **Créer un mot de passe d'application Gmail:**
   
   a. Aller sur https://myaccount.google.com/security
   
   b. **Activer la validation en 2 étapes** (si pas déjà fait)
   
   c. Aller sur https://myaccount.google.com/apppasswords
   
   d. Créer un nouveau mot de passe:
      - Application: "Autre (nom personnalisé)"
      - Nom: "CGF GESTION Simulateur"
   
   e. **Copier le mot de passe** (format: xxxx xxxx xxxx xxxx)

2. **Configurer le fichier .env:**
   ```bash
   cd /home/runner/work/Simulateur-d-investissement/Simulateur-d-investissement
   cp .env.example .env
   nano .env  # ou votre éditeur préféré
   ```
   
   **Remplir avec vos valeurs:**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=votre.email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx
   ```
   
   ⚠️ **Important:** 
   - Remplacer `votre.email@gmail.com` par votre vraie adresse Gmail
   - Remplacer `xxxx xxxx xxxx xxxx` par le mot de passe d'application (garder les espaces ou les retirer)
   - Le fichier `.env` est dans `.gitignore` (ne sera pas commité)

3. **Relancer l'application** (pour charger les variables):
   ```bash
   streamlit run app.py
   ```

#### Test de l'envoi d'email:

1. **Effectuer une simulation** (comme dans Test 1)

2. **Dans la section "📤 Exporter le rapport":**
   - Colonne de gauche: Bouton PDF
   - **Colonne de droite:** Section "📧 Envoyer par email"

3. **Cliquer sur "📧 Configurer l'envoi"** pour déplier le formulaire

4. **Remplir le formulaire:**
   - **Email de l'interlocuteur (expéditeur):** Votre email Gmail (celui configuré dans .env)
   - **Email du client (destinataire):** Email de test (peut être le même pour tester)
   - **Commentaire personnalisé (optionnel):** Message facultatif

5. **Cliquer sur "📧 Envoyer le rapport"**

6. **Vérifier le résultat:**
   
   **✅ En cas de succès:**
   - Message vert: "✅ Email envoyé avec succès à [email]"
   
   **❌ En cas d'erreur:**
   - Message d'erreur détaillé avec la cause

7. **Vérifier la réception de l'email:**
   - Ouvrir la boîte mail du destinataire
   - Vérifier les spams si nécessaire
   
   **Contenu de l'email:**
   - ✅ Objet: "CGF GESTION - Simulation d'investissement au DD/MM/YYYY"
   - ✅ Corps de l'email avec résumé ou commentaire personnalisé
   - ✅ PDF en pièce jointe
   - ✅ Nom de la pièce jointe: `Simulation_CGF_GESTION_DD-MM-YYYY.pdf`

**Résultat attendu:** ✅ Email reçu avec PDF joint, contenu correct

---

### Test 3: Cas d'erreur et validations

#### Test 3.1: Email sans configuration SMTP

1. **Ne PAS créer de fichier .env** (ou le renommer temporairement)
2. Essayer d'envoyer un email
3. **Résultat attendu:** Message d'erreur expliquant que la configuration SMTP est manquante

#### Test 3.2: Email avec mauvais mot de passe

1. Modifier `.env` avec un mauvais mot de passe
2. Relancer l'app et essayer d'envoyer
3. **Résultat attendu:** Message d'erreur d'authentification avec instructions pour créer un mot de passe d'application

#### Test 3.3: Champs email vides

1. Laisser les champs email vides
2. Cliquer sur "Envoyer le rapport"
3. **Résultat attendu:** ⚠️ Message: "Veuillez renseigner les deux adresses email"

#### Test 3.4: PDF sans informations commerciales

1. Laisser les champs de la sidebar vides (interlocuteur, client)
2. Effectuer une simulation et télécharger le PDF
3. **Résultat attendu:** PDF généré avec "N/A" pour les champs vides

---

## Problèmes Courants et Solutions

### ❌ Le bouton PDF n'apparaît pas
**Cause:** La simulation n'a pas été lancée
**Solution:** Cliquer sur "Lancer la simulation" d'abord

### ❌ Erreur "No module named 'reportlab'"
**Cause:** Dépendances non installées
**Solution:**
```bash
pip install -r requirements.txt
```

### ❌ Email non reçu
**Causes possibles:**
- Email dans les spams → Vérifier le dossier spam
- Mauvais mot de passe → Utiliser un mot de passe d'application
- Configuration SMTP incorrecte → Vérifier le fichier .env
- Validation 2 étapes non activée → Activer dans les paramètres Google

**Solution:** Vérifier les variables dans `.env` et relancer l'app

### ❌ Erreur "Authentication failed"
**Cause:** Mot de passe d'application incorrect ou validation 2 étapes non activée
**Solution:**
1. Vérifier que la validation en 2 étapes est activée
2. Générer un nouveau mot de passe d'application
3. Copier-coller sans erreur dans .env
4. Relancer l'application

### ❌ Erreur "SMTP_USERNAME not set"
**Cause:** Le fichier .env n'est pas chargé ou n'existe pas
**Solution:**
1. Vérifier que le fichier `.env` existe à la racine du projet
2. Vérifier qu'il contient toutes les variables requises
3. Relancer l'application

### ❌ PDF vide ou incomplet
**Cause:** Erreur dans la génération des graphiques
**Solution:** Vérifier les logs dans la console, réinstaller matplotlib

---

## Fichiers Modifiés/Créés

### Nouveaux fichiers:
- ✅ `core/export.py` - Module d'exportation PDF et email
- ✅ `.env.example` - Template de configuration SMTP

### Fichiers modifiés:
- ✅ `requirements.txt` - Ajout de reportlab, matplotlib, python-dotenv
- ✅ `ui/layout.py` - Ajout de la section d'exportation dans display_results()
- ✅ `app.py` - Chargement automatique du fichier .env
- ✅ `GUIDE_TEST.md` - Ce guide complet

---

## Validation Finale - Checklist

Avant de valider l'implémentation, vérifier:

### Fonctionnalité PDF:
- [ ] Le bouton de téléchargement PDF s'affiche après la simulation
- [ ] Le PDF se télécharge sans erreur
- [ ] Le PDF contient toutes les sections (info, paramètres, résultats, graphiques)
- [ ] Les graphiques sont lisibles et en couleur
- [ ] Les tableaux sont bien formatés
- [ ] Les montants sont au bon format (FCFA, séparateurs)
- [ ] La mise en page est professionnelle

### Fonctionnalité Email:
- [ ] Le formulaire d'envoi email s'affiche
- [ ] Les champs email sont validés
- [ ] L'email est envoyé avec succès (avec config SMTP)
- [ ] L'objet de l'email suit le format requis
- [ ] Le résumé est inclus dans le corps
- [ ] Le PDF est bien attaché
- [ ] Les messages d'erreur sont clairs et utiles

### Configuration:
- [ ] Le fichier .env.example est présent et documenté
- [ ] Les variables d'environnement sont bien chargées
- [ ] .env est dans .gitignore
- [ ] Les dépendances sont dans requirements.txt

### Documentation:
- [ ] GUIDE_TEST.md est complet et à jour
- [ ] Instructions claires pour la configuration Gmail
- [ ] Section troubleshooting complète
- [ ] Exemples et captures d'écran (si disponibles)

---

## Notes Techniques

### Dépendances ajoutées:
```
reportlab>=4.0.0     # Génération PDF
matplotlib>=3.7.0    # Graphiques pour PDF
python-dotenv>=1.0.0 # Variables d'environnement
```

### Backend matplotlib:
Le module utilise le backend 'Agg' (sans interface graphique) pour générer les graphiques en mémoire, compatible avec les environnements serveur.

### Format des emails:
- **Objet:** `CGF GESTION - Simulation d'investissement au {date}`
- **Date:** Format DD/MM/YYYY
- **Encodage:** UTF-8
- **Type MIME:** multipart/mixed (texte + PDF)

### Sécurité:
- ⚠️ Ne JAMAIS commiter le fichier .env
- ⚠️ Utiliser des mots de passe d'application (pas le mot de passe principal)
- ⚠️ Les credentials SMTP sont en variables d'environnement uniquement

---

## Support

Pour toute question ou problème:
1. Vérifier les logs dans la console
2. Consulter la section "Problèmes Courants"
3. Vérifier que toutes les dépendances sont installées
4. Tester d'abord le PDF (ne nécessite pas de config)
5. Puis tester l'email (après configuration SMTP)

**Développé par:** Dylane Emmanuel Reyane NDOUDY-BAMOUENIZO pour CGF GESTION
**Date:** Décembre 2025

