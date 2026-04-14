from flask import flash, redirect, url_for
from flask_login import login_user

from flask_models import db, User


def create_user(new_login, true_login, password, is_admin=False):
    if not new_login or not password:
        return False, 'Заполните оба поля'
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
        flash('Неверно введён логин или пароль', 'error')
        return redirect(url_for('login_page.login'))

    login_user(user)
    flash(f'Добро пожаловать, {entered_login}!', 'success')
    return redirect(url_for('main_page.main'))

