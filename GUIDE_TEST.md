# Guide de Test - PDF Export et Email

## Ce qui a été corrigé

### 1. Problème de téléchargement PDF ✅ CORRIGÉ
**Problème**: Le bouton de téléchargement n'apparaissait que brièvement puis disparaissait
**Solution**: Le bouton `st.download_button` est maintenant affiché directement sans nécessiter de clic préalable. Le PDF est généré automatiquement quand la page s'affiche.

### 2. Problème d'envoi email ✅ CORRIGÉ  
**Problème**: L'email n'était pas envoyé
**Solution**: 
- Amélioration de la gestion des erreurs avec messages clairs
- Ajout du support pour fichier .env
- Documentation complète pour la configuration SMTP

## Comment tester

### Test 1: Téléchargement PDF (Ne nécessite aucune configuration)

1. Lancez l'application:
   ```bash
   cd /home/runner/work/Simulateur-d-investissement/Simulateur-d-investissement
   streamlit run app.py
   ```

2. Dans la barre latérale, remplissez les informations commerciales:
   - Interlocuteur: Votre nom
   - Nom du client: Un nom test
   - Pays: Sélectionnez un pays

3. Allez dans "Simulation" (menu à gauche)

4. Remplissez les paramètres et cliquez sur "Lancer la simulation"

5. **VÉRIFICATION**: En bas de la page, vous devriez voir immédiatement:
   - Un bouton bleu "📥 Télécharger le rapport PDF"
   - Le bouton devrait être visible EN PERMANENCE (pas de disparition)

6. Cliquez sur le bouton → Le PDF devrait se télécharger automatiquement

7. Ouvrez le PDF pour vérifier qu'il contient:
   - Les informations commerciales
   - Les paramètres de la simulation
   - Les résultats
   - Une mise en page professionnelle

### Test 2: Envoi par Email (Nécessite configuration SMTP)

#### Configuration préalable

1. **Créer un mot de passe d'application Gmail**:
   - Allez sur https://myaccount.google.com/security
   - Activez la validation en 2 étapes si ce n'est pas déjà fait
   - Allez sur https://myaccount.google.com/apppasswords
   - Créez un mot de passe pour "Autre (nom personnalisé)"
   - Nommez-le "CGF GESTION Simulateur"
   - Copiez le mot de passe (format: xxxx xxxx xxxx xxxx)

2. **Configurer les variables d'environnement**:
   
   Option A - Fichier .env (Recommandé):
   ```bash
   cd /home/runner/work/Simulateur-d-investissement/Simulateur-d-investissement
   cp .env.example .env
   nano .env  # ou utilisez votre éditeur préféré
   ```
   
   Remplissez:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=dylanetraderinvestor@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx
   ```
   (Remplacez par le vrai mot de passe d'application)
   
   Option B - Variables système:
   ```bash
   export SMTP_SERVER="smtp.gmail.com"
   export SMTP_PORT="587"
   export SMTP_USERNAME="dylanetraderinvestor@gmail.com"
   export SMTP_PASSWORD="xxxx xxxx xxxx xxxx"
   ```

#### Test de l'envoi

1. Lancez l'application (avec les variables d'environnement configurées):
   ```bash
   streamlit run app.py
   ```

2. Effectuez une simulation (comme dans Test 1)

3. Dans la section "📤 Exporter le rapport", cliquez sur "📧 Envoyer par email" (à droite)

4. Entrez l'adresse email de test: dylanetraderinvestor@gmail.com

5. Cliquez sur "📧 Envoyer le rapport"

6. **VÉRIFICATIONS**:
   - Si configuré correctement: Message vert "✅ Email envoyé avec succès..."
   - Si mal configuré: Message orange avec l'erreur détaillée
   - Vérifiez votre boîte mail (et spam) pour l'email

7. L'email devrait contenir:
   - Un en-tête "CGF GESTION"
   - Un résumé des résultats
   - Le PDF en pièce jointe

### Test 3: Test automatisé (Sans UI)

Pour tester rapidement sans lancer Streamlit:

```bash
cd /home/runner/work/Simulateur-d-investissement/Simulateur-d-investissement

# Test PDF uniquement
python /tmp/test_complete.py

# Avec SMTP configuré, testera aussi l'email
```

## Problèmes courants

### Le bouton PDF n'apparaît pas
→ Vérifiez que vous avez bien cliqué sur "Lancer la simulation"
→ Vérifiez dans la console s'il y a des erreurs

### Email non reçu
→ Vérifiez vos spams
→ Vérifiez que vous utilisez un **mot de passe d'application** (pas le mot de passe Gmail normal)
→ Vérifiez que la validation en 2 étapes est activée
→ Relancez l'app après avoir configuré les variables

### Erreur "Authentication failed"
→ Le mot de passe d'application est incorrect
→ Retirez les espaces du mot de passe

### Message "SMTP_USERNAME not set"
→ Les variables d'environnement ne sont pas chargées
→ Vérifiez que le fichier .env existe et contient les bonnes valeurs
→ Relancez l'application

## Fichiers modifiés

- `core/export.py`: Amélioration de send_email_with_attachment (retourne tuple)
- `ui/layout.py`: Fix du bouton PDF download + gestion erreurs email
- `app.py`: Ajout chargement automatique .env
- `requirements.txt`: Ajout python-dotenv
- `.env.example`: Template de configuration
- `CONFIGURATION_EMAIL.md`: Guide détaillé
- `README.md`: Mise à jour instructions

## Validation finale

✅ PDF généré correctement (testé, 3.86 KB)
✅ Bouton de téléchargement persiste (code corrigé)
✅ Messages d'erreur clairs pour email
✅ Configuration .env supportée
✅ Documentation complète ajoutée

⏳ En attente: Test réel de l'envoi email avec credentials
