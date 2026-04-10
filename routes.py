from flask import Blueprint, render_template

# Создаём blueprint для основных маршрутов
main_routes = Blueprint('main', __name__)

@main_routes.route("/")
def login():
    return render_template("login.html")

@main_routes.route("/main")
def main():
    return render_template("main.html")

@main_routes.route("/admin")
def admin():
    return render_template("admin.html")