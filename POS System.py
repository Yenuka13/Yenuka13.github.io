from PyQt5 import QtWidgets, uic
import sys
import sqlite3

class POS(QtWidgets.QMainWindow):
    def __init__(self):
        super(POS, self).__init__()
        uic.loadUi("pos_ui.ui", self)  # Load UI file created in Qt Designer
        
        self.conn = sqlite3.connect("pos.db")
        self.cursor = self.conn.cursor()
        self.create_tables()
        
        self.add_to_cart_button.clicked.connect(self.add_to_cart)
        self.checkout_button.clicked.connect(self.checkout)
        self.load_products()
    
    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT, price REAL, stock INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                product_id INTEGER, quantity INTEGER, total_price REAL)''')
        self.conn.commit()
    
    def load_products(self):
        self.cursor.execute("SELECT * FROM products")
        products = self.cursor.fetchall()
        for product in products:
            self.product_list.addItem(f"{product[1]} - ${product[2]} (Stock: {product[3]})")
    
    def add_to_cart(self):
        selected_item = self.product_list.currentItem().text()
        product_name = selected_item.split(" - ")[0]
        self.cursor.execute("SELECT * FROM products WHERE name = ?", (product_name,))
        product = self.cursor.fetchone()
        if product:
            quantity = int(self.quantity_input.text())
            if quantity <= product[3]:
                total_price = product[2] * quantity
                self.cart_list.addItem(f"{product_name} x{quantity} - ${total_price}")
                self.cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product[0]))
                self.conn.commit()
                self.load_products()
            else:
                QtWidgets.QMessageBox.warning(self, "Stock Error", "Not enough stock available!")
    
    def checkout(self):
        total_amount = 0
        for index in range(self.cart_list.count()):
            item_text = self.cart_list.item(index).text()
            total_amount += float(item_text.split(" - $")[1])
        
        QtWidgets.QMessageBox.information(self, "Total Payment", f"Total Amount: ${total_amount}")
        self.cart_list.clear()
    
app = QtWidgets.QApplication(sys.argv)
window = POS()
window.show()
sys.exit(app.exec_())
