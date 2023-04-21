DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'root'
PASSWORD = '1488'
HOST = 'localhost'
PORT = '13306'
DATABASE = 'python_flask'

SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8mb4".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST,
                                                                          PORT,
                                                                          DATABASE)
