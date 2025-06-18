from flask import Flask, render_template,request
from models import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://root:Fu4wi8Zs7zFN10JhAqpWxLknDGZONvvJ@localhost:5432/esmir'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


with app.app_context():
    db.create_all()
    
@app.route('/')
def index():
    return render_template('index.html')




if __name__ == '__main__':
    app.run(debug=True)