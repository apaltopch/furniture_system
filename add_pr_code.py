from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QListWidget, QListWidgetItem
import MySQLdb as mdb
import sys
from add import Ui_AddForn

try:
    connect = mdb.connect('127.0.0.1', 'root', 'root', 'furniture_db')
    cur = connect.cursor()
except mdb.Error as e:
    QMessageBox.critical(None, 'Ошибка', f'Ошибка подключения к бд {e}')

class AddForm(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.ui = Ui_AddForn()
        self.ui.setupUi(self)

        self.main_window =  main_window

        self.ui.back_btn.clicked.connect(self.back)
        self.ui.add_btn.clicked.connect(self.add_pr)
        self.load_materials()
        self.load_models()
        self.load_types()

    def add_pr(self):
        try:
            name = self.ui.namePr_line.text()
            min_price = self.ui.partn_price_line.text()
            article = self.ui.article_line.text()
            descr = self.ui.descr_line.toPlainText()
            model = self.ui.model_cb.currentData()
            type = self.ui.typePr_cb.currentData()
            material = self.ui.material_cb.currentData()

            if not all([name, min_price, article, descr]):
                QMessageBox.warning(self, 'Внимание', 'Заполните все поля')
                return

            if ([model, material, type]) is None:
                QMessageBox.warning(self, 'Внимание', 'Заполните все поля')
                return

            if not min_price.isdigit():
                QMessageBox.warning(self, 'Неверный тип данных', 'Введите число в поле цена')
                return

            if not article.isdigit():
                QMessageBox.warning(self, 'Неверный тип данных', 'Введите число в поле артикул')
                return

            cur.execute("""insert into products (products.name, products.min_price_partner, 
                            products.article, products.description, 
                            products.id_material, products.id_model, products.id_typePr) values 
                            (%s, %s, %s, %s, %s, %s, %s)""", (name, min_price, article, descr,
                                                              material, model, type))

            connect.commit()
            self.update_products()
            QMessageBox.information(self, 'Успех', 'Мебель успешно добавлена')
            self.main_window.show()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка добавления в бд \n {e}')

    def update_products(self):
        try:
            self.main_window.ui.products_lw.clear()

            cur.execute("""select products.id_product, products.name, products.min_price_partner, products.article, 
                            materials.name, products_type.name, products.total_min from products
                            join materials on products.id_material = materials.id_material
                            join products_type on products.id_typePr = products_type.id_typePr""")

            products = cur.fetchall()

            if products:
                for product in products:
                    id_pr, name, min_price, article, material, type, total_min = product

                    item_text = (f"{type} | {name}\n"
                                 f"{article}\n"
                                 f"{min_price}                                                                                          {total_min}\n"
                                 f"{material}\n")

                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, id_pr)
                    self.main_window.ui.products_lw.addItem(item)
            else:
                self.main_window.ui.products_lw.addItem('Отсутствует информация о продуктах')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка вывода продуктов {e}')


    def load_materials(self):
        try:
            self.ui.material_cb.clear()
            self.ui.material_cb.addItem('Выберите материал', None)

            cur.execute("""select id_material, name from materials""")
            materials = cur.fetchall()

            for id, name in materials:
                self.ui.material_cb.addItem(name, id)

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка вывода материалов в combo box {e}')


    def load_types(self):
        try:
            self.ui.typePr_cb.clear()
            self.ui.typePr_cb.addItem('Выберите тип мебели', None)

            cur.execute("""select id_typePr, name from products_type""")
            types = cur.fetchall()

            for id, name in types:
                self.ui.typePr_cb.addItem(name, id)

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка вывода типов в combo box {e}')

    def load_models(self):
        try:
            self.ui.model_cb.clear()
            self.ui.model_cb.addItem('Выберите модель', None)

            cur.execute("""select id_model, name from models""")
            models = cur.fetchall()

            for id, name in models:
                self.ui.model_cb.addItem(name, id)

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка вывода моделей в combo box {e}')


    def back(self):
        self.main_window.show()
        self.close()





