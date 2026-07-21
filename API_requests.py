import calendar
import os
import requests

from datetime import datetime

JWT = os.getenv("PANEL_API_KEY")
url = os.getenv("ADMIN_URL")


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
    response = requests.get(
        url + "users/by-username/" + true_login,
        headers={
            "Authorization": f"Bearer {JWT}",
            "X-Forwarded-For": "127.0.0.1",
            "X-Forwarded-Proto": "https"
        }
    )
    if response.status_code == 200:
        data = response.json()
        response_data = data['response']
        status = response_data.get('status')
        expire_at = response_data.get('expireAt')
        limit_traffic_bytes = response_data.get('trafficLimitBytes')
        used_traffic_bytes = response_data.get('userTraffic', {}).get('usedTrafficBytes')
        subscription_url = response_data.get('subscriptionUrl')

        return True, status, expire_at, limit_traffic_bytes, used_traffic_bytes, subscription_url
    else:
        return False, "Запрос не выполнен, сервер не отвечает", None, None, None, None


def check_server_status():
    response = requests.get(
        url + "hosts",
        headers={
            "Authorization": f"Bearer {JWT}",
            "X-Forwarded-For": "127.0.0.1",
            "X-Forwarded-Proto": "https"
        }
    )
    statuses = []
    check = False
    for host in response.json()["response"]:
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
    response = requests.get(
        url+ "users/by-username/" + true_login,
        headers={
            "Authorization": f"Bearer {JWT}",
            "X-Forwarded-For": "127.0.0.1",
            "X-Forwarded-Proto": "https"
        }
    )

    if response.status_code == 200:
        data = response.json()
        response_data = data['response']
        expire_at = response_data.get('expireAt')
        new_expire = get_last_day_of_next_month(expire_at)
    else:
        return False, "Запрос не выполнен, сервер не отвечает"

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
