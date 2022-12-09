#!/usr/bin/env python3

import locale

import jinja2
import mandrill
from flask import (
    Flask,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

app = Flask(__name__)

# Secret key doesn't have to be changed, it is only used for flash messages
app.secret_key = "secret key"
app.config.from_envvar("WWWPELLOV_CONFIG", silent=True)

locale.setlocale(locale.LC_ALL, ("fr_FR", "UTF-8"))

MANDRILL_KEY = app.config.get("MANDRILL_KEY")


@app.route("/")
@app.route("/<page>")
def page(page="index"):
    try:
        return render_template("{}.html".format(page), page=page)
    except jinja2.exceptions.TemplateNotFound:
        abort(404)


@app.route("/robots.txt")
def robots():
    return Response("User-agent: *\nDisallow: \n", mimetype="text/plain")


@app.route("/contact", methods=["POST"])
def contact():
    message = {
        "to": [{"email": "contact@kozea.fr"}],
        "subject": "Prise de contact sur le site de PromoMaker",
        "from_email": "contact@kozea.fr",
        "html": "<br>".join(
            [
                "Prénom : %s" % request.form.get("firstname", ""),
                "Nom : %s" % request.form.get("lastname", ""),
                "Email : %s" % request.form.get("email", ""),
                "Société : %s" % request.form.get("company", ""),
                "Téléphone : %s" % request.form.get("phone", ""),
            ]
        ),
    }

    if app.debug:
        print(message)
    else:
        mandrill.Mandrill(MANDRILL_KEY).messages.send(message=message)

    flash(
        "Nous vous remercions pour votre demande. "
        "Notre équipe va revenir vers vous dans les plus brefs délais."
    )
    return redirect(url_for("page"))


if __name__ == "__main__":
    app.run(debug=True)
