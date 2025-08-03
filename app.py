from flask import Flask,request,render_template,redirect, url_for,session,flash
from collections import defaultdict
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os
db = SQLAlchemy()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://root:iwTU47llUDaJ5Nv5gB2xZoJ8bYlyIVja@dpg-d21vi3qdbo4c73emg960-a.oregon-postgres.render.com/esmir_buu7'
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
    id_compra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cedula = db.Column(db.BigInteger, db.ForeignKey('cliente.cedula'))
    detalle_compra = db.relationship('DetalleCompra', backref='compra', uselist=False)


class DetalleCompra(db.Model):
    __tablename__='detallecompra'
    id_compra = db.Column(db.Integer, db.ForeignKey('compra.id_compra'))
    id_detalle_compra=db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_producto=db.Column(db.String(20),nullable=False)
    talla=db.Column(db.String(5), nullable=False)
    cantidad=db.Column(db.Integer, nullable=False)
    precio_producto=db.Column(db.Integer, nullable=False)


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
    busqueda = request.args.get('busqueda', '')
    categoria_id = request.args.get('categoria', '')
    cedula_U=session.get('usuario_id')
    carro=Carrito.query.filter_by(cedula=cedula_U).first()

    query = Producto.query

    if busqueda:
        query = query.filter(Producto.nombre_producto.ilike(f"%{busqueda}%"))
    if categoria_id:
        query = query.join(Producto.categorias).filter(Categoria.id_categoria == categoria_id)

    productos = query.all()
    categorias = Categoria.query.all()

    tallas_por_producto = {}
    for producto in productos:
        inventarios = Inventario.query.filter_by(id_producto=producto.id_producto).all()
        tallas_info = {}
        for inv in inventarios:
            talla = Talla.query.get(inv.id_talla)
            tallas_info[inv.id_talla] = {
                'nombre_talla': talla.nombre_talla,
                'cantidad': inv.cantidad
            }
        tallas_por_producto[producto.id_producto] = tallas_info

    return render_template('catalogo.html',productos=productos,categorias=categorias,tallas_por_producto=tallas_por_producto,cedula_U=cedula_U,carro=carro)


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
    acumulador=0
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
    for item in datos:
        precio=item['producto'].precio 
        cantidad=item['detalle'].cantidad
        monto=precio*cantidad
        acumulador+=monto
    return render_template('carrito.html',datos=datos,acumulador=acumulador)

@app.route('/guardar_en_carrito',methods=['POST'])
def guardar_en_carrito():
    if 'usuario_id' in session:
        id_produ = request.form.get("id_p")
        id_talla_seleccionada = request.form.get(f"talla_{id_produ}")
        cantidad = request.form.get(f"cantidad_{id_talla_seleccionada}")
        consultas.guardar_detalles_carrito(id_produ,cantidad,id_talla_seleccionada)
        return redirect(url_for('catalogo'))
    else:
        flash("Debes inicar sesion primero si deseas realizar una compra")
        return redirect(url_for('catalogo'))

@app.route('/cerrar_sesion')
def cerrar_sesion():
    consultas.cerrar_Sesion()
    cedula=session.get('usuario_id')
    return render_template('index.html',cedula=cedula)

@app.route('/compra')
def compra():
    cedula_U=session.get('usuario_id')
    carrito=Carrito.query.filter_by(cedula=cedula_U).first()
    datos=[]
    acumulador=0
    detalles = DetalleCarrito.query.filter_by(id_carrito=carrito.id_carrito).all()
    for detalle in detalles:
        inventario = Inventario.query.filter_by(id_inventario=detalle.id_inventario).first()
        producto=Producto.query.filter_by(id_producto=inventario.id_producto).first()
        talla=Talla.query.filter_by(id_talla=inventario.id_talla).first()
        inventario.cantidad -= detalle.cantidad
        datos.append({
            'carrito': carrito,
            'detalle': detalle,
            'inventario': inventario,
            'producto':producto,
            'talla': talla
        })
    consultas.guardar_compra(datos)
    db.session.commit()
    return redirect(url_for('catalogo'))

@app.route('/Actualizar_usuario')
def Actualizar_usuario():
    cedula_U=session.get('usuario_id')
    cliente =Cliente.query.filter_by(cedula=cedula_U).first()
    ubicacion=Ubicacion.query.filter_by(id=cliente.ubicacion_id).first()
    return render_template('actualizar_datos.html',cliente=cliente,ubicacion=ubicacion)

@app.route('/actualizar_al_usuario',methods=['POST'])
def actualizar_al_usuario():
    nombre=request.form['nombreU']
    apellido=request.form['apellidoU']
    correo=request.form['correoU']
    telefono=request.form['telefonoU']
    password=request.form['password']
    ubicacion=request.form['ubicacion']
    aviso=consultas.actualizar_usuario(nombre,apellido,correo,telefono,password,ubicacion)
    cedula_U=session.get('usuario_id')
    cliente =Cliente.query.filter_by(cedula=cedula_U).first()
    ubicacion=Ubicacion.query.filter_by(id=cliente.ubicacion_id).first()
    return render_template('actualizar_datos.html',cliente=cliente,ubicacion=ubicacion,aviso=aviso)


@app.route('/historial_compras')
def historial_compras():
    cedula_U = session.get('usuario_id')
    control = Compra.query.filter_by(cedula=cedula_U).all()
    datos = []

    for compra in control:
        historial_detalles = DetalleCompra.query.filter_by(id_compra=compra.id_compra).all()
        for historial in historial_detalles:
            datos.append({
                'historial': historial
            })

    return render_template('historial.html', datos=datos)

@app.route('/limpiar')
def limpiar():
    cedula_U = session.get('usuario_id')
    carrito = Carrito.query.filter_by(cedula=cedula_U).first()

    if carrito:
        DetalleCarrito.query.filter_by(id_carrito=carrito.id_carrito).delete()
        db.session.commit()

    return redirect(url_for('catalogo'))

    
@app.route('/ventas')
def ventas():
    compras = Compra.query.all()
    datos = []

    for compra in compras:
        detalles = DetalleCompra.query.filter_by(id_compra=compra.id_compra).all()
        cedula=Cliente.query.filter_by(cedula=compra.cedula).first()
        for detalle in detalles:
            datos.append({
                'historial': detalle,
                'compra': compra,
                'cliente':cedula
            })

    return render_template('historial_admins.html', datos=datos)


@app.route('/editar_categoria')
def editar_categoria():
    categoria=Categoria.query.all()
    return render_template('categorias.html',categoria=categoria)

@app.route('/update_cat',methods=['POST'])
def update_cat():
    idcat=request.form['id_categoria']
    categoria=Categoria.query.filter_by(id_categoria=idcat).first()
    return render_template('editar_categoria.html',categoria=categoria)

@app.route('/actualizar_cat',methods=['POST'])
def actualizar_cat():
    idcat=request.form['idcat']
    nombrecat=request.form['nombrec']
    aviso=consultas.actualizar_categoria(idcat,nombrecat)
    return redirect(url_for('editar_categoria'))

@app.route('/ver_clientes')
def ver_clientes():
    cedula_U = session.get('usuario_id')
    clientes = Cliente.query.filter(Cliente.cedula != cedula_U).all()
    
    datos = []
    for detalle in clientes:
        ubicacion=Ubicacion.query.filter_by(id=detalle.ubicacion_id).first()
        datos.append({
            'Cliente': detalle,
            'Ubicacion': ubicacion,
        })
    return render_template('ver_clientes.html', datos=datos)

@app.route('/historial_clientes', methods=['POST'])
def historial_clientes():
    cedula = request.form['cedulac']
    compras = Compra.query.filter_by(cedula=cedula).all()

    datos_agrupados = defaultdict(list)

    for compra in compras:
        detalles = DetalleCompra.query.filter_by(id_compra=compra.id_compra).all()

        for detalle in detalles:
            datos_agrupados[compra.id_compra].append({
                'historial': detalle
            })

    return render_template('historial_admin_cliente.html', datos=datos_agrupados)

    
if __name__ == '__main__':
    app.run(debug=True)