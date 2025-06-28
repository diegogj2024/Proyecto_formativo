from flask import Flask,request,render_template,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
db = SQLAlchemy()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://root:yKKnLeAD9yFZvbmdc7qL1jagKw50qxx8@dpg-d1d9bk15pdvs73ahmfv0-a.oregon-postgres.render.com/esmir_krng'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'creacionesesmir@gmail.com'
app.config['MAIL_PASSWORD'] = 'fhkz aomg wxuw pxmj'
app.config['MAIL_DEFAULT_SENDER'] = 'creacionesesmir@gmail.com'


class Ubicacion(db.Model):
    __tablename__ = 'ubicacion'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    direccion = db.Column(db.String(255))
    clientes = db.relationship('Cliente', backref='ubicacion', lazy=True)


class Cliente(db.Model):
    __tablename__ = 'cliente'
    cedula = db.Column(db.BigInteger, primary_key=True)
    apellido = db.Column(db.String(100))
    correo = db.Column(db.String(100))
    telefono = db.Column(db.String(15))
    nombre = db.Column(db.String(100))
    password=db.Column(db.String(100))
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicacion.id'))


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
    cedula = db.Column(db.BigInteger, db.ForeignKey('cliente.cedula'))
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'))
    factura = db.relationship('Factura', backref='compra', uselist=False)


class Factura(db.Model):
    __tablename__ = 'factura'
    id_compra = db.Column(db.Integer, db.ForeignKey('compra.id_compra'), primary_key=True)
    fecha = db.Column(db.Date)
    monto_total = db.Column(db.Numeric(10, 2))

mail = Mail(app)

db.init_app(app)


import consultas

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
    exito, mensaje2 = consultas.validar_login(email, password)
    if exito:
        return redirect(url_for('catalogo'))
    else:
        return render_template('inicio_sesion.html', mensaje2=mensaje2)


@app.route('/registrarse', methods=['POST'])
def registrarse():
    nombre=request.form['name']
    correo=request.form['email']
    password=request.form['password']
    cedula=request.form['cedula']
    direccion=request.form['direccion']
    apellido=request.form['apellido']
    telefono=request.form['telefono']
    validacion=consultas.validar_registro(cedula,apellido,correo,telefono,nombre,password,direccion)
    if validacion==2:
       return redirect(url_for('catalogo'))
    elif validacion==1:
        return render_template('inicio_sesion.html', mensaje="esta ubicacion ya existe")
    elif validacion==4:
        return render_template('inicio_sesion.html', mensaje="esta cedula ya esta registrada")
    else:
        return render_template('inicio_sesion.html', mensaje="este correo ya existe")
    
@app.route('/mostrar_recuperar')
def mostrar_recuperar():
    return render_template('recuperacion.html')

@app.route('/recuperar', methods=['POST'])
def recuperar():
    correo = request.form['email']
    aviso=consultas.nueva_contraseña(correo)
    return render_template('recuperacion.html', aviso=aviso)




if __name__ == '__main__':
    app.run(debug=True)