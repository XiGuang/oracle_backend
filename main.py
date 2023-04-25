from backend import app
from backend.initializaion.initialize_database import create_tables

if __name__ == '__main__':
    with app.app_context():
        create_tables()
        # app.run(host='127.0.0.1',port=5000,debug=True)