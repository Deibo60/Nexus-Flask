"""
=============================================================
  NEXUS MARKETPLACE - Aplicación Principal
=============================================================
"""

from flask import Flask
from flask_cors import CORS
import os
from extensions import db, login_manager, bcrypt, cors

# 1. Definimos la ruta absoluta de la carpeta del proyecto
# Esto ayuda a que SQLite no se pierda buscando la carpeta 'instance'
basedir = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__)

    # ─── Configuración ─────────────────────────────────────
    app.config['SECRET_KEY'] = 'nexus-secret-key-2024-change-in-production'
    
    # CORRECCIÓN DE RUTA: Usamos 4 slashes para ruta absoluta en Windows/Linux
    # Esto apunta directamente a: C:\Tu\Ruta\nexus-marketplace\instance\nexus.db
    db_path = os.path.join(basedir, 'instance', 'nexus.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # ─── Inicializar extensiones ────────────────────────────
    db.init_app(app)
    cors.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder.'

    # ─── Registrar Blueprints ───────────────────────────────
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.api import api_bp
    from routes.admin import admin_bp
    from routes.social import social_bp
    from routes.ecommerce import ecommerce_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(social_bp, url_prefix='/social')
    app.register_blueprint(ecommerce_bp, url_prefix='/shop')

    # ─── Crear tablas y datos iniciales ────────────────────
    with app.app_context():
        # Importamos models para que SQLAlchemy registre las tablas
        import models
        db.create_all()
        seed_data()

    return app

def seed_data():
    """Inserta datos de prueba si la BD está vacía."""
    from models.user import User
    from models.product import Product
    from models.post import Post
    from werkzeug.security import generate_password_hash

    try:
        if User.query.count() == 0:
            print("🌱 Insertando datos de prueba...")
            # Usuarios
            users = [
                User(nombre='Admin Nexus', email='admin@nexus.com',
                     password=generate_password_hash('admin123'), rol='admin'),
                User(nombre='María García', email='maria@nexus.com',
                     password=generate_password_hash('user123'), rol='user'),
            ]
            for u in users:
                db.session.add(u)
            db.session.commit()

            # Productos (Asegúrate que el campo sea vendedor_id o usuario_id según tu model)
            p1 = Product(nombre='MacBook Pro M3', precio=45999.00,
                         descripcion='Laptop chip M3, 16GB RAM.',
                         vendedor_id=1)
            db.session.add(p1)
            db.session.commit()

            print("✅ Datos de prueba insertados correctamente.")
    except Exception as e:
        print(f"⚠️ Error al insertar datos (posiblemente ya existen): {e}")
        db.session.rollback()

@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)