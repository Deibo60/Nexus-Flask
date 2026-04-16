"""
Modelo de Usuario - Nexus Marketplace
"""
# CAMBIO CLAVE: Importamos db desde extensions para evitar el error circular
from extensions import db 
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id         = db.Column(db.Integer, primary_key=True)
    nombre     = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    rol        = db.Column(db.String(20), default='user')  # admin / user / invitado
    avatar     = db.Column(db.String(300), default='https://api.dicebear.com/7.x/avataaars/svg?seed=default')
    bio        = db.Column(db.Text, default='')
    fecha_reg  = db.Column(db.DateTime, default=datetime.utcnow)
    activo     = db.Column(db.Boolean, default=True)

    # Relaciones - IMPORTANTE: Solo funcionarán si tienes los otros modelos creados
    # Si te da error de "KeyError", ponles un # al principio a estas 5 líneas:
    productos     = db.relationship('Product',  backref='vendedor',  lazy=True)
    publicaciones = db.relationship('Post',     backref='autor',     lazy=True)
    comentarios   = db.relationship('Comment',  backref='usuario',   lazy=True)
    carrito       = db.relationship('CartItem', backref='usuario',   lazy=True)
    ordenes       = db.relationship('Order',    backref='cliente',   lazy=True)

    def to_dict(self):
        return {
            'id':       self.id,
            'nombre':   self.nombre,
            'email':    self.email,
            'rol':      self.rol,
            'avatar':   self.avatar,
            'bio':      self.bio,
            'fecha_reg': self.fecha_reg.isoformat() if self.fecha_reg else None,
            'activo':   self.activo
        }

    def __repr__(self):
        return f'<User {self.email}>'