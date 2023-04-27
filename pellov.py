#!/usr/bin/env python3

import locale
import logging
from datetime import datetime

import gspread
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
logging.basicConfig(
    level=logging.DEBUG if app.debug else logging.INFO,
    format="%(asctime)s %(name)s %(levelname)-8s %(message)s",
)
logger = logging.getLogger(__name__)

CONTACT_SERVICE_ACCOUNT = app.config.get("CONTACT_SERVICE_ACCOUNT")
CONTACT_SPREADSHEET_ID = app.config.get("CONTACT_SPREADSHEET_ID")
CONTACT_WORKSHEET_ID = app.config.get("CONTACT_WORKSHEET_ID")
MANDRILL_KEY = app.config.get("MANDRILL_KEY")


def store_contact(firstname, lastname, email, company, phone, **_):

    gc = gspread.service_account(CONTACT_SERVICE_ACCOUNT)

    wks = gc.open_by_key(CONTACT_SPREADSHEET_ID).get_worksheet_by_id(
        CONTACT_WORKSHEET_ID
    )

    contact_date = datetime.now()

    wks.append_row(
        (
            contact_date.strftime("%d/%m/%Y"),
            contact_date.strftime("%H:%M"),
            firstname,
            lastname,
            email,
            company,
            phone,
        )
    )


@app.route("/")
@app.route("/<page>")
def page(page="index"):
    try:
        return render_template(
            "{}.html".format(page), page=page, current_year=datetime.now().year
        )

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

    try:
        if app.debug:
            logger.debug(message)
        else:
            mandrill.Mandrill(MANDRILL_KEY).messages.send(message=message)
        flash(
            "Nous vous remercions pour votre demande. "
            "Notre équipe va revenir vers vous dans les plus brefs délais."
        )
    except Exception as e:
        logger.error(f"Error while trying to send mail: {e}")

    try:
        store_contact(**request.form)
    except Exception as e:
        logger.error(f"Error while storing contact: {e}")

    return redirect(url_for("page"))


if __name__ == "__main__":
    app.run(debug=True)
