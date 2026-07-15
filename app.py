from flask import Flask
from flask_migrate import Migrate

from flask_models import db, User
from flask_login import LoginManager
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
migrate = Migrate(app, db)

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


if __name__ == '__main__':
    app.run(debug=True)
