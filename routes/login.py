from flask import render_template, request, Blueprint, redirect, url_for, jsonify
from flask_login import login_required, logout_user, login_user, current_user

from data_base import get_user
from notifications import create_notification

login_page = Blueprint('login_page', __name__)


@login_page.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_page.main'))
    if request.method == 'POST':
        entered_login = request.form.get('login')
        password = request.form.get('password')
        user, error = get_user(entered_login, password)

        if error:
            return jsonify({
                'success': False,
                'message': error
            }), 401

        login_user(user)
        create_notification(
            f'Добро пожаловать, {entered_login}!',
            'success',
            'main_page.main'
        )

        return jsonify({
            'success': True,
            'redirect_url': url_for('main_page.main')
        })

    return render_template("login.html")


@login_page.route("/logout")
@login_required
def logout():
    logout_user()
    create_notification(
        "Вы вышли из системы",
        "info",
        "login_page.login"
    )
    return redirect(url_for('login_page.login'))
