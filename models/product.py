"""
Modelo de Producto - Nexus Marketplace
"""
from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'productos'

    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(200), nullable=False)
    precio      = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text)
    imagen      = db.Column(db.String(500))
    categoria   = db.Column(db.String(100), default='General')
    stock       = db.Column(db.Integer, default=10)
    lat         = db.Column(db.Float, default=20.5204)   # Geolocalización
    lng         = db.Column(db.Float, default=-100.8147)
    fecha_crea  = db.Column(db.DateTime, default=datetime.utcnow)
    activo      = db.Column(db.Boolean, default=True)
    usuario_id  = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # Relaciones
    items_carrito = db.relationship('CartItem', backref='producto', lazy=True)

    def to_dict(self):
        return {
            'id':          self.id,
            'nombre':      self.nombre,
            'precio':      self.precio,
            'descripcion': self.descripcion,
            'imagen':      self.imagen,
            'categoria':   self.categoria,
            'stock':       self.stock,
            'lat':         self.lat,
            'lng':         self.lng,
            'fecha_crea':  self.fecha_crea.isoformat(),
            'activo':      self.activo,
            'usuario_id':  self.usuario_id,
            'vendedor':    self.vendedor.nombre if self.vendedor else 'N/A'
        }
