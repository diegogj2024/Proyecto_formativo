from app import app, db, Cliente, Ubicacion,mail,Message
import secrets

def validar_login(email, password):
    with app.app_context():
        usuario = Cliente.query.filter_by(correo=email).first()
        ver=usuario.password

    if usuario:
        if usuario.password == password:
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
