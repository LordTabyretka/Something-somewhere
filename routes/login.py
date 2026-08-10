from flask import render_template, request, Blueprint, flash, redirect, url_for
from flask_login import login_required, logout_user, login_user

from data_base import get_user

login_page = Blueprint('login_page', __name__)


@login_page.route("/", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        entered_login = request.form.get('login')
        password = request.form.get('password')
        user, error = get_user(entered_login, password)

        if error:
            flash('Неверно введён логин или пароль', 'error')
            return redirect(url_for('login_page.login'))

        login_user(user)
        flash(f'Добро пожаловать, {entered_login}!', 'success')

        return redirect(url_for('main_page.main'))

    return render_template("login.html")


@login_page.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for('login_page.login'))
