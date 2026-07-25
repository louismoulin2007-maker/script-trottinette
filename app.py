import os
import shutil
import subprocess
import tempfile
import traceback

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 300 * 1024 * 1024  # 300 Mo (limite RAM hébergement gratuit)

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

_whisper_model = None


def get_whisper_model():
    """Charge le modèle Whisper une seule fois (paresseux, coûteux au démarrage)."""
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    return _whisper_model


def check_ffmpeg():
    return shutil.which("ffmpeg") is not None


def extract_audio(video_path: str, audio_path: str):
    """Extrait une piste audio mono 16kHz depuis la vidéo, via ffmpeg."""
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-ac", "1", "-ar", "16000",
        "-f", "wav", audio_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Échec extraction audio (ffmpeg) : {result.stderr[-800:]}")


def transcribe_audio(audio_path: str) -> str:
    model = get_whisper_model()
    segments, _info = model.transcribe(audio_path, language="fr", vad_filter=True)
    return " ".join(seg.text.strip() for seg in segments).strip()


TRANSLATION_SYSTEM_PROMPT = """Tu es traducteur et adaptateur de scripts pour du contenu TikTok / YouTube Shorts, dans la niche des trottinettes électriques.

On te donne un script en français. Traduis-le en allemand pour un public germanophone, en respectant ces règles strictes :

- Ton direct, familier, percutant ("du" partout, jamais "Sie").
- Phrases courtes, punchy, maximum ~15 mots chacune. Une idée par phrase.
- Garde la même structure : accroche choc en première phrase, développement fluide, appel à l'action final.
- N'ajoute rien qui ne soit pas dans l'original (pas d'intro molle, pas de commentaire de ta part).
- Adapte les expressions idiomatiques françaises en expressions allemandes naturelles plutôt que de traduire mot à mot.
- Garde tous les chiffres, faits et exemples concrets identiques.
- N'utilise jamais de listes à puces : uniquement des paragraphes fluides, comme une voix off orale.

Réponds uniquement avec le texte allemand final, sans aucun commentaire, préambule ni guillemets."""


def translate_to_german(french_text: str) -> str:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY manquante. Ajoute-la dans le fichier .env.")

    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2000,
        system=TRANSLATION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": french_text}],
    )
    return "".join(block.text for block in message.content if block.type == "text").strip()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({
        "ffmpeg": check_ffmpeg(),
        "anthropic_key_set": bool(ANTHROPIC_API_KEY),
        "whisper_model": WHISPER_MODEL_SIZE,
    })


@app.route("/api/process", methods=["POST"])
def process():
    if not check_ffmpeg():
        return jsonify({"error": "ffmpeg introuvable sur ce système. Installe-le puis relance l'app."}), 500

    video_file = request.files.get("video")
    if not video_file or video_file.filename == "":
        return jsonify({"error": "Aucune vidéo reçue."}), 400

    tmp_dir = tempfile.mkdtemp(prefix="trottinette_")
    video_path = os.path.join(tmp_dir, video_file.filename)
    audio_path = os.path.join(tmp_dir, "audio.wav")

    try:
        video_file.save(video_path)
        extract_audio(video_path, audio_path)
        french_text = transcribe_audio(audio_path)

        if not french_text:
            return jsonify({"error": "Aucune parole détectée dans la vidéo."}), 422

        german_text = translate_to_german(french_text)

        return jsonify({
            "french": french_text,
            "german": german_text,
            "french_word_count": len(french_text.split()),
            "german_word_count": len(german_text.split()),
        })
    except Exception as exc:
        traceback.print_exc()
        return jsonify({"error": str(exc)}), 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
