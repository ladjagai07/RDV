from flask import Flask, render_template, request, url_for
import base64
import json

app = Flask(__name__)


def encoder_donnees(donnees: dict) -> str:
    """Encode un dictionnaire en une chaîne sûre pour une URL (base64)."""
    json_str = json.dumps(donnees, ensure_ascii=False)
    return base64.urlsafe_b64encode(json_str.encode("utf-8")).decode("utf-8")


def decoder_donnees(chaine: str) -> dict:
    """Décode la chaîne de l'URL pour retrouver le dictionnaire de données."""
    json_str = base64.urlsafe_b64decode(chaine.encode("utf-8")).decode("utf-8")
    return json.loads(json_str)


@app.route("/", methods=["GET", "POST"])
def creer():
    lien_genere = None
    if request.method == "POST":
        donnees = {
            "prenom": request.form.get("prenom", "").strip() or "toi",
            "date": request.form.get("date", ""),
            "heure": request.form.get("heure", ""),
            "lieu": request.form.get("lieu", "").strip(),
            "activites": request.form.get("activites", "").strip(),
            "message": request.form.get("message", "").strip(),
            "photo_url": request.form.get("photo_url", "").strip(),
            "musique_url": request.form.get("musique_url", "").strip(),
        }
        code = encoder_donnees(donnees)
        lien_genere = url_for("invitation", code=code, _external=True)
    return render_template("index.html", lien_genere=lien_genere)


@app.route("/invitation/<code>")
def invitation(code):
    try:
        donnees = decoder_donnees(code)
    except Exception:
        return "Ce lien est invalide ou corrompu.", 400
    return render_template("invitation.html", donnees=donnees)


if __name__ == "__main__":
    app.run(debug=True)
