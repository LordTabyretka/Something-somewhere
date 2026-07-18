from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
import os
from API_requests import check_server_status, check_user_status, extend
from main_page_service import limit_calculations, format_expire_at, create_port_for_user, rename_user_port, \
    delete_user_port, build_user_port_rows

main_page = Blueprint('main_page', __name__)

source_url = os.getenv('SOURCE_URL')

@main_page.route("/main", methods=["GET"])
@login_required
def main():
    true_login = current_user.true_login

    success, status, expire_at, limit_traffic_bytes, used_traffic_bytes, subscription_url = check_user_status(true_login)

    traffic_used, traffic_limit, traffic_left, traffic_percent = limit_calculations(
        success,
        limit_traffic_bytes,
        used_traffic_bytes
    )

    server_success, server_msg = check_server_status()

    if server_success:
        server_status = 'Активны'
    else:
        server_status = 'Неактивны'

    if status == "ACTIVE":
        status = "Активна"
    else:
        status = "Неактивна"

    return render_template(
        "main.html",
        traffic_used=traffic_used,
        traffic_limit=traffic_limit,
        traffic_left=traffic_left,
        traffic_percent=traffic_percent,
        traffic_unit="ГБ",
        server_status=server_status,
        subscription_status=status,
        subscription_expire_at=format_expire_at(expire_at),
        subscription_link=subscription_url,
        user_ports=build_user_port_rows(current_user, source_url)
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
