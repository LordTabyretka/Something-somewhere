from flask_models import db, User, UserPort
from parser import get_user_url

start_port, end_port = 20000, 21000

def create_user(new_login, true_login, password, is_admin=False):
    if not new_login or not password:
        return False, 'Заполните все поля'
    if User.query.filter_by(login=new_login).first():
        return False, 'Логин занят'
    if User.query.filter_by(true_login=true_login).first():
        return False, 'Рабочий логин уже используется'
    new_user = User(login=new_login, true_login=true_login, is_admin=is_admin)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return True, f'Пользователь "{new_login}" успешно создан'


def delete_user(login):
    if not login:
        return False, 'Введите логин для удаления'
    user = User.query.filter_by(login=login).first()
    if not user:
        return False, f'Пользователь "{login}" не найден'
    db.session.delete(user)
    db.session.commit()
    return True, f'Пользователь "{login}" успешно удалён'


def get_user(entered_login, password):
    user = User.query.filter_by(login=entered_login).first()
    if not user or not user.check_password(password):
        return None, 'Неверно введён логин или пароль'
    return user, None

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


def delete_user_port(user, port_id):
    user_port = UserPort.query.filter_by(id=port_id, user_id=user.id).first()

    if user_port is None:
        return False, "Порт не найден"

    db.session.delete(user_port)
    db.session.commit()

    return True, "Ссылка удалена"


