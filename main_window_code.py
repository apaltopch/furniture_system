from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QListWidget, QListWidgetItem
import MySQLdb as mdb
import sys
from main_form import Ui_MainForm
from add_pr_code import AddForm
from reg_code import EditForm



try:
    connect = mdb.connect('127.0.0.1', 'root', 'root', 'furniture_db')
    cur = connect.cursor()
except mdb.Error as e:
    QMessageBox.critical(None, 'Ошибка', f'Ошибка подключения к бд {e}')

class MainWindow(QMainWindow):
    def __init__(self, show_auth):
        super().__init__()
        self.ui = Ui_MainForm()
        self.ui.setupUi(self)

        self.show_auth = show_auth

        self.load_materials_cb()
        self.load_type_pr_cb()
        self.update_total_min()
        self.load_products()
        self.load_products_cb()

        self.ui.models_cb.currentIndexChanged.connect(self.filter)
        self.ui.type_pr_cb.currentIndexChanged.connect(self.filter)
        self.ui.exit_btn.clicked.connect(sys.exit)

        self.ui.products_cb.currentIndexChanged.connect(self.show_workshops)

        self.ui.addPr_btn.clicked.connect(self.open_add_win)
        self.ui.products_lw.itemClicked.connect(self.on_item_clicked)
        self.ui.next_page_btn.clicked.connect(self.next_page)
        self.ui.back_btn.clicked.connect(self.back)


    def next_page(self):
        self.ui.tabWidget.setCurrentIndex(1)

    def back(self):
        self.ui.tabWidget.setCurrentIndex(0)

    # выводим в комбо бокс данные для фильтрации
    def load_materials_cb(self):
        try:
            self.ui.models_cb.clear()
            self.ui.models_cb.addItem('Выберите материал', None)

            cur.execute("""select id_material, name from materials""")
            materials = cur.fetchall()

            for id, name in materials:
                self.ui.models_cb.addItem(name, id)

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка вывода моделей в combo box {e}')

    def load_type_pr_cb(self):
        try:
            self.ui.type_pr_cb.clear()
            self.ui.type_pr_cb.addItem('Выберите тип мебели', None)

            cur.execute("""select products_type.id_typePr, name from products_type""")
            products = cur.fetchall()

            for id, name in products:
                self.ui.type_pr_cb.addItem(name, id)

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка вывода типов в combo box {e}')


    # вывод каталога продукций
    def load_products(self):
        try:
            self.ui.products_lw.clear()

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
                    self.ui.products_lw.addItem(item)
            else:
                self.ui.products_lw.addItem('Отсутствует информация о продуктах')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка вывода продуктов {e}')

    # сортировка по материалам и типу продукции
    def filter(self):
        try:
           material_id = self.ui.models_cb.currentData() # получаем выбранные значения из комбо бокс
           type_id = self.ui.type_pr_cb.currentData()

           self.ui.products_lw.clear()
           query = """select products.id_product, products.name, products.min_price_partner, products.article, 
                            materials.name, products_type.name, products.total_min from products
                            join materials on products.id_material = materials.id_material
                            join products_type on products.id_typePr = products_type.id_typePr
                            where 1=1""" # техническое условие, чтобы удобнее было добавлять фильтры через and
           params = [] # список для значений фильтров

           if material_id is not None:
                query += " and products.id_material = %s"
                params.append(material_id)

           if type_id is not None:
               query += " and products.id_typePr = %s"
               params.append(type_id)

           cur.execute(query, tuple(params)) # tuple - кортеж из параметров

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
                self.ui.products_lw.addItem(item)
           else:
                self.ui.products_lw.addItem('Отсутствуют товары по выбранным параметрам')

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка вывода продуктов {e}')


    def update_total_min(self):
        try:
            cur.execute("""update products 
            set total_min = (select coalesce(sum(pw.production_time), 0) 
            from product_workshops pw
            where pw.product_id = products.id_product)""")

            connect.commit()
            self.load_products()

        except Exception as e:
            print(f"Ошибка при массовом обновлении времени: {e}")
            QMessageBox.critical(self, 'Ошибка', f'{e}')

    def open_add_win(self):
        self.add_win = AddForm(self)
        self.add_win.show()

    def get_selected_item(self, product_id):
        try:
            cur.execute("""select products.id_product, products.name, products.min_price_partner, 
                                products.article, products.description, 
                                products.id_material, products.id_model, products.id_typePr from products
                                where id_product = %s""", (product_id,))

            product = cur.fetchone()

            if not product:
                QMessageBox.information(self, 'Информация', 'Нет данных о продукте')
                return

            return {'id': product[0], 'name': product[1], 'min_price': product[2],
                    'article': product[3], 'descr': product[4], 'material': product[5],
                    'model': product[6], 'type': product[7]}
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка получения данных о продукте  \n {e}')

    def on_item_clicked(self, item):
        try:
            product_data = item.data(Qt.ItemDataRole.UserRole)
            selected_product = self.get_selected_item(product_data)

            if selected_product:
                self.edit_win = EditForm(self, selected_product)
                self.edit_win.show()

            else:
                QMessageBox.information(self, 'Нет данных', 'Нет данных')

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при нажатии \n {e}')
            print(e)


    def load_products_cb(self):
        try:
            self.ui.products_cb.clear()

            self.ui.products_cb.addItem('Выберите продукт', None)

            cur.execute("""select products.id_product, products.name from products""")
            products = cur.fetchall()

            for id, name in products:
                self.ui.products_cb.addItem(name, id)

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка вывода продуктов в кб {e}')


    def show_workshops(self):
        try:
            product_id = self.ui.products_cb.currentData()

            if product_id is None:
                self.ui.workshops_lw.clear()
                self.ui.workshops_lw.addItem('Выберите продукт для показа цехов')
                return

            cur.execute("""select products.id_product, products.name, products.article, workshops.name, workshops.workers_count, 
                            product_workshops.production_time from product_workshops
                            join products on product_workshops.product_id = products.id_product
                            join workshops on product_workshops.workshop_id = workshops.id_workshop 
                            where products.id_product = %s""", (product_id,))

            workshops = cur.fetchall()

            if workshops:
                for workshop in workshops:
                    id_pr, name, article, workshop, workers_count, production_time = workshop

                    item_text = (f"{name} | {article} \n"
                                 f"{workshop}: количество рабочих: {workers_count} \n"
                                 f"время изготовления в цехе: {production_time} \n ")

                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, id_pr)
                    self.ui.workshops_lw.addItem(item)

            else:
                self.ui.products_lw.addItem('Отсутствует информация о продуктах')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка вывода цехов {e}')


















