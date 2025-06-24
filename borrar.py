from app import app
from models import db, Cliente

with app.app_context():
    db.drop_all()
    print("Todas las tablas fueron eliminadas correctamente")