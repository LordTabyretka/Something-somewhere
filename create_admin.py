import os
import getpass

from dotenv import load_dotenv
from flask import Flask

from flask_models import db, User


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL не задан в .env")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
db.init_app(app)


def main():
    print("=== Создание администратора ===")

    login = input("Логин: ").strip()
    if not login:
        print("Ошибка: логин не может быть пустым.")
        return

    true_login = input(
        f"Рабочий логин [{login}]: "
    ).strip() or login

    password = getpass.getpass("Пароль: ")
    password_repeat = getpass.getpass("Повторите пароль: ")

    if not password:
        print("Ошибка: пароль не может быть пустым.")
        return

    if password != password_repeat:
        print("Ошибка: пароли не совпадают.")
        return

    with app.app_context():
        user = User.query.filter_by(login=login).first()

        if user:
            user.true_login = true_login
            user.set_password(password)
            user.is_admin = True
            db.session.commit()
            print(f'Пользователь "{login}" теперь администратор.')
            return

        if User.query.filter_by(true_login=true_login).first():
            print(f'Ошибка: рабочий логин "{true_login}" уже используется.')
            return

        user = User(
            login=login,
            true_login=true_login,
            is_admin=True,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print(f'Администратор "{login}" успешно создан.')


if __name__ == "__main__":
    main()
