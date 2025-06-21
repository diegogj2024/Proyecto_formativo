from flask import Flask, render_template,request
from models import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://root:Fu4wi8Zs7zFN10JhAqpWxLknDGZONvvJ@dpg-d19bsf7fte5s73c8q7p0-a.oregon-postgres.render.com/esmir'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


with app.app_context():
    db.create_all()
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html')

if __name__ == '__main__':
    app.run(debug=True)