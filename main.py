import sys
from PyQt6.QtWidgets import QApplication
from auth_code import Auth
from main_window_code import MainWindow


# класс для навигации в системе
class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.auth_win = None
        self.main_win = None
        self.show_auth()

    def show_auth(self):
        if self.auth_win:
            self.auth_win.close()

        if self.main_win:
            self.main_win.close()

        self.auth_win = Auth(main_window=self.show_main)
        self.auth_win.show()

    def show_main(self):
        self.main_win = MainWindow(show_auth=self.show_auth)
        self.main_win.show()

    def run(self):
        sys.exit(self.app.exec())


if __name__ == '__main__':
    app = App()
    app.run()
