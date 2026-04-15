import calendar
from datetime import datetime
import requests
import os

JWT = os.getenv("PANEL_API_KEY")
url = "http://localhost:3003/api/users/by-username/"
server_stats_url = os.getenv("SERVER_CHECK_URL")
igor_port = "http://localhost:3003/api/users"


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
        url+true_login,
        headers={
            "Authorization": f"Bearer {JWT}"
        }
    )
    if response.status_code == 200:
        data = response.json()
        response_data = data['response']
        status = response_data.get('status')
        expire_at = response_data.get('expireAt')
        online_at = response_data.get('userTraffic', {}).get('onlineAt')
        used_traffic_bytes = response_data.get('userTraffic', {}).get('usedTrafficBytes')
        return True, status
    else:
        return False, "Запрос не выполнен, сервер не отвечает"


def check_server_status():
    if (requests.get(server_stats_url)).status_code == 200:
        return True, 'Сервера работают'
    return False, 'Сервера не отвечают'


def extend(true_login):
    response = requests.get(
        url + true_login,
        headers={
            "Authorization": f"Bearer {JWT}"
        }
    )

    if response.status_code == 200:
        data = response.json()
        response_data = data['response']
        expire_at = response_data.get('expireAt')
        new_expire = get_last_day_of_next_month(expire_at)
    else:
        return False, "Запрос не выполнен, сервер не отвечает"

    patch_response = requests.patch(igor_port,
        headers={
          "Content-Type": "application/json",
          "Authorization": f"Bearer {JWT}"
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
