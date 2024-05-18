import tkinter as tk
from tkinter import ttk
import mysql.connector
from cryptography.fernet import Fernet

# Clave para encriptar y desencriptar
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Función para encriptar datos
def encrypt_data(data):
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data.encode())
    return encrypted_data

# Función para desencriptar datos
def decrypt_data(encrypted_data):
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(encrypted_data).decode()
    return decrypted_data

# Función para añadir productos
def add_product():
    product_id = int(product_id_entry.get())
    product_name = encrypt_data(product_name_entry.get())
    # Resto de los datos...

    # Conexión a la base de datos
    connection = mysql.connector.connect(
        host="tu_host",
        user="tu_usuario",
        password="tu_contraseña",
        database="tu_base_de_datos"
    )
    cursor = connection.cursor()

    # Ejecutar consulta SQL para añadir producto
    query = "INSERT INTO Producto (ID, Nombre, Descripcion, Precio, StockActual) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (product_id, product_name, encrypted_description, encrypted_price, encrypted_stock))
    connection.commit()

    # Cerrar conexión
    cursor.close()
    connection.close()

# Función para añadir proveedor
def add_supplier():
    # Similar a la función add_product

# Función para añadir categoría
def add_category():
    # Similar a la función add_product

# Función para revisar inventario
def check_inventory():
    # Conexión a la base de datos
    connection = mysql.connector.connect(
        host="tu_host",
        user="tu_usuario",
        password="tu_contraseña",
        database="tu_base_de_datos"
    )
    cursor = connection.cursor()

    # Ejecutar consulta SQL para obtener inventario
    query = "SELECT * FROM Producto"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Mostrar inventario desencriptando los datos
    for row in rows:
        decrypted_name = decrypt_data(row[1])
        # Resto de los datos desencriptados...

        print(f"ID: {row[0]}, Nombre: {decrypted_name}, Descripcion: {decrypted_description}, Stock: {decrypted_stock}")

    # Cerrar conexión
    cursor.close()
    connection.close()

# Función para manejar la selección del menú principal
def menu_handler(option):
    if option == 1:
        add_product_window()
    elif option == 2:
        remove_product_window()
    elif option == 3:
        add_supplier_window()
    elif option == 4:
        add_category_window()
    elif option == 5:
        check_inventory()

# Función para crear la ventana principal
def main_window():
    window = tk.Tk()
    window.title("Gestor de Inventario")
    window.geometry("500x500")

    menu_label = tk.Label(window, text="Menú Principal", font=("Arial", 16))
    menu_label.pack(pady=20)

    options = ["Añadir Productos", "Retirar Productos", "Añadir Proveedor", "Añadir Categoría", "Revisar Inventario"]
    option_menu = ttk.Combobox(window, values=options)
    option_menu.pack(pady=10)

    submit_button = tk.Button(window, text="Seleccionar", command=lambda: menu_handler(option_menu.current() + 1))
    submit_button.pack(pady=20)

    window.mainloop()

# Función para crear la ventana de añadir productos
def add_product_window():
    add_product_window = tk.Toplevel()
    add_product_window.title("Añadir Producto")
    add_product_window.geometry("300x300")

    product_id_label = tk.Label(add_product_window, text="ID del Producto:")
    product_id_label.pack()

    product_id_entry = tk.Entry(add_product_window)
    product_id_entry.pack()

    product_name_label = tk.Label(add_product_window, text="Nombre del Producto:")
    product_name_label.pack()

    product_name_entry = tk.Entry(add_product_window)
    product_name_entry.pack()

    # Agregar más campos...

    submit_button = tk.Button(add_product_window, text="Añadir Producto", command=add_product)
    submit_button.pack()

# Función para crear la ventana de retirar productos
def remove_product_window():
    # Similar a la función add_product_window

# Función para crear la ventana de añadir proveedor
def add_supplier_window():
    # Similar a la función add_product_window

# Función para crear la ventana de añadir categoría
def add_category_window():
    # Similar a la función add_product_window

# Iniciar la aplicación
main_window()
