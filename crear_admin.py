from app import app, db, Talla

with app.app_context():
    try:
        
        
        nueva_talla=Talla(
        nombre_talla="L"  
        )

        db.session.add(nueva_talla)
        db.session.commit()
        print("empresa creado correctamente.")

    except Exception as e:
        db.session.rollback()
        print(f"Ocurrió un error: {e}")
