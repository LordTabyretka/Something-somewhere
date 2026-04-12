from flask import Flask, render_template, request, redirect, url_for, flash
from flask_models import db, User
from flask_login import LoginManager, login_required, logout_user, current_user
from data_base import create_user, delete_user, get_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your-secret-key-here'

db.init_app(app)

with app.app_context():
    db.create_all()


login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        entered_login = request.form.get('login')
        password = request.form.get('password')
        return get_user(entered_login, password)
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for('login'))


@app.route("/main")
@login_required
def main():
    return render_template("main.html")


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if not current_user.is_admin:
        flash("Доступ запрещён. Требуются права администратора.", "error")
        return redirect(url_for('main'))
    if request.method == 'POST':
        new_login = request.form.get('login')
        password = request.form.get('password')

        if 'create' in request.form:
            is_admin = request.form.get('is_admin') == 'yes'
            success, msg = create_user(new_login, password, is_admin)
            flash(msg, 'success' if success else 'error')
            return redirect(url_for('admin'))

        elif 'delete' in request.form:
            if current_user.login == new_login:
                flash("Нельзя удалить самого себя", "error")
                return redirect(url_for('admin'))
            success, msg = delete_user(new_login)
            flash(msg, 'success' if success else 'error')
            return redirect(url_for('admin'))

        return redirect(url_for('admin'))

    return render_template("admin.html")

@app.route("/check-api", methods=["POST"])
@login_required
def check_api():
    flash("Функционал проверки в разработке", "info")
    return redirect(url_for('main'))

@app.route("/confirm-api", methods=["POST"])
@login_required
def confirm_api():
    flash("Функционал подтверждения в разработке", "info")
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)