import calendar
import os
import requests

from datetime import datetime

JWT = os.getenv("PANEL_API_KEY")
url = os.getenv("ADMIN_URL")


def request_panel(endpoint):
    response = requests.get(
        url + endpoint,
        headers={
            "Authorization": f"Bearer {JWT}",
            "X-Forwarded-For": "127.0.0.1",
            "X-Forwarded-Proto": "https"
        }
    )

    response.raise_for_status()

    data = response.json()
    return data['response']


def get_last_day_of_next_month(expire_at_str):
    dt = datetime.fromisoformat(expire_at_str.replace('Z', '+00:00'))
    year = dt.year
    month = dt.month

    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1

    last_day = calendar.monthrange(next_year, next_month)[1]
    new_dt = datetime(next_year, next_month, last_day, 23, 59, 59)

    return new_dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def check_user_status(true_login):
    try:
        response_data = request_panel("users/by-username/" + true_login)
    except requests.exceptions.RequestException:
        return False, "Запрос не выполнен, сервер не отвечает", None, None, None, None

    status = response_data.get('status')
    expire_at = response_data.get('expireAt')
    limit_traffic_bytes = response_data.get('trafficLimitBytes')
    used_traffic_bytes = response_data.get('userTraffic', {}).get('usedTrafficBytes')
    subscription_url = response_data.get('subscriptionUrl')

    return True, status, expire_at, limit_traffic_bytes, used_traffic_bytes, subscription_url


def check_server_status():
    try:
        response_data = request_panel("hosts")
    except requests.exceptions.RequestException:
        return False, 'Данные о серверах получить не удалось'
    statuses = []
    check = False
    for host in response_data:
        if host['isDisabled']:
            continue
        server_status_url = 'https://' + host['address']
        if (requests.get(server_status_url)).status_code == 200:
            statuses.append(f'Сервер {host['remark']} активен')
            check = True
        else:
            statuses.append(f'Сервер {host['remark']} не активен')
    return check, '\n'.join(statuses)

def extend(true_login):
    try:
        response_data = request_panel("users/by-username/" + true_login)
    except requests.exceptions.RequestException:
        return False, "Запрос не выполнен, сервер не отвечает"

    expire_at = response_data.get('expireAt')
    new_expire = get_last_day_of_next_month(expire_at)

    patch_response = requests.patch(url + "users",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {JWT}",
            "X-Forwarded-For": "127.0.0.1",
            "X-Forwarded-Proto": "https"
        },
        json={
            "username": f"{true_login}",
            "expireAt": new_expire
        }
    )

    if patch_response.status_code == 200:
        return True, f"Подписка продлена до {new_expire}"
    else:
        return False, f"Ошибка продления: {patch_response.status_code}"
