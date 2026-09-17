from flask import render_template, Blueprint, redirect, url_for, request
from flask_login import login_required, current_user

from API_requests import extend, check_server_status
from data_base import delete_user_port, rename_user_port, create_port_for_user
from notifications import create_notification
from main_page_service import main_page_render_service

main_page = Blueprint('main_page', __name__)

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
    create_notification(
        msg,
        'success' if success else 'error',
        'main_page.main'
    )
    return redirect(url_for('main_page.main') + '#links-section')


@main_page.route("/ports/<int:port_id>/rename", methods=["POST"])
@login_required
def rename_port(port_id):
    new_name = request.form.get("link_name", "")
    success, msg = rename_user_port(current_user, port_id, new_name)
    create_notification(
        msg,
        'success' if success else 'error',
        'main_page.main'
    )
    return redirect(url_for('main_page.main') + '#links-section')


@main_page.route("/ports/<int:port_id>/delete", methods=["POST"])
@login_required
def delete_port(port_id):
    success, msg = delete_user_port(current_user, port_id)
    create_notification(
        msg,
        'success' if success else 'error',
        'main_page.main'
    )
    return redirect(url_for('main_page.main') + '#links-section')


@main_page.route("/extend-access", methods=["POST"])
@login_required
def extend_access():
    true_login = current_user.true_login
    success, msg = extend(true_login)
    create_notification(
        msg,
        'success' if success else 'error',
        'main_page.main'
    )
    return redirect(url_for('main_page.main'))


@main_page.route("/check-server-status", methods=["POST"])
@login_required
def check_servers():
    success, msg = check_server_status()
    create_notification(
        msg,
        'success' if success else 'error',
        'main_page.main'
    )

    return redirect(url_for('main_page.main'))
