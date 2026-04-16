from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# Inicializamos las extensiones "vacías" para evitar el error de importación circular
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
cors = CORS()