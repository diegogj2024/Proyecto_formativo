from app import app, db, Cliente, Ubicacion

def validar_login(email, password):
    with app.app_context():
        usuario = Cliente.query.filter_by(correo=email).first()

    if usuario:
        if usuario.password == password:
            return True, usuario.nombre
        else:
            return False, "Contraseña incorrecta"
    else:
        return False, "Usuario no encontrado"