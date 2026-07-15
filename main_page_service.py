import os
from datetime import datetime

from flask_models import db, UserLink

start_port, end_port = 20000, 21000


def create_link_for_user(user, name='новая ссылка'):
    last_link = UserLink.query.order_by(UserLink.port_number.desc()).first()

    if last_link is None:
        next_port = start_port
    else:
        next_port = last_link.port_number + 1

    if next_port >= end_port:
        return False, "Свободные порты закончились"

    url_pt1 = os.getenv("BASE_URL_P1")
    url_pt2 = os.getenv("BASE_URL_P2")

    if not url_pt1 or not url_pt2:
        return False, "Не настроены переменные BASE_URL_P1 или BASE_URL_P2"

    url = url_pt1 + str(next_port) + url_pt2

    new_link = UserLink(
        user_id=user.id,
        name=name,
        port_number=next_port,
        url=url
    )

    db.session.add(new_link)
    db.session.commit()

    return True, "Ссылка создана"

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

        if traffic_left < 0:
            traffic_left = 0

        if traffic_limit > 0:
            traffic_percent = round((traffic_used / traffic_limit) * 100)

        if traffic_percent > 100:
            traffic_percent = 100

        return traffic_used, traffic_limit, traffic_left, traffic_percent

    traffic_used = 'Сервер не отвечает'
    traffic_limit = 'Сервер не отвечает'
    traffic_left = 'Сервер не отвечает'

    return traffic_used, traffic_limit, traffic_left, traffic_percent


def rename_user_link(user, link_id, new_name):
    link = UserLink.query.filter_by(id=link_id, user_id=user.id).first()

    if link is None:
        return False, 'Ссылка не найдена'

    new_name = new_name.strip()
    if not new_name:
        return False, 'Название не может быть пустым'

    link.name = new_name
    db.session.commit()
    return True, f'Название изменено на: {new_name}'


def delete_user_link(user, link_id):
    link = UserLink.query.filter_by(id=link_id, user_id=user.id).first()

    if link is None:
        return False, 'Ссылка не найдена'

    db.session.delete(link)
    db.session.commit()

    return True, f'Ссылка {link_id} удалена'