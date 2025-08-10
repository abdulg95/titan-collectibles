from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure PostgreSQL/MySQL database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname'

# Initialize the database
db = SQLAlchemy(app)

@app.route('/')
def hello():
    return "Hello, Digital Sports Cards Backend!"

if __name__ == '__main__':
    app.run(debug=True)
