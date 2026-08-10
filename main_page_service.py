import os

from datetime import datetime


from API_requests import check_user_status, check_server_status
from data_base import build_user_port_rows

source_url = os.getenv('SOURCE_URL')


def bytes_to_gb(value):
    if value is None:
        return 0

    return round(value / 1024 ** 3, 2)


def format_expire_at(expire_at):
    if not expire_at:
        return '—'

    try:
        dt = datetime.fromisoformat(expire_at.replace('Z', '+00:00'))
        return dt.strftime('%d.%m.%Y %H:%M')
    except ValueError:
        return expire_at


def limit_calculations(success, limit_traffic_bytes, used_traffic_bytes):
    traffic_percent = 0

    if success:
        traffic_used = bytes_to_gb(used_traffic_bytes)
        traffic_limit = bytes_to_gb(limit_traffic_bytes)

        traffic_left = round(traffic_limit - traffic_used, 2)

        traffic_percent = round((traffic_used / traffic_limit) * 100)

        return traffic_used, traffic_limit, traffic_left, traffic_percent

    traffic_used = 'Сервер не отвечает'
    traffic_limit = 'Сервер не отвечает'
    traffic_left = 'Сервер не отвечает'

    return traffic_used, traffic_limit, traffic_left, traffic_percent


def status_check(server_success, status):
    if server_success:
        server_status = 'Активны'
    else:
        server_status = 'Неактивны'

    if status == "ACTIVE":
        status = "Активна"
    else:
        status = "Неактивна"

    return server_status, status


def main_page_render_service(user):
    true_login = user.true_login

    success, status, expire_at, limit_traffic_bytes, used_traffic_bytes, subscription_url = check_user_status(true_login)

    traffic_used, traffic_limit, traffic_left, traffic_percent = limit_calculations(success, limit_traffic_bytes, used_traffic_bytes)

    server_success, server_msg = check_server_status()

    server_status, subscription_status = status_check(server_success, status)

    return {
        "traffic_used": traffic_used,
        "traffic_limit": traffic_limit,
        "traffic_left": traffic_left,
        "traffic_percent": traffic_percent,
        "traffic_unit": "ГБ",

        "server_status": server_status,

        "subscription_status": subscription_status,
        "subscription_expire_at": format_expire_at(expire_at),
        "subscription_link": subscription_url,

        "user_ports": build_user_port_rows(user, source_url)
    }
