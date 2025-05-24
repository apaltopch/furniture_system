from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox
import MySQLdb as mdb
import sys
from auth import Ui_AuthForm



try:
    connect = mdb.connect('127.0.0.1', 'root', 'root', 'furniture_db')
    cur = connect.cursor()
except mdb.Error as e:
    QMessageBox.critical(None, 'Ошибка', f'Ошибка подключения к бд {e}')

class Auth(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.ui = Ui_AuthForm()
        self.ui.setupUi(self)

        self.main_window = main_window

        self.ui.pushButton.clicked.connect(self.auth)
        self.ui.pushButton_2.clicked.connect(self.reg)

    def auth(self):
        email = self.ui.login_line.text()
        password = self.ui.passw_line.text()

        # проверка на заполнение всех полей
        if not email or not password:
            QMessageBox.warning(self, 'Внимание', 'Заполните все поля!')
            return

        # поиск юзера в базе
        try:
            cur.execute("""select users.id_user, users.name from users
                        where users.email= %s and users.password_hash=%s""", (email, password))

            user = cur.fetchone()

            if user:
                QMessageBox.information(self, 'Успех', f'Добро пожаловать в систему {user[1]}')
                self.main_window()
            else:
                QMessageBox.information(self, 'Неверные данные', 'Неверный логин или пароль!\n Попробуйте еще раз.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка авторизации \n {e}')


    def reg(self):
        QMessageBox.information(self, 'ноу', 'не реализовано')














