from app import app, db, Cliente, Ubicacion,mail,Message,Producto,Categoria,os,Inventario,session,Carrito,DetalleCarrito,Compra,DetalleCompra
from werkzeug.utils import secure_filename
import secrets
from flask import flash
def validar_login(email, password):
    with app.app_context():
        usuario = Cliente.query.filter_by(correo=email).first()

    if usuario:
        if usuario.password == password:
            if email=="diegogarcia0809@outlook.com":
                return True, 4
            else:
                return True, usuario.nombre
        else:
            mensaje= "Contraseña incorrecta"
            return False,mensaje
    else:
        mensaje= "Usuario no encontrado"
        return False,mensaje

def validar_registro(cedula,apellido,correo,telefono,nombre,password,direccion):
    with app.app_context():
        try:
            correo_existe=Cliente.query.filter_by(correo=correo).first()

            if not correo_existe :                  
                nueva_ubicacion = Ubicacion(direccion=direccion)
                db.session.add(nueva_ubicacion)
                db.session.commit()
                nuevo_cliente =Cliente(
                cedula=cedula,
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                telefono=telefono,
                password=password,
                ubicacion_id=nueva_ubicacion.id
                )
                db.session.add(nuevo_cliente)
                db.session.commit()
                print("Cliente creado correctamente.") 
                return 2   
            else:
                if correo_existe:
                    print("correo ya existe")
                    return 3
                
                
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
            return 4


def generar_token():
    return secrets.token_urlsafe(12) 

def nueva_contraseña(correo):
    with app.app_context():
     usuario = Cliente.query.filter_by(correo=correo).first()

     if not usuario:
         aviso="este correo no esta registrado en Creaciones Esmir"
         return aviso
    
     clave=generar_token()
     usuario.password=clave
     db.session.commit()

     mensaje = Message('Recuperación de cuenta', recipients=[correo])
     mensaje.body = f'Se ha restablecido tu contraseña temporal:\n {clave}\nPor favor, cámbiala al iniciar sesión.'
     mail.send(mensaje)

     aviso="se ha enviado una nueva contraseña a tu correo revisalo porfavor"
     return aviso


def guardar_Categoria(categoria):
    with app.app_context():
        gcategoria= Categoria.query.filter_by(nombre_categoria=categoria).first()
        if gcategoria:
            aviso="esta categoria ya existe"
            return aviso
        else:
            nueva_categoria=Categoria(
                nombre_categoria=categoria
            )
            db.session.add(nueva_categoria)
            db.session.commit()
            aviso="categoria guardada exitosamente"
            return aviso
        
        
def guardar_productos(nombrep, descripcionp, categorias, imagen_nombre, preciop, tallas, form):
    with app.app_context():
        producto = Producto.query.filter_by(nombre_producto=nombrep).first()
        preciop = float(preciop)

        if preciop <= 0:
            return "El precio debe ser mayor a 0, intente nuevamente"

        if producto:
            return "Este producto ya está registrado"

        nuevo_producto = Producto(
            nombre_producto=nombrep,
            imagen=imagen_nombre,
            descripcion=descripcionp,
            precio=preciop
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        for id_categoria in categorias:
            categoria = Categoria.query.get(int(id_categoria))
            if categoria:
                nuevo_producto.categorias.append(categoria)

        db.session.commit()

        for id_talla in tallas:
            cantidad_key = f'cantidad_{id_talla}'
            cantidad = int(form.get(cantidad_key, 0))

            if cantidad <= 0:
                continue

            inventario = Inventario(
                id_producto=nuevo_producto.id_producto,
                id_talla=int(id_talla),
                cantidad=cantidad
            )
            db.session.add(inventario)

        db.session.commit()
        return "Producto guardado exitosamente"

        
def actualizar(nombre, descripcion, categorias, precio, imagen, id_producto, tallas, form):
     with app.app_context():
        producto = Producto.query.get(id_producto)
        if not producto:
            return "Producto no encontrado"

        producto.nombre_producto = nombre
        producto.descripcion = descripcion
        producto.precio = float(precio)

        if imagen and imagen.filename != "":
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], imagen.filename)
            if not os.path.exists(ruta):
                ruta_antigua = os.path.join(app.config['UPLOAD_FOLDER'], producto.imagen)
                if os.path.exists(ruta_antigua):
                    os.remove(ruta_antigua)
                imagen.save(ruta)
            producto.imagen = imagen.filename

        producto.categorias.clear()
        for id_cat in categorias:
            categoria = Categoria.query.get(int(id_cat))
            if categoria:
                producto.categorias.append(categoria)

        Inventario.query.filter_by(id_producto=id_producto).delete()
        for id_talla in tallas:
            cantidad = int(form.get(f'cantidad_{id_talla}', 0))
            if cantidad > 0:
                inventario = Inventario(id_producto=id_producto, id_talla=int(id_talla), cantidad=cantidad)
                db.session.add(inventario)

        db.session.commit()
        return "Producto actualizado correctamente"

def cerrar_Sesion():
    session.clear()

def guardar_detalles_carrito(id_produ,cantidad,id_talla_seleccionada):
    with app.app_context():
        cedula_U=session.get('usuario_id')
        verificar_carro=Carrito.query.filter_by(cedula=cedula_U).first()
        inventario = Inventario.query.filter_by(id_producto=id_produ, id_talla=id_talla_seleccionada).first()
        if verificar_carro:
            nuevo_detalle_Carrito=DetalleCarrito(
                id_carrito=verificar_carro.id_carrito,
                id_inventario=inventario.id_inventario,
                cantidad=cantidad
            )
            db.session.add(nuevo_detalle_Carrito)
            db.session.commit()
        else:
            nuevo_carrito=Carrito(
                cedula=cedula_U
            )
            db.session.add(nuevo_carrito)
            db.session.commit()
            verificar_carro2=Carrito.query.filter_by(cedula=cedula_U).first()

            nuevo_detalle_Carrito=DetalleCarrito(
                id_carrito=verificar_carro2.id_carrito,
                id_inventario=inventario.id_inventario,
                cantidad=cantidad
            )
            db.session.add(nuevo_detalle_Carrito)
            db.session.commit()

def actualizar_usuario(nombre,apellido,correo,telefono,password,ubicacion):
    with app.app_context():
        cedula = session.get('usuario_id')
        cliente = Cliente.query.filter_by(cedula=cedula).first()

        try:
            correo_existente = Cliente.query.filter(Cliente.correo == correo, Cliente.cedula != cedula).first()
        
            if correo_existente:
                return "Este correo ya existe"

            usuario = Cliente.query.get(cedula)
            ubicacion_obj = Ubicacion.query.get(usuario.ubicacion_id)
            usuario.nombre = nombre
            usuario.apellido = apellido
            usuario.correo = correo
            usuario.telefono = telefono
            usuario.password = password
            ubicacion_obj.direccion = ubicacion  
            db.session.commit()
            return "Se actualizó con éxito"

        except Exception as e:
            return f"Error: {str(e)}"

def guardar_compra(datos):
    with app.app_context():
       cedula=session.get('usuario_id')
       nueva_compra=Compra(
       cedula=cedula
       )
       db.session.add(nueva_compra)
       db.session.commit()
       for items in datos:
            nuevo_detalle_compra=DetalleCompra(
                id_compra=nueva_compra.id_compra,
                nombre_producto=items['producto'].nombre_producto,
                talla=items['talla'].nombre_talla,
                cantidad=items['detalle'].cantidad,
                precio_producto=items['producto'].precio
            )
            db.session.add(nuevo_detalle_compra)
            db.session.commit()
    
       carro=Carrito.query.filter_by(cedula=cedula).first()
       if carro:
            detalles = DetalleCarrito.query.filter_by(id_carrito=carro.id_carrito).all()
            for detalle in detalles:
                db.session.delete(detalle)
                db.session.commit()
       flash("compra realizada con exito")

def actualizar_categoria(idcat,nombrecat):
    with app.app_context():
        actualizar=Categoria.query.get(idcat)
        actualizar.nombre_categoria=nombrecat
        db.session.commit()
        return "categoria actualizada exitosamente"
