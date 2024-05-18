import tkinter as tk
from tkinter import messagebox
import mysql.connector
from cryptography.fernet import Fernet
import base64
from itertools import cycle
# Cadena secreta como clave (32 bytes)
secret_key = b'123456789'

# Asegurar que la clave tenga exactamente 32 bytes
while len(secret_key) < 32:
    secret_key += secret_key

# Tomar solo los primeros 32 bytes
secret_key = secret_key[:32]

# Codificar la clave en base64
key = base64.urlsafe_b64encode(secret_key)

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
def add_product(product_id, product_name, encrypted_description, stock):
    try:
        # Conexión a la base de datos
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="pruebas_inventario"
        )
        cursor = connection.cursor()

        # Ejecutar consulta SQL para añadir producto
        query = "INSERT INTO Producto (ID, Nombre, Descripcion, StockActual) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (product_id, product_name, encrypted_description, stock))
        connection.commit()

        # Cerrar conexión
        cursor.close()
        connection.close()

        messagebox.showinfo("Éxito", "Producto añadido exitosamente")

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al añadir el producto: {err}")

# Función para revisar inventario
def check_inventory():
    try:
        # Conexión a la base de datos
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="pruebas_inventario"
        )
        cursor = connection.cursor()

        # Ejecutar consulta SQL para obtener inventario
        query = "SELECT * FROM Producto"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Crear una ventana para mostrar la información del inventario
        inventory_window = tk.Toplevel()
        inventory_window.title("Inventario")
        inventory_window.geometry("500x300")

        # Mostrar inventario desencriptando los datos
        for i, row in enumerate(rows, start=1):
            decrypted_name = decrypt_data(row[1])
            decrypted_description = decrypt_data(row[2])

            inventory_label = tk.Label(inventory_window, text=f"ID: {row[0]}, Nombre: {decrypted_name}, Descripcion: {decrypted_description}, Stock: {row[3]}")
            inventory_label.pack(pady=5)

        # Cerrar conexión
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al revisar el inventario: {err}")

# Función para manejar la selección del menú principal
def menu_handler(option):
    if option == 1:
        add_product_window()
    elif option == 2:
        check_inventory()

# Función para calcular el dígito verificador de un RUT
def digito_verificador(rut):
    reversed_digits = map(int, reversed(str(rut)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    return (-s) % 11
# Función para verificar el RUT
def verify_rut(rut):
    try:
        rut = int(rut)
        if not (1 <= len(str(rut)) <= 8):
            raise ValueError("El RUT debe tener entre 1 y 8 caracteres")
        digito_verif = digito_verificador(rut)

        # Mostrar 'K' en lugar de '10' cuando el dígito verificador es 10
        if digito_verif == 10:
            result = f"{rut}-K"
        else:
            result = f"{rut}-{digito_verif}"

        # Mostrar el resultado por consola
        print(f"Verificación del RUT: {result}")
        return result

    except ValueError as e:
        return f"Error: {e}"

# Función para manejar el inicio de sesión
def login_handler(window, rut_entry, password_entry):
    rut = rut_entry.get()
    password = password_entry.get()
    result = verify_rut(rut)

    if "-" in result:
        # Verificar el RUT en la base de datos
        if check_credentials_in_database(result, password):
            messagebox.showinfo("Inicio de Sesión Exitoso", f"Tu RUT está en la base de datos, hola {get_user_name(result)}")
            window.destroy()  # Cerrar la ventana de inicio de sesión
            menu_window()  # Abrir la ventana del menú principal
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")
    else:
        messagebox.showerror("Error", result)

# Función para verificar las credenciales en la base de datos
def check_credentials_in_database(rut, password):
    try:
        # Conexión a la base de datos
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="pruebas_inventario"
        )
        cursor = connection.cursor()

        # Consultar la base de datos para verificar las credenciales
        query = "SELECT * FROM usuario WHERE rut = %s AND password = %s"
        cursor.execute(query, (rut, password))
        user_data = cursor.fetchone()

        # Cerrar conexión
        cursor.close()
        connection.close()

        return user_data is not None

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error en la base de datos: {err}")
        return False

# Función para obtener el nombre del usuario en la base de datos
def get_user_name(rut):
    try:
        # Conexión a la base de datos
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="pruebas_inventario"
        )
        cursor = connection.cursor()

        # Consultar la base de datos para obtener el nombre del usuario
        query = "SELECT nombre FROM usuario WHERE rut = %s"
        cursor.execute(query, (rut,))
        user_name = cursor.fetchone()[0]

        # Cerrar conexión
        cursor.close()
        connection.close()

        return user_name

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error en la base de datos: {err}")
        return "Desconocido"

# Función para crear la ventana principal
def main_window():
    window = tk.Tk()
    window.title("Gestor de Inventario - Inicio de Sesión")
    window.geometry("300x200")

    login_label = tk.Label(window, text="Ingrese su RUT (1-8 dígitos):")
    login_label.pack(pady=10)

    rut_entry = tk.Entry(window)
    rut_entry.pack(pady=10)

    password_label = tk.Label(window, text="Ingrese su Contraseña:")
    password_label.pack(pady=10)

    password_entry = tk.Entry(window, show="*")
    password_entry.pack(pady=10)

    login_button = tk.Button(window, text="Iniciar Sesión", command=lambda: login_handler(window, rut_entry, password_entry))
    login_button.pack(pady=10)

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

    description_label = tk.Label(add_product_window, text="Descripción:")
    description_label.pack()

    description_entry = tk.Entry(add_product_window)
    description_entry.pack()

    stock_label = tk.Label(add_product_window, text="Stock Actual:")
    stock_label.pack()

    stock_entry = tk.Entry(add_product_window)
    stock_entry.pack()

    submit_button = tk.Button(add_product_window, text="Añadir Producto", command=lambda: add_product(
        product_id_entry.get(),
        encrypt_data(product_name_entry.get()),
        encrypt_data(description_entry.get()),
        stock_entry.get()
    ))
    submit_button.pack()

# Función para crear la ventana del menú principal
def menu_window():
    menu_window = tk.Tk()
    menu_window.title("Menú Principal")
    menu_window.geometry("500x500")

    menu_label = tk.Label(menu_window, text="Menú Principal", font=("Arial", 16))
    menu_label.pack(pady=20)

    # Crear botones para las opciones del menú
    options = ["Añadir Productos", "Revisar Inventario"]
    for i, option in enumerate(options, start=1):
        button = tk.Button(menu_window, text=option, command=lambda i=i: menu_handler(i))
        button.pack(pady=10)

    menu_window.mainloop()

# Iniciar la aplicación
main_window()
