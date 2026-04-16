"""
Modelos de Publicaciones, Comentarios, Carrito y Órdenes
"""
from app import db
from datetime import datetime

# ─── Publicación (Post) ──────────────────────────────────────
class Post(db.Model):
    __tablename__ = 'publicaciones'

    id         = db.Column(db.Integer, primary_key=True)
    contenido  = db.Column(db.Text, nullable=False)
    imagen     = db.Column(db.String(500))
    likes      = db.Column(db.Integer, default=0)
    fecha      = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    comentarios = db.relationship('Comment', backref='publicacion', lazy=True,
                                  cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id':        self.id,
            'contenido': self.contenido,
            'imagen':    self.imagen,
            'likes':     self.likes,
            'fecha':     self.fecha.isoformat(),
            'usuario_id':self.usuario_id,
            'autor':     self.autor.nombre if self.autor else 'Anónimo',
            'avatar':    self.autor.avatar if self.autor else '',
            'num_comentarios': len(self.comentarios)
        }


# ─── Comentario ──────────────────────────────────────────────
class Comment(db.Model):
    __tablename__ = 'comentarios'

    id             = db.Column(db.Integer, primary_key=True)
    contenido      = db.Column(db.Text, nullable=False)
    fecha          = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id     = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    publicacion_id = db.Column(db.Integer, db.ForeignKey('publicaciones.id'), nullable=False)

    def to_dict(self):
        return {
            'id':             self.id,
            'contenido':      self.contenido,
            'fecha':          self.fecha.isoformat(),
            'usuario_id':     self.usuario_id,
            'autor':          self.usuario.nombre if self.usuario else 'Anónimo',
            'publicacion_id': self.publicacion_id
        }


# ─── Carrito ─────────────────────────────────────────────────
class CartItem(db.Model):
    __tablename__ = 'carrito'

    id          = db.Column(db.Integer, primary_key=True)
    usuario_id  = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad    = db.Column(db.Integer, default=1)
    fecha       = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':          self.id,
            'usuario_id':  self.usuario_id,
            'producto_id': self.producto_id,
            'cantidad':    self.cantidad,
            'nombre':      self.producto.nombre if self.producto else '',
            'precio':      self.producto.precio if self.producto else 0,
            'imagen':      self.producto.imagen if self.producto else '',
            'subtotal':    (self.producto.precio * self.cantidad) if self.producto else 0
        }


# ─── Orden / Pedido ──────────────────────────────────────────
class Order(db.Model):
    __tablename__ = 'ordenes'

    id          = db.Column(db.Integer, primary_key=True)
    usuario_id  = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    total       = db.Column(db.Float, nullable=False)
    estado      = db.Column(db.String(50), default='pendiente')  # pendiente/enviado/entregado
    fecha       = db.Column(db.DateTime, default=datetime.utcnow)
    detalles    = db.Column(db.Text)  # JSON con productos

    def to_dict(self):
        return {
            'id':         self.id,
            'usuario_id': self.usuario_id,
            'total':      self.total,
            'estado':     self.estado,
            'fecha':      self.fecha.isoformat(),
            'detalles':   self.detalles
        }
