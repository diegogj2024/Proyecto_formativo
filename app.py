from flask import Flask,request,render_template,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import consultas
db = SQLAlchemy()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://root:yKKnLeAD9yFZvbmdc7qL1jagKw50qxx8@dpg-d1d9bk15pdvs73ahmfv0-a.oregon-postgres.render.com/esmir_krng'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class Ubicacion(db.Model):
    __tablename__ = 'ubicacion'
    direccion = db.Column(db.String(255), primary_key=True)
    clientes = db.relationship('Cliente', backref='ubicacion', lazy=True)


class Cliente(db.Model):
    __tablename__ = 'cliente'
    cedula = db.Column(db.Integer, primary_key=True)
    apellido = db.Column(db.String(100))
    correo = db.Column(db.String(100))
    telefono = db.Column(db.String(15))
    nombre = db.Column(db.String(100))
    password=db.Column(db.String(100))
    direccion = db.Column(db.String(255), db.ForeignKey('ubicacion.direccion'))


class Categoria(db.Model):
    __tablename__ = 'categoria'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre_categoria = db.Column(db.String(100))
    productos = db.relationship('Producto', backref='categoria', lazy=True)


class Comentario(db.Model):
    __tablename__ = 'comentario'
    id_comentario = db.Column(db.Integer, primary_key=True)

    productos = db.relationship('Producto', backref='comentario', lazy=True)


class CreacionesEsmi(db.Model):
    __tablename__ = 'creacionesesmi'
    rut = db.Column(db.Integer, primary_key=True)

    productos = db.relationship('Producto', backref='creador', lazy=True)


class Producto(db.Model):
    __tablename__ = 'producto'
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre_producto = db.Column(db.String(100))
    id_comentario = db.Column(db.Integer, db.ForeignKey('comentario.id_comentario'))
    rut = db.Column(db.Integer, db.ForeignKey('creacionesesmi.rut'))
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'))
    precio = db.Column(db.Numeric(10, 2))

    compras = db.relationship('Compra', backref='producto', lazy=True)


class Compra(db.Model):
    __tablename__ = 'compra'
    id_compra = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.Integer, db.ForeignKey('cliente.cedula'))
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'))

    factura = db.relationship('Factura', backref='compra', uselist=False)


class Factura(db.Model):
    __tablename__ = 'factura'
    id_compra = db.Column(db.Integer, db.ForeignKey('compra.id_compra'), primary_key=True)
    fecha = db.Column(db.Date)
    monto_total = db.Column(db.Numeric(10, 2))

db.init_app(app)


with app.app_context():
    db.create_all()
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html')

@app.route('/inicio_sesion')
def inicio_sesion():
    return render_template('inicio_sesion.html')

@app.route('/iniciar_sesion', methods=['POST'])
def iniciar_Sesion():
    email=request.form['email']
    password=request.form['password']
    consultas.validar_datos_incio_sesion(email,password)
    return render_template('index.html')


@app.route('/registrarse', methods=['POST'])
def registrarse():
    nombre=request.form['name']
    email=request.form['email']
    password=request.form['password']
    consultas.validar_registro(nombre,email,password)
    return redirect(url_for('catalogo'))




if __name__ == '__main__':
    app.run(debug=True)