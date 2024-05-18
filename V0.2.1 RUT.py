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

# Variable para almacenar el nombre del usuario
current_user_name = ""

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
def menu_handler(option, user_label, menu_window):
    if option == 1:
        add_product_window()
    elif option == 2:
        check_inventory()
    elif option == 3:
        create_user_window()  # Nueva opción: Crear Usuario
    elif option == 4:
        close_session(user_label, menu_window)

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
def login_handler(window, user_label, rut_entry, password_entry):
    global current_user_name  # Usamos la variable global para almacenar el nombre del usuario
    rut = rut_entry.get()
    password = password_entry.get()
    result = verify_rut(rut)

    if "-" in result:
        # Verificar el RUT en la base de datos
        if check_credentials_in_database(result, password):
            current_user_name = get_user_name(result)  # Almacenar el nombre del usuario globalmente
            user_label.config(text=f"Bienvenido, {current_user_name}")
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

        # Ejecutar consulta SQL para verificar las credenciales
        query = "SELECT * FROM usuario WHERE rut = %s AND password = %s"
        cursor.execute(query, (rut, password))
        user_data = cursor.fetchone()

        # Cerrar conexión
        cursor.close()
        connection.close()

        return user_data is not None  # Si se encuentra el usuario, las credenciales son válidas

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al verificar las credenciales en la base de datos: {err}")
        return False

# Función para obtener el nombre del usuario desde la base de datos
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

        # Ejecutar consulta SQL para obtener el nombre del usuario
        query = "SELECT nombre FROM usuario WHERE rut = %s"
        cursor.execute(query, (rut,))
        user_name = cursor.fetchone()[0]

        # Cerrar conexión
        cursor.close()
        connection.close()

        return user_name

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al obtener el nombre del usuario desde la base de datos: {err}")
        return ""

# Función para cerrar la sesión
def close_session(user_label, menu_window):
    global current_user_name  # Restablecer la variable global del nombre del usuario
    current_user_name = ""
    user_label.config(text="")
    menu_window.destroy()  # Cerrar la ventana del menú principal
    main_window()  # Abrir la ventana de inicio de sesión nuevamente

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

# Función para crear la ventana de crear usuario
def create_user_window():
    create_user_window = tk.Toplevel()
    create_user_window.title("Crear Usuario")
    create_user_window.geometry("300x300")

    rut_label = tk.Label(create_user_window, text="RUT (1-8 dígitos):")
    rut_label.pack()

    rut_entry = tk.Entry(create_user_window)
    rut_entry.pack()

    name_label = tk.Label(create_user_window, text="Nombre:")
    name_label.pack()

    name_entry = tk.Entry(create_user_window)
    name_entry.pack()

    password_label = tk.Label(create_user_window, text="Contraseña:")
    password_label.pack()

    password_entry = tk.Entry(create_user_window, show="*")
    password_entry.pack()

    user_type_label = tk.Label(create_user_window, text="Tipo de Usuario:")
    user_type_label.pack()

    user_type_var = tk.StringVar(create_user_window)
    user_type_var.set("admin")  # Valor predeterminado
    user_type_options = ["admin", "lector"]
    user_type_menu = tk.OptionMenu(create_user_window, user_type_var, *user_type_options)
    user_type_menu.pack()

    submit_button = tk.Button(create_user_window, text="Crear Usuario", command=lambda: create_user(
        rut_entry.get(),
        name_entry.get(),
        password_entry.get(),
        user_type_var.get()
    ))
    submit_button.pack()

# Función para crear un usuario
def create_user(rut, name, password, user_type):
    try:
        # Verificar el RUT usando la función verify_rut
        verified_rut = verify_rut(rut)

        if "-" in verified_rut:
            # Conexión a la base de datos
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="pruebas_inventario"
            )
            cursor = connection.cursor()

            # Verificar si el usuario ya existe en la base de datos
            query_check_user = "SELECT * FROM usuario WHERE rut = %s"
            cursor.execute(query_check_user, (verified_rut,))
            existing_user = cursor.fetchone()

            if existing_user:
                messagebox.showerror("Error", "El usuario ya existe en la base de datos")
            else:
                # Agregar nuevo usuario a la tabla
                query_add_user = "INSERT INTO usuario (rut, password, permisos, nombre) VALUES (%s, %s, %s, %s)"
                cursor.execute(query_add_user, (verified_rut, password, user_type, name))
                connection.commit()

                messagebox.showinfo("Éxito", "Usuario creado exitosamente")

            # Cerrar conexión
            cursor.close()
            connection.close()

        else:
            messagebox.showerror("Error", verified_rut)

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al crear el usuario: {err}")

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al crear el usuario: {err}")

# Función para crear la ventana del menú principal
def menu_window():
    menu_window = tk.Tk()
    menu_window.title("Menú Principal")
    menu_window.geometry("500x500")

    user_label = tk.Label(menu_window, text=f"Bienvenido, {current_user_name}", anchor="e")
    user_label.pack(pady=5, padx=5)

    # Crear botones para las opciones del menú
    options = ["Añadir Productos", "Revisar Inventario", "Crear Usuario", "Cerrar Sesión"]
    for i, option in enumerate(options, start=1):
        button = tk.Button(menu_window, text=option, command=lambda i=i: menu_handler(i, user_label, menu_window))
        button.pack(pady=10)

    menu_window.mainloop()

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

    user_label = tk.Label(window, text="", anchor="e")
    user_label.pack(pady=5, padx=5)

    login_button = tk.Button(window, text="Iniciar Sesión", command=lambda: login_handler(window, user_label, rut_entry, password_entry))
    login_button.pack(pady=10)

    window.mainloop()

# Iniciar la aplicación
main_window()
