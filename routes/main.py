from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
import os
from API_requests import extend
from main_page_service import create_port_for_user, rename_user_port, delete_user_port, main_page_render_service

main_page = Blueprint('main_page', __name__)

source_url = os.getenv('SOURCE_URL')

@main_page.route("/main", methods=["GET"])
@login_required
def main():
    template_data = main_page_render_service(current_user)

    return render_template(
        "main.html",
        **template_data
    )


@main_page.route("/ports/create", methods=["POST"])
@login_required
def create_port():
    success, msg = create_port_for_user(current_user)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('main_page.main') + '#links-section')


@main_page.route("/ports/<int:port_id>/rename", methods=["POST"])
@login_required
def rename_port(port_id):
    new_name = request.form.get("link_name", "")
    success, msg = rename_user_port(current_user, port_id, new_name)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('main_page.main') + '#links-section')


@main_page.route("/ports/<int:port_id>/delete", methods=["POST"])
@login_required
def delete_port(port_id):
    success, msg = delete_user_port(current_user, port_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('main_page.main') + '#links-section')


@main_page.route("/check-api", methods=["POST", "GET"])
@login_required
def check_api():
    if request.method == "POST":
        if 'extend' in request.form:
            true_login = current_user.true_login
            success, msg = extend(true_login)
            flash(msg, 'success' if success else 'error')
            return redirect(url_for('main_page.main'))
    return redirect(url_for('main_page.main'))
