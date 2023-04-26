from backend import app
from backend.initializaion.initialize_database import modify_word_table

if __name__ == '__main__':
    with app.app_context():
        modify_word_table()
        # app.run(host='127.0.0.1',port=5000,debug=True)