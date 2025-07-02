from app import app, db, Categoria

with app.app_context():
    try:
        
        
        nueva_empresa =Categoria(
        id_categoria=2,
        nombre_categoria="niños",
        )

        db.session.add(nueva_empresa)
        db.session.commit()
        print("empresa creado correctamente.")

    except Exception as e:
        db.session.rollback()
        print(f"Ocurrió un error: {e}")
