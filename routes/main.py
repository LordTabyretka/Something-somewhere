from flask import render_template, Blueprint
from flask_login import login_required, current_user

from API_requests import check_limits

main_page = Blueprint('main_page', __name__)

def bytes_to_gb(value):
    if value is None:
        return 0

    return round(value / 1024 ** 3, 2)


@main_page.route("/main", methods=["GET", "POST"])
@login_required
def main():

    true_login = current_user.true_login

    success, limit_traffic_bytes, used_traffic_bytes = check_limits(true_login)
    traffic_percent = 0
    if success:

        traffic_used = bytes_to_gb(used_traffic_bytes)
        traffic_limit = bytes_to_gb(limit_traffic_bytes)

        traffic_left = round(traffic_limit - traffic_used, 2)

        if traffic_left < 0:
            traffic_left = 0

        if traffic_limit > 0:
            traffic_percent = round((traffic_used / traffic_limit) * 100)

        if traffic_percent > 100:
            traffic_percent = 100
    else:
        traffic_used = 'Сервер не отвечает'
        traffic_limit = 'Сервер не отвечает'
        traffic_left = 'Сервер не отвечает'

    return render_template(
        "main.html",
        traffic_used=traffic_used,
        traffic_limit=traffic_limit,
        traffic_left=traffic_left,
        traffic_percent=traffic_percent,
        traffic_unit="ГБ",
        )
