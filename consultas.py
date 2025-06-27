from app import app, db, Cliente, Ubicacion

def validar_login(email, password):
    with app.app_context():
        usuario = Cliente.query.filter_by(correo=email).first()

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