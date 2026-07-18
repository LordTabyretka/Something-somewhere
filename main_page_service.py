from datetime import datetime
from flask_models import db, UserPort
from parser import get_user_url

start_port, end_port = 20000, 21000


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


def create_port_for_user(user, name='Новая ссылка'):
    last_port = UserPort.query.order_by(UserPort.port_number.desc()).first()

    if last_port is None:
        next_port = start_port
    else:
        next_port = last_port.port_number + 1

    if next_port >= end_port:
        return False, "Свободные порты закончились"

    new_port = UserPort(
        user_id=user.id,
        name=name,
        port_number=next_port
    )

    db.session.add(new_port)
    db.session.commit()

    return True, "Ссылка создана"


def rename_user_port(user, port_id, new_name):
    user_port = UserPort.query.filter_by(id=port_id, user_id=user.id).first()

    if user_port is None:
        return False, "Порт не найден"

    new_name = new_name.strip()
    if not new_name:
        return False, "Название не может быть пустым"

    user_port.name = new_name
    db.session.commit()

    return True, "Название сохранено"


def delete_user_port(user, port_id):
    user_port = UserPort.query.filter_by(id=port_id, user_id=user.id).first()

    if user_port is None:
        return False, "Порт не найден"

    db.session.delete(user_port)
    db.session.commit()

    return True, "Ссылка удалена"


def build_user_port_rows(user, source_url):
    user_ports = UserPort.query.filter_by(user_id=user.id).order_by(UserPort.port_number).all()

    result = []

    for user_port in user_ports:
        generated_links = get_user_url(source_url, user_port.port_number)

        result.append({
            "id": user_port.id,
            "name": user_port.name,
            "port_number": user_port.port_number,
            "links": generated_links
        })

    return result