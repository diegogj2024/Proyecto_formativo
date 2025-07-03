from app import app, db, Cliente, Ubicacion,mail,Message,Producto,Descripcion,Categoria,os
from werkzeug.utils import secure_filename
import secrets

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
        
        
def guardar_productos(nombrep,cantidadp,descripcionp,categoriap,imagen_nombre,preciop):
    with app.app_context():
        producto = Producto.query.filter_by(nombre_producto=nombrep).first()
        cantidadp = int(cantidadp)
        preciop = float(preciop)
        if cantidadp <= 0 or preciop <= 0:
            aviso="El precio y/o cantidad debe ser mayor a 0, intente nuevamente"
            return aviso

        if producto:
            aviso="este producto ya esta registrado"
            return aviso
        else:
            nueva_descripcion=Descripcion(
                descripcion=descripcionp,
            )
            db.session.add(nueva_descripcion)
            db.session.commit()

            iddescripcion=Descripcion.query.filter_by(descripcion=descripcionp).first()
            nuevo_producto=Producto(
                nombre_producto=nombrep,
                imagen=imagen_nombre,
                cantidad=cantidadp,
                id_descripcion=iddescripcion.id_descripcion,
                id_categoria=categoriap,
                precio=preciop
            )

            db.session.add(nuevo_producto)
            db.session.commit()
            aviso="producto guardado exitosamente"
            return aviso
        
def actualizar(nombre,cantidad,descripcion,categoria,precio,imagen,id_producto):
    with app.app_context():
        try:
            producto = Producto.query.filter_by(id_producto=id_producto).first()
            descripcion1=Descripcion.query.filter_by(id_descripcion=producto.id_descripcion).first()
            if producto:
               filename = secure_filename(imagen.filename)
               ruta = os.path.join('static/productos', filename)
               if not os.path.exists(ruta):
                        imagen.save(ruta)
                        producto.imagen = filename

               producto.nombre_producto = nombre
               producto.cantidad = cantidad
               producto.id_categoria = categoria
               producto.precio = precio
               descripcion1.descripcion=descripcion
               db.session.commit()
               aviso="editado con exito"
               return aviso
        except Exception as e:
            aviso="error "
            return aviso



