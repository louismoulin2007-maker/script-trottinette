# FR → DE — Studio de script

App qui prend une vidéo (ton contenu trottinettes en français), transcrit la voix, puis génère une version allemande punchy et prête pour la voix off, en respectant la structure hook / développement / CTA.

---

## 🌐 Option A — Mettre le site en ligne (sans terminal, sans rien installer)

Tout se fait dans le navigateur, en deux étapes : mettre le code sur GitHub, puis le connecter à Render (hébergeur gratuit).

### A.1 — Mettre le projet sur GitHub

1. Va sur **github.com**, crée un compte gratuit si besoin.
2. Clique sur le **+** en haut à droite → **New repository**.
3. Donne-lui un nom (ex : `script-trottinette`), laisse-le en **Public** ou **Private**, clique **Create repository**.
4. Sur la page du nouveau repo, clique **uploading an existing file**.
5. Ouvre le dossier `trottinette-transcriber` sur ton PC, sélectionne **tout son contenu** (pas le dossier lui-même, ce qu'il y a dedans) et fais un glisser-déposer dans la zone GitHub.
6. Descends en bas de page, clique **Commit changes**.

### A.2 — Déployer sur Render

1. Va sur **render.com**, crée un compte gratuit (tu peux te connecter directement avec ton compte GitHub).
2. Clique **New +** → **Web Service**.
3. Connecte ton repo GitHub `script-trottinette` (Render va lister tes repos, choisis-le).
4. Render détecte automatiquement le `Dockerfile` — laisse les réglages par défaut.
5. Choisis l'instance **Free**.
6. Dans la section **Environment Variables**, ajoute :
   - `ANTHROPIC_API_KEY` → colle ta clé (console.anthropic.com → API Keys)
7. Clique **Create Web Service**.

Le premier build prend 5-10 minutes (installation + téléchargement du modèle). Une fois terminé, Render t'affiche ton URL publique, du type :

```
https://script-trottinette.onrender.com
```

C'est ce lien que tu utilises et partages. À garder en tête :
- Le plan gratuit s'endort après 15 min sans visite : le premier chargement après une pause prend ~30-60 secondes, c'est normal.
- Le modèle de transcription utilisé (`base`) est plus léger pour tenir dans la RAM gratuite — bon pour des vidéos de quelques minutes. Si tu veux plus de précision plus tard, tu pourras passer sur un plan payant (~7$/mois) et repasser en modèle `small` ou `medium`.

Ta clé Anthropic reste privée : elle est stockée uniquement dans les "Environment Variables" de Render, jamais visible publiquement.

---

## 💻 Option B — Faire tourner l'app sur ton PC en local

Tout tourne **sur ta machine** : la vidéo et l'audio ne quittent jamais ton ordinateur. Seul le texte transcrit est envoyé à l'API Claude pour la traduction/adaptation.

### 1. Prérequis

- **Python 3.10+** — vérifie avec `python3 --version`
- **ffmpeg** installé et accessible dans le PATH :
  - macOS : `brew install ffmpeg`
  - Windows : `winget install ffmpeg` (ou télécharge sur ffmpeg.org et ajoute-le au PATH)
  - Linux : `sudo apt install ffmpeg`
- Une **clé API Anthropic** (console.anthropic.com → API Keys). Utilisée uniquement pour la traduction du texte, pas pour la vidéo.

### 2. Installation

```bash
cd trottinette-transcriber
python3 -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# puis ouvre .env et colle ta clé ANTHROPIC_API_KEY
```

### 3. Lancer l'app

```bash
python app.py
```

Ouvre ensuite **http://localhost:5001** dans ton navigateur.

Au premier lancement, le modèle Whisper (quelques centaines de Mo) se télécharge automatiquement — ça peut prendre une minute ou deux. Les lancements suivants seront rapides.

### 4. Utilisation

1. Dépose ta vidéo (MP4, MOV, WEBM…) dans la zone de dépôt.
2. Clique sur **Transcrire & traduire**.
3. L'app extrait l'audio, transcrit ta voix en français, puis génère le script allemand.
4. Copie le texte allemand ou télécharge-le en `.txt`, prêt pour ton doublage ou ta voix off.

### Réglages utiles (dans `.env`)

- `WHISPER_MODEL` : `small` par défaut. Passe à `medium` ou `large-v3` si tu veux plus de précision (plus lent, plus gourmand en RAM).
- `ANTHROPIC_MODEL` : `claude-sonnet-5` par défaut.

### Limites connues (Option B)

- Les vidéos très longues (>15-20 min) prennent du temps à transcrire sur CPU — c'est normal.
- Si aucune parole n'est détectée, vérifie que la piste audio de la vidéo n'est pas silencieuse ou trop bruitée.
- La traduction adapte le ton (accroche, phrases courtes, CTA) plutôt que de traduire mot à mot — relis toujours avant de publier.
