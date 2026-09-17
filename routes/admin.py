from flask import render_template, redirect, url_for, request, Blueprint
from flask_login import current_user, login_required

from data_base import delete_user, create_user
from notifications import create_notification

admin = Blueprint('admin', __name__)


@admin.route('/admin', methods=["GET", "POST"])
@login_required
def admin_panel():
    if not current_user.is_admin:
        create_notification(
            "Доступ запрещён. Требуются права администратора.",
            "error",
            "main_page.main"
        )
        return redirect(url_for('main_page.main'))

    if request.method == 'POST':
        new_login = request.form.get('login')
        password = request.form.get('password')
        true_login = request.form.get('true_login')

        if 'create' in request.form:
            is_admin = request.form.get('is_admin') == 'yes'
            success, msg = create_user(new_login, true_login, password, is_admin)
            create_notification(
                msg,
                'success' if success else 'error',
                'admin.admin_panel'
            )
            return redirect(url_for('.admin_panel'))

        elif 'delete' in request.form:
            if current_user.login == new_login:
                create_notification(
                    "Нельзя удалить самого себя",
                    "error",
                    "admin.admin_panel"
                )
                return redirect(url_for('.admin_panel'))
            success, msg = delete_user(new_login)
            create_notification(
                msg,
                'success' if success else 'error',
                'admin.admin_panel'
            )
            return redirect(url_for('.admin_panel'))

        return redirect(url_for('.admin_panel'))

    return render_template("admin.html")
