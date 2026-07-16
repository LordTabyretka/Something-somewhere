from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user

from API_requests import check_server_status, check_user_status, extend
from main_page_service import limit_calculations, format_expire_at, create_link_for_user, rename_user_link, \
    delete_user_link

main_page = Blueprint('main_page', __name__)


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
        user_links=current_user.links
    )


@main_page.route("/links/create", methods=["POST"])
@login_required
def create_link():
    success, msg = create_link_for_user(current_user)

    flash(msg, 'success' if success else 'error')

    return redirect(url_for('main_page.main') + '#links-section')

@main_page.route("/links/<int:link_id>/rename", methods=["POST"])
@login_required
def rename_link(link_id):
    new_name = request.form.get("link_name", '')

    success, msg = rename_user_link(current_user, link_id, new_name)
    flash(msg, 'success' if success else 'error')

    return redirect(url_for('main_page.main') + '#links-section')


@main_page.route("/links/<int:link_id>/delete", methods=["POST"])
@login_required
def delete_link(link_id):
    success, msg = delete_user_link(current_user, link_id)
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