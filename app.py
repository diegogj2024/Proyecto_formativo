from flask import Flask,request,render_template,redirect, url_for,session,flash
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

app.config['SESSION_PERMANENT'] = False

app.secret_key = 'f45@sdA54f!asd9wq8e*as'

db = SQLAlchemy()

producto_categoria = db.Table('producto_categoria',
    db.Column('id_producto', db.Integer, db.ForeignKey('producto.id_producto'), primary_key=True),
    db.Column('id_categoria', db.Integer, db.ForeignKey('categoria.id_categoria'), primary_key=True)
)

class Ubicacion(db.Model):
    __tablename__ = 'ubicacion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    direccion = db.Column(db.String(255))
    clientes = db.relationship('Cliente', backref='ubicacion', lazy=True)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    cedula = db.Column(db.BigInteger, primary_key=True)
    apellido = db.Column(db.String(100))
    correo = db.Column(db.String(100))
    telefono = db.Column(db.String(15))
    nombre = db.Column(db.String(100))
    password = db.Column(db.String(100))
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicacion.id'))


class Categoria(db.Model):
    __tablename__ = 'categoria'  
    id_categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_categoria = db.Column(db.String(100))
    productos = db.relationship('Producto', secondary=producto_categoria, backref='categorias')


class Empresa(db.Model):
    __tablename__ = 'empresa'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    rut = db.Column(db.String(20), unique=True)
    direccion = db.Column(db.String(100))


class Producto(db.Model):
    __tablename__ = 'producto'
    id_producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_producto = db.Column(db.String(100))
    imagen = db.Column(db.String(100))
    descripcion = db.Column(db.String(100))
    precio = db.Column(db.Numeric(10, 2))
    inventarios = db.relationship('Inventario', backref='producto', lazy=True)



class Talla(db.Model):
    __tablename__ = 'talla'
    id_talla = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_talla = db.Column(db.String(10), unique=True, nullable=False)
    inventarios = db.relationship('Inventario', backref='talla', lazy=True)



class Inventario(db.Model):
    __tablename__ = 'inventario'
    id_inventario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'), nullable=False)
    id_talla = db.Column(db.Integer, db.ForeignKey('talla.id_talla'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)



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

class Carrito(db.Model):
    __tablename__ = 'carrito'
    id_carrito = db.Column(db.Integer, primary_key=True,autoincrement=True)
    cedula = db.Column(db.Integer, db.ForeignKey('cliente.cedula'), nullable=False)
    detalles = db.relationship('DetalleCarrito', backref='carrito', cascade="all, delete-orphan")

class DetalleCarrito(db.Model):
    __tablename__ = 'detallecarrito'
    id_detalle = db.Column(db.Integer, primary_key=True,autoincrement=True)
    id_carrito = db.Column(db.Integer, db.ForeignKey('carrito.id_carrito'), nullable=False)
    id_inventario = db.Column(db.Integer, db.ForeignKey('inventario.id_inventario'), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    inventario = db.relationship('Inventario')
    
mail = Mail(app)

db.init_app(app)


import consultas

with app.app_context():
    db.create_all()
    
@app.route('/')
def index():
    cedula=session.get('usuario_id')
    return render_template('index.html',cedula=cedula)

@app.route('/catalogo')
def catalogo():
    cedula_U=session.get('usuario_id')
    productos = Producto.query.all()
    carro=Carrito.query.filter_by(cedula=cedula_U).first()
    tallas_por_producto = {} 

    for producto in productos:
        inventario = Inventario.query.filter_by(id_producto=producto.id_producto).all()
        tallas_con_cantidades = {}

        for item in inventario:
            talla = Talla.query.get(item.id_talla)
            if talla:
                tallas_con_cantidades[talla.id_talla] ={
                    'nombre_talla': talla.nombre_talla,
                    'cantidad': item.cantidad
                }
        
        tallas_por_producto[producto.id_producto] = tallas_con_cantidades

    return render_template('catalogo.html', productos=productos, tallas_por_producto=tallas_por_producto,cedula_U=cedula_U,carro=carro)


@app.route('/inicio_sesion')
def inicio_sesion():
    return render_template('inicio_sesion.html')

@app.route('/iniciar_sesion', methods=['POST'])
def iniciar_Sesion():
    email=request.form['email']
    password=request.form['password']
    exito, mensaje2 = consultas.validar_login(email, password)
    cliente = Cliente.query.filter_by(correo=email).first()
    if exito:
        if mensaje2==4:
            session['usuario_id'] = cliente.cedula
            session['correo'] = cliente.correo
            return render_template('admin.html')
        else:
            session['usuario_id'] = cliente.cedula
            session['correo'] = cliente.correo
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
       return redirect(url_for('inicio_sesion'))
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
    tallas=Talla.query.all()
    return render_template('crear_productos.html', categorias=categorias,tallas=tallas)

@app.route('/ingresar_productos', methods=['POST'])
def ingresar_productos():
    imagen = request.files['imagenp']
    nombrep = request.form['nombrep']
    descripcionp = request.form['descripcionp']
    categorias_seleccionadas = request.form.getlist('categorias')
    preciop = request.form['preciop']
    tallas_seleccionadas = request.form.getlist('tallas')

    if imagen:
        ruta_guardado = os.path.join(app.config['UPLOAD_FOLDER'], imagen.filename)
        imagen.save(ruta_guardado)
        imagen_nombre = imagen.filename

        aviso = consultas.guardar_productos(nombrep, descripcionp, categorias_seleccionadas, imagen_nombre, preciop, tallas_seleccionadas, request.form)

        categorias = Categoria.query.all()
        tallas = Talla.query.all()
        return render_template('crear_productos.html', aviso=aviso, categorias=categorias, tallas=tallas)


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
    id_producto = request.form['id_p']
    categorias = Categoria.query.all()
    tallas = Talla.query.all()
    producto = Producto.query.get_or_404(id_producto)

    categorias_seleccionadas = [c.id_categoria for c in producto.categorias]

    inventario = Inventario.query.filter_by(id_producto=id_producto).all()
    tallas_con_cantidades = {}
    for item in inventario:
        talla = Talla.query.get(item.id_talla)
        tallas_con_cantidades[item.id_talla] = {"cantidad": item.cantidad,"nombre": talla.nombre_talla}


    return render_template('formulario_editar_productos.html', producto=producto,categorias=categorias,tallas=tallas,categorias_seleccionadas=categorias_seleccionadas,tallas_con_cantidades=tallas_con_cantidades)

@app.route('/actualizar',methods=['POST'])
def actualizar():
    id_producto = request.form['id_producto']
    nombre = request.form['nombrep']
    descripcion = request.form['descripcionp']
    categorias_seleccionadas = request.form.getlist('categorias')
    precio = request.form['preciop']
    imagen = request.files['imagenp']
    tallas_seleccionadas = request.form.getlist('tallas')
    aviso = consultas.actualizar(nombre, descripcion, categorias_seleccionadas, precio, imagen, id_producto, tallas_seleccionadas, request.form)
    return redirect('/mostrar_editar_producto')

@app.route('/carrito')
def carrito():
    cedula_U=session.get('usuario_id')
    carrito=Carrito.query.filter_by(cedula=cedula_U).first()
    datos=[]
    detalles = DetalleCarrito.query.filter_by(id_carrito=carrito.id_carrito).all()
    for detalle in detalles:
        inventario = Inventario.query.filter_by(id_inventario=detalle.id_inventario).first()
        producto=Producto.query.filter_by(id_producto=inventario.id_producto).first()
        talla=Talla.query.filter_by(id_talla=inventario.id_talla).first()
        datos.append({
            'carrito': carrito,
            'detalle': detalle,
            'inventario': inventario,
            'producto':producto,
            'talla': talla
        })
    return render_template('carrito.html',datos=datos)

@app.route('/guardar_en_carrito',methods=['POST'])
def guardar_en_carrito():
    if 'usuario_id' in session:
        id_produ = request.form.get("id_p")
        id_talla_seleccionada = request.form.get(f"talla_{id_produ}")
        cantidad = request.form.get(f"cantidad_{id_talla_seleccionada}")
        consultas.guardar_detalles_carrito(id_produ,cantidad,id_talla_seleccionada)
        flash("guardao en el carrito")
        return redirect(url_for('catalogo'))
    else:
        flash("Debes inicar sesion primero si deseas realizar una compra")
        return redirect(url_for('catalogo'))

@app.route('/cerrar_sesion')
def cerrar_sesion():
    consultas.cerrar_Sesion()
    cedula=session.get('usuario_id')
    return render_template('index.html',cedula=cedula)

if __name__ == '__main__':
    app.run(debug=True)