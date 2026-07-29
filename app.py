import os
import base64
import json
import stripe
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
PRIX_INVITATION_CENTIMES = 300


def encoder_donnees(donnees: dict) -> str:
    json_str = json.dumps(donnees, ensure_ascii=False)
    return base64.urlsafe_b64encode(json_str.encode("utf-8")).decode("utf-8")


def decoder_donnees(chaine: str) -> dict:
    json_str = base64.urlsafe_b64decode(chaine.encode("utf-8")).decode("utf-8")
    return json.loads(json_str)


@app.route("/", methods=["GET"])
def accueil():
    return render_template("index.html")


@app.route("/creer", methods=["POST"])
def creer_paiement():
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

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": "Invitation personnalisée"},
                "unit_amount": PRIX_INVITATION_CENTIMES,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=url_for("succes", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=url_for("accueil", _external=True),
        metadata={"donnees": code},
    )
    return redirect(session.url, code=303)


@app.route("/succes")
def succes():
    session_id = request.args.get("session_id")
    if not session_id:
        return "Session de paiement manquante.", 400

    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == "paid":
        code = session.metadata.get("donnees")
        lien = url_for("invitation", code=code, _external=True)
        return render_template("succes.html", lien=lien)
    else:
        return "Le paiement n'a pas été confirmé.", 402


@app.route("/invitation/<code>")
def invitation(code):
    try:
        donnees = decoder_donnees(code)
    except Exception:
        return "Lien invalide ou corrompu.", 400
    return render_template("invitation.html", donnees=donnees)


if __name__ == "__main__":
    app.run(debug=True)
