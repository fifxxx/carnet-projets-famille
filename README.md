# Le carnet de projets — version autonome

Cette application ne dépend plus de Claude : elle tourne comme un site web normal,
avec **Firebase** (Firestore) pour stocker et synchroniser les données entre vous
et votre épouse, hébergé sur **Netlify**, à partir d'un dépôt **GitHub**.

C'est un site statique : un seul fichier `index.html`, pas d'étape de build,
pas de serveur à gérer.

---

## Étape 1 — Créer le projet Firebase (5 min)

1. Allez sur [console.firebase.google.com](https://console.firebase.google.com) et connectez-vous avec un compte Google.
2. **Ajouter un projet** → donnez-lui un nom (ex. `carnet-projets-famille`) → vous pouvez désactiver Google Analytics, il n'est pas utile ici.
3. Dans le menu de gauche, allez dans **Compilation > Firestore Database** → **Créer une base de données**.
   - Choisissez un emplacement proche de vous (ex. `eur3 (europe-west)`).
   - Démarrez en **mode production** (les règles de sécurité seront collées à l'étape 3).
4. Toujours dans la console, cliquez sur l'icône ⚙️ **Paramètres du projet**, descendez à **Vos applications**, cliquez sur l'icône **</>** (Web) pour ajouter une application web.
   - Donnez-lui un nom (ex. `carnet-web`), pas besoin de cocher Firebase Hosting.
   - Firebase vous affiche un bloc `firebaseConfig = { ... }` : copiez ces valeurs dans le fichier **`firebase-config.js`** de ce projet, à la place des `VOTRE_...`.

## Étape 2 — Coller les règles de sécurité (2 min)

1. Dans la console Firebase, allez dans **Firestore Database > Règles**.
2. Remplacez tout le contenu par celui du fichier **`firestore.rules`** fourni ici.
3. Cliquez sur **Publier**.

Ces règles limitent l'accès à un seul document (`carnetFamilial/menage`), celui
utilisé par l'application — le reste de votre projet Firebase reste fermé.

## Étape 3 — Mettre le projet sur GitHub (5 min)

> ⚠️ Créez ce dépôt en **privé**. La configuration Firebase collée à l'étape 1
> n'est pas un mot de passe secret, mais un dépôt privé évite qu'un inconnu
> tombe dessus et vienne écrire dans votre carnet.

1. Sur [github.com](https://github.com), cliquez sur **New repository**.
   - Nom : par exemple `carnet-projets-famille`.
   - Visibilité : **Private**.
   - Ne cochez aucune case d'initialisation (pas de README, pas de licence).
2. Sur votre ordinateur, ouvrez un terminal dans le dossier de ce projet (celui qui contient `index.html`) et lancez :

```bash
git init
git add .
git commit -m "Premier envoi du carnet de projets"
git branch -M main
git remote add origin https://github.com/VOTRE-COMPTE/carnet-projets-famille.git
git push -u origin main
```

(Remplacez `VOTRE-COMPTE` par votre nom d'utilisateur GitHub.)

## Étape 4 — Connecter Netlify au dépôt GitHub (5 min)

1. Allez sur [app.netlify.com](https://app.netlify.com) et connectez-vous (ou créez un compte gratuit).
2. **Add new site > Import an existing project**.
3. Choisissez **GitHub**, autorisez Netlify à accéder à vos dépôts, puis sélectionnez `carnet-projets-famille`.
4. Netlify détecte le fichier `netlify.toml` fourni : aucune commande de build n'est nécessaire, laissez les champs tels quels.
5. Cliquez sur **Deploy site**.

Votre site est en ligne en moins d'une minute, avec une adresse du type
`https://un-nom-genere.netlify.app`. Vous pouvez la personnaliser dans
**Site settings > Domain management**, ou brancher votre propre nom de domaine.

À partir de maintenant, **chaque `git push` sur la branche `main` redéploie automatiquement le site.**

## Étape 5 — Partager avec votre épouse

Envoyez-lui simplement l'adresse du site Netlify. Comme les données sont dans
Firestore (et non plus dans le stockage propre à Claude), tout ce que vous
ajoutez ou modifiez l'un ou l'autre se synchronise **en temps réel**, sans
avoir besoin d'ouvrir le même fichier ni de recharger la page.

---

## Pour aller plus loin (facultatif)

- **Sécurité renforcée** : dans cette version, quiconque connaît l'adresse de
  votre projet Firebase peut lire/écrire le carnet. Pour un usage à deux dans
  un dépôt privé, c'est un compromis raisonnable. Si vous voulez une vraie
  authentification (email/mot de passe), c'est possible avec Firebase
  Authentication, mais cela demande un écran de connexion en plus — dites-moi
  si vous voulez que je l'ajoute.
- **Nom de domaine personnalisé** : Netlify permet de brancher un domaine que
  vous possédez déjà (Site settings > Domain management > Add custom domain).
- **Historique des données** : Firestore garde uniquement la dernière version
  du document. Si vous voulez un historique des modifications, cela peut se
  faire avec une sous-collection `historique`, à ajouter plus tard si besoin.

## Structure du projet

```
index.html          → l'application (à ne pas modifier sauf si vous savez ce que vous faites)
firebase-config.js   → vos identifiants de projet Firebase (à remplir, étape 1)
firestore.rules      → règles de sécurité à coller dans la console Firebase (étape 2)
netlify.toml         → indique à Netlify comment publier le site (rien à changer)
.gitignore
README.md            → ce guide
```
