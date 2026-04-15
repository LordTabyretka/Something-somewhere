from flask import Flask, redirect, url_for, flash, request

from API_requests import check_server_status, check_user_status, extend
from flask_models import db, User
from flask_login import LoginManager, login_required, current_user
from routes.admin import admin
from routes.login import login_page
from routes.main import main_page
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.getenv('APP_KEY')

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(admin)
app.register_blueprint(login_page)
app.register_blueprint(main_page)

login_manager = LoginManager(app)
login_manager.login_view = 'login_page.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/check-api", methods=["POST", "GET"])
@login_required
def check_api():
    if request.method == "POST":
        if 'check server status' in request.form:
            success, msg = check_server_status()
            flash(msg, 'success' if success else 'error')
            return redirect(url_for('main_page.main'))
        elif 'check user status' in request.form:
            true_login = current_user.true_login
            success, msg = check_user_status(true_login)
            flash(msg, 'success' if success else 'error')
            return redirect(url_for('main_page.main'))
        elif 'extend' in request.form:
            true_login = current_user.true_login
            success, msg = extend(true_login)
            flash(msg, 'success' if success else 'error')
            return redirect(url_for('main_page.main'))
    return redirect(url_for('main_page.main'))


if __name__ == '__main__':
    app.run(debug=True)
