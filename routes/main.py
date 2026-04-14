from flask import render_template, Blueprint
from flask_login import login_required


main_page = Blueprint('main_page', __name__)


@main_page.route("/main", methods=["GET", "POST"])
@login_required
def main():
    return render_template("main.html")