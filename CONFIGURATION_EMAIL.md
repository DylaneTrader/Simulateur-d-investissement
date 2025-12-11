# Guide de Configuration Email - Simulateur d'Investissement

## Configuration SMTP pour Gmail

Ce guide explique comment configurer l'envoi d'emails depuis l'application.

### Étape 1: Préparer votre compte Gmail

1. Connectez-vous à votre compte Gmail (dylanetraderinvestor@gmail.com)
2. Allez sur: https://myaccount.google.com/security
3. Activez la **validation en 2 étapes** si ce n'est pas déjà fait

### Étape 2: Créer un mot de passe d'application

1. Une fois la validation en 2 étapes activée, allez sur: https://myaccount.google.com/apppasswords
2. Dans "Sélectionner une application", choisissez **"Autre (nom personnalisé)"**
3. Entrez un nom comme: **"CGF GESTION Simulateur"**
4. Cliquez sur **"Générer"**
5. Google vous donnera un mot de passe de 16 caractères (format: xxxx xxxx xxxx xxxx)
6. **Copiez ce mot de passe** - vous ne pourrez plus le voir après avoir fermé cette fenêtre

### Étape 3: Configurer les variables d'environnement

#### Option A: Fichier .env (Recommandé pour développement local)

1. Copiez le fichier `.env.example` vers `.env`:
   ```bash
   cp .env.example .env
   ```

2. Éditez le fichier `.env` avec vos vraies valeurs:
   ```bash
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=dylanetraderinvestor@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx
   ```
   (remplacez `xxxx xxxx xxxx xxxx` par votre mot de passe d'application)

3. Chargez les variables d'environnement avant de lancer l'application:
   ```bash
   # Sous Linux/Mac
   export $(cat .env | xargs)
   streamlit run app.py
   
   # Sous Windows PowerShell
   Get-Content .env | ForEach-Object {
       $name, $value = $_.split('=')
       Set-Content env:\$name $value
   }
   streamlit run app.py
   ```

#### Option B: Variables d'environnement système (Recommandé pour production)

**Linux/Mac:**
```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="dylanetraderinvestor@gmail.com"
export SMTP_PASSWORD="xxxx xxxx xxxx xxxx"
streamlit run app.py
```

**Windows CMD:**
```cmd
set SMTP_SERVER=smtp.gmail.com
set SMTP_PORT=587
set SMTP_USERNAME=dylanetraderinvestor@gmail.com
set SMTP_PASSWORD=xxxx xxxx xxxx xxxx
streamlit run app.py
```

**Windows PowerShell:**
```powershell
$env:SMTP_SERVER="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USERNAME="dylanetraderinvestor@gmail.com"
$env:SMTP_PASSWORD="xxxx xxxx xxxx xxxx"
streamlit run app.py
```

### Étape 4: Tester la fonctionnalité email

1. Lancez l'application avec les variables d'environnement configurées
2. Effectuez une simulation
3. Dans la section "📧 Envoyer par email", entrez une adresse email de test
4. Cliquez sur "📧 Envoyer le rapport"
5. Vérifiez que l'email est reçu

### Dépannage

#### Erreur "Authentication failed"
- Vérifiez que vous utilisez bien un **mot de passe d'application** et non votre mot de passe Gmail normal
- Vérifiez que la validation en 2 étapes est activée
- Vérifiez qu'il n'y a pas d'espaces dans le mot de passe

#### Erreur "SMTP_USERNAME not set"
- Les variables d'environnement ne sont pas correctement chargées
- Relancez l'application après avoir configuré les variables
- Vérifiez que le fichier .env existe et contient les bonnes valeurs

#### L'email n'arrive pas
- Vérifiez vos spams
- Vérifiez que l'adresse email du destinataire est correcte
- Vérifiez les logs de l'application pour voir les erreurs

### Sécurité

⚠️ **IMPORTANT:**
- Ne commitez **JAMAIS** le fichier `.env` dans Git (il est déjà dans `.gitignore`)
- Ne partagez **JAMAIS** votre mot de passe d'application
- En production, utilisez un gestionnaire de secrets (AWS Secrets Manager, Azure Key Vault, etc.)
- Révocuez et régénérez le mot de passe d'application si vous pensez qu'il a été compromis

### Alternative: Autres fournisseurs SMTP

Si vous n'utilisez pas Gmail, adaptez les paramètres:

**Outlook/Hotmail:**
```
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
```

**Yahoo:**
```
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

**Autre fournisseur:**
Consultez la documentation de votre fournisseur email pour les paramètres SMTP.
