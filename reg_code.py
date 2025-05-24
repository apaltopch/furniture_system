from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QListWidget, QListWidgetItem, QDialog
import MySQLdb as mdb
import sys
from edit import Ui_EditForm

try:
    connect = mdb.connect('127.0.0.1', 'root', 'root', 'furniture_db')
    cur = connect.cursor()
except mdb.Error as e:
    QMessageBox.critical(None, 'Ошибка', f'Ошибка подключения к бд {e}')


class EditForm(QDialog):
    def __init__(self, main_window, product_data):
        super().__init__()
        self.ui = Ui_EditForm()
        self.ui.setupUi(self)
        self.main_window = main_window

        self.product_data = product_data
        self.product_id = product_data['id']

        self.load_materials()
        self.load_models()
        self.load_types()

        self.ui.namePr_line.setText(product_data['name'])
        self.ui.partn_price_line.setText(str(product_data['min_price']))
        self.ui.article_line.setText(str(product_data['article']))
        self.ui.descr_line.setPlainText(product_data['descr'])

        index = self.ui.material_cb.findData(product_data['material'])
        if index >= 0:
            self.ui.material_cb.setCurrentIndex(index)

        index2 = self.ui.model_cb.findData(product_data['model'])
        if index2 >= 0:
            self.ui.model_cb.setCurrentIndex(index2)

        index3 = self.ui.typePr_cb.findData(product_data['type'])
        if index3 >= 0:
            self.ui.typePr_cb.setCurrentIndex(index3)

        self.ui.back_btn.clicked.connect(self.back)
        self.ui.edit_btn.clicked.connect(self.save_changes)

    def back(self):
        self.close()
        self.main_window.show()

    def save_changes(self):
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

            if not article.isdigit():
                QMessageBox.warning(self, 'Неверный тип данных', 'Введите число в поле артикул')
                return

            cur.execute("""update products set products.name = %s, products.min_price_partner = %s, 
                                        products.article = %s, products.description = %s, 
                                        products.id_material = %s, products.id_model = %s, products.id_typePr = %s 
                                        where products.id_product = %s""",
                                                                (name, min_price, article, descr,material, model, type, self.product_id))

            connect.commit()
            QMessageBox.information(self, 'Успех', 'Мебель успешно отредактирована')
            self.update_products()
            self.accept()


        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка редактирования бд \n {e}')


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
        cur.execute("""select id_material, name from materials""")
        materials = cur.fetchall()

        for id, name in materials:
            self.ui.material_cb.addItem(name, id)


    def load_types(self):
        cur.execute("""select id_typePr, name from products_type""")
        types = cur.fetchall()

        for id, name in types:
            self.ui.typePr_cb.addItem(name, id)


    def load_models(self):
        cur.execute("""select id_model, name from models""")
        models = cur.fetchall()

        for id, name in models:
            self.ui.model_cb.addItem(name, id)






