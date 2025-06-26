from app import app, db, Cliente, Ubicacion

with app.app_context():
    try:
        direccion = "Calle 123"

        ubicacion_existente = Ubicacion.query.filter_by(direccion=direccion).first()

        if not ubicacion_existente:
            nueva_ubicacion = Ubicacion(direccion=direccion)
            db.session.add(nueva_ubicacion)
            db.session.commit()
            print("Dirección creada.")
        else:
            print("La dirección ya existe.")
            nuevo_cliente =Cliente(
            cedula=1030040622,
            nombre="Diego",
            apellido="Garcia",
            correo="diegogarcia0809@outlook.com",
            telefono="3176636963",
            password="12345",
            direccion=direccion
        )

        db.session.add(nuevo_cliente)
        db.session.commit()
        print("Cliente creado correctamente.")

    except Exception as e:
        db.session.rollback()
        print(f"Ocurrió un error: {e}")
