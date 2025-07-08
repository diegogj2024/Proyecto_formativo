from app import app, db,DetalleCarrito,Carrito,Factura,Compra,Inventario,Producto,producto_categoria,Categoria,Talla,Cliente,Ubicacion,Empresa

with app.app_context():
     with db.engine.connect() as conn:
        conn.execute(db.text('DROP TABLE IF EXISTS factura CASCADE'))
        conn.execute(db.text('DROP TABLE IF EXISTS compra CASCADE'))
        conn.execute(db.text('DROP TABLE IF EXISTS inventario CASCADE'))
        conn.execute(db.text('DROP TABLE IF EXISTS detallecarrito CASCADE'))
        conn.execute(db.text('DROP TABLE IF EXISTS carrito CASCADE'))
        conn.execute(db.text('DROP TABLE IF EXISTS producto_categoria CASCADE'))
        conn.execute(db.text('DROP TABLE IF EXISTS producto CASCADE'))
        conn.execute(db.text('DROP TABLE IF EXISTS categoria CASCADE'))
        conn.execute(db.text('DROP TABLE IF EXISTS talla CASCADE'))
        conn.execute(db.text('DROP TABLE IF EXISTS cliente CASCADE'))
        conn.execute(db.text('DROP TABLE IF EXISTS ubicacion CASCADE'))
        conn.execute(db.text('DROP TABLE IF EXISTS empresa CASCADE'))
        print("Todas las tablas fueron eliminadas correctamente.")
