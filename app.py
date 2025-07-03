from flask import Flask,request,render_template,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os
db = SQLAlchemy()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://root:yKKnLeAD9yFZvbmdc7qL1jagKw50qxx8@dpg-d1d9bk15pdvs73ahmfv0-a.oregon-postgres.render.com/esmir_krng'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = 'static/productos'

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
    id_categoria = db.Column(db.Integer, primary_key=True,autoincrement=True)
    nombre_categoria = db.Column(db.String(100))
    productos = db.relationship('Producto', backref='categoria', lazy=True)


class Descripcion(db.Model):
    __tablename__ = 'descripcion'
    id_descripcion = db.Column(db.Integer, primary_key=True,autoincrement=True)
    descripcion = db.Column(db.String(100))
    productos = db.relationship('Producto', backref='comentario', lazy=True)


class Empresa(db.Model):
    __tablename__ = 'empresa'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    rut = db.Column(db.String(20), unique=True)
    direccion = db.Column(db.String(100))


class Producto(db.Model):
    __tablename__ = 'producto'
    id_producto = db.Column(db.Integer, primary_key=True,autoincrement=True)
    nombre_producto = db.Column(db.String(100))
    imagen=db.Column(db.String(100))
    cantidad=db.Column(db.Integer)
    id_descripcion = db.Column(db.Integer, db.ForeignKey('descripcion.id_descripcion'))
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'))
    precio = db.Column(db.Numeric(10, 2))


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
        if mensaje2==4:
            return render_template('admin.html')
        else:
            return redirect(url_for('catalogo'))
    else:
        return render_template('inicio_sesion.html', mensaje2=mensaje2)

@app.route('/admin')
def admin():
    return render_template('admin.html')

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


@app.route('/crear_productos')
def crear_productos():
    categorias = Categoria.query.all()
    return render_template('crear_productos.html', categorias=categorias)

@app.route('/ingresar_productos', methods=['POST'])
def ingresar_productos():
    imagen=request.files['imagenp']
    nombrep=request.form['nombrep']
    cantidadp=request.form['cantidadp']
    descripcionp=request.form['descripcionp']
    categoria=request.form['categoria']
    preciop=request.form['preciop']

    if imagen:
        ruta_guardado = os.path.join(app.config['UPLOAD_FOLDER'], imagen.filename)
        imagen.save(ruta_guardado)
        imagen_nombre=imagen.filename
        aviso=consultas.guardar_productos(nombrep,cantidadp,descripcionp,categoria,imagen_nombre,preciop)
        return render_template('crear_productos.html',aviso=aviso)


@app.route('/crear_categoria')
def crear_categoria():
   return render_template('crear_categoria.html')

@app.route('/guardar_categoria', methods=['POST'])
def guardar_categoria():
    categoria=request.form['categorianame']
    aviso=consultas.guardar_Categoria(categoria)
    return render_template('crear_categoria.html',aviso=aviso)

@app.route('/mostrar_editar_producto')
def mostrar_editar_producto():
    productos=Producto.query.all()
    return render_template('editar_productos.html',productos=productos)

@app.route('/editar_producto', methods=['POST'])
def editar_producto():
    id_producto=request.form['id_p']
    categorias = Categoria.query.all()
    producto_Editar=Producto.query.filter_by(id_producto=id_producto).first()
    descripcion_e=Descripcion.query.filter_by(id_descripcion=producto_Editar.id_descripcion).first()
    return render_template('formulario_editar_productos.html',categorias=categorias,producto=producto_Editar,descripcion=descripcion_e)
@app.route('/actualizar',methods=['POST'])
def actualizar():
    nombre = request.form['nombrep']
    cantidad = request.form['cantidadp']
    descripcion = request.form['descripcionp']
    categoria = request.form['categoria']
    precio = request.form['preciop']
    imagen = request.files['imagenp']
    id_producto = request.form['id_producto']
    aviso=consultas.actualizar(nombre,cantidad,descripcion,categoria,precio,imagen,id_producto)
    producto = Producto.query.filter_by(id_producto=id_producto).first()
    descripcion_obj = Descripcion.query.filter_by(id_descripcion=producto.id_descripcion).first()
    categorias = Categoria.query.all()
    return render_template(
        'formulario_editar_productos.html',
        aviso=aviso,
        producto=producto,
        descripcion=descripcion_obj,
        categorias=categorias
    )

if __name__ == '__main__':
    app.run(debug=True)