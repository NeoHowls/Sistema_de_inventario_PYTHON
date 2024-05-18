import tkinter as tk
import tkinter.ttk as ttk


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
def add_product(product_id, product_name, description, stock):
    try:
        # Conexión a la base de datos
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="pruebas_inventario"
        )
        cursor = connection.cursor()

        # Convertir el nombre del producto y la descripción a minúsculas
        product_name_lower = product_name.lower()
        description_lower = description.lower()

        # Convertir el ID a varchar y encriptar
        encrypted_id = encrypt_data(str(product_id))

        # Desencriptar el ID para la verificación
        decrypted_id_check = decrypt_data(encrypted_id)

        # Verificar si el ID ya está en la base de datos
        query_check_id = "SELECT ID FROM Producto"
        cursor.execute(query_check_id)
        existing_ids = cursor.fetchall()

        # Desencriptar los IDs existentes y comparar
        decrypted_existing_ids = [decrypt_data(existing_id[0]) for existing_id in existing_ids]

        if decrypted_id_check in decrypted_existing_ids:
            messagebox.showerror("Error", "El ID ya está ingresado en la base de datos")
        else:
            # Ejecutar consulta SQL para añadir producto con el nombre y la descripción en minúsculas
            query_add_product = "INSERT INTO Producto (ID, Nombre, Descripcion, StockActual) VALUES (%s, %s, %s, %s)"
            cursor.execute(query_add_product, (encrypted_id, product_name_lower, description_lower, stock))
            connection.commit()

            messagebox.showinfo("Éxito", "Producto añadido exitosamente")

        # Cerrar conexión
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al añadir el producto: {err}")

# Función para desencriptar el ID de la base de datos
def decrypt_database_id():
    try:
        # Conexión a la base de datos
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="pruebas_inventario"
        )
        cursor = connection.cursor()

        # Obtener todos los IDs encriptados de la base de datos
        query_get_encrypted_ids = "SELECT ID FROM Producto"
        cursor.execute(query_get_encrypted_ids)
        encrypted_ids = cursor.fetchall()

        # Desencriptar y mostrar los IDs
        decrypted_ids = [decrypt_data(encrypted_id[0]) for encrypted_id in encrypted_ids]
        print("IDs desencriptados:", decrypted_ids)

        # Cerrar conexión
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error al desencriptar los IDs de la base de datos: {err}")

# Llamada a la función para desencriptar los IDs de la base de datos
decrypt_database_id()

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

        # Construir la consulta SQL para obtener todo el inventario
        query = "SELECT * FROM Producto"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Crear una ventana para buscar y mostrar información del inventario
        inventory_window = tk.Toplevel()
        inventory_window.title("Inventario")
        inventory_window.geometry("500x300")

        # Etiquetas y entradas para el nombre y la descripción (Búsqueda)
        name_label = tk.Label(inventory_window, text="Nombre del Producto:")
        name_label.pack()

        name_entry = tk.Entry(inventory_window)
        name_entry.pack()

        description_label = tk.Label(inventory_window, text="Descripción del Producto:")
        description_label.pack()

        description_entry = tk.Entry(inventory_window)
        description_entry.pack()

        # Función para mostrar inventario desencriptando solo el ID
        def show_inventory(search_name="", search_description=""):
            try:
                nonlocal rows, cursor  # Acceder a las variables externas 'rows' y 'cursor'

                # Limpiar el contenido previo en la ventana de inventario
                for widget in inventory_window.winfo_children():
                    widget.destroy()

                # Etiqueta para mostrar resultados de búsqueda
                search_result_label = tk.Label(inventory_window, text=f"Resultados para {search_name} {search_description}")
                search_result_label.pack(pady=10)

                # Etiquetas y entradas para el nombre y la descripción (Búsqueda)
                name_label = tk.Label(inventory_window, text="Nombre del Producto:")
                name_label.pack()

                name_entry = tk.Entry(inventory_window)
                name_entry.pack()

                description_label = tk.Label(inventory_window, text="Descripción del Producto:")
                description_label.pack()

                description_entry = tk.Entry(inventory_window)
                description_entry.pack()

                # Botón para realizar la búsqueda
                search_button = tk.Button(
                    inventory_window, 
                    text="Buscar", 
                    command=lambda: show_inventory(name_entry.get(), description_entry.get())
                )
                search_button.pack()

                # Construir la consulta SQL para obtener inventario con filtros de búsqueda
                if search_name and search_description:
                    query = "SELECT * FROM Producto WHERE Nombre LIKE %s AND Descripcion LIKE %s"
                    cursor.execute(query, (f"%{search_name}%", f"%{search_description}%"))
                elif search_name:
                    query = "SELECT * FROM Producto WHERE Nombre LIKE %s"
                    cursor.execute(query, (f"%{search_name}%",))
                elif search_description:
                    query = "SELECT * FROM Producto WHERE Descripcion LIKE %s"
                    cursor.execute(query, (f"%{search_description}%",))
                else:
                    query = "SELECT * FROM Producto"
                    cursor.execute(query)

                rows = cursor.fetchall()

                # Verificar si se encontraron productos
                if not rows:
                    not_found_label = tk.Label(inventory_window, text="Producto no encontrado")
                    not_found_label.pack(pady=10)
                else:
                    # Crear el Treeview para mostrar la información como una tabla
                    columns = ("ID (Desencriptado)", "Nombre", "Descripción", "Stock")
                    tree = ttk.Treeview(inventory_window, columns=columns, show="headings")

                    # Configurar encabezados de columna
                    for col in columns:
                        tree.heading(col, text=col)
                        tree.column(col, width=100)

                    # Insertar datos en el Treeview
                    for row in rows:
                        decrypted_id = decrypt_data(row[0])
                        tree.insert("", "end", values=(decrypted_id, row[1], row[2], row[3]))
                        
                        # Imprimir el ID encriptado por consola
                        print(f"ID encriptado: {row[0]}")

                    # Mostrar el Treeview
                    tree.pack(pady=10)

            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error al revisar el inventario: {err}")


        # Llamar a la función para mostrar el inventario inicialmente
        show_inventory()

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al revisar el inventario: {err}")

    finally:
        # Cerrar conexión y cursor al cerrar la ventana de inventario
        def close_inventory_window():
            inventory_window.destroy()
            cursor.close()
            connection.close()

        inventory_window.protocol("WM_DELETE_WINDOW", close_inventory_window)
#---------------


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

    def validate_numeric_input(char):
        # Función de validación para permitir solo caracteres numéricos
        return char.isdigit() or char == ""

    product_id_label = tk.Label(add_product_window, text="ID del Producto:")
    product_id_label.pack()

    # Utilizar la validación de entrada para permitir solo valores numéricos
    vcmd = (add_product_window.register(validate_numeric_input), '%S')
    product_id_entry = tk.Entry(add_product_window, validate="key", validatecommand=vcmd)
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

    # Utilizar la validación de entrada para permitir solo valores numéricos en stock_actual
    stock_vcmd = (add_product_window.register(validate_numeric_input), '%S')
    stock_entry = tk.Entry(add_product_window, validate="key", validatecommand=stock_vcmd)
    stock_entry.pack()

    submit_button = tk.Button(add_product_window, text="Añadir Producto", command=lambda: add_product(
        product_id_entry.get(),
        product_name_entry.get(),
        description_entry.get(),
        stock_entry.get()
    ))
    submit_button.pack()

# Función para desencriptar el ID específico de la base de datos
def decrypt_specific_id(product_id):
    try:
        # Conexión a la base de datos
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="pruebas_inventario"
        )
        cursor = connection.cursor()

        # Obtener el ID encriptado específico de la base de datos
        query_get_encrypted_id = "SELECT ID FROM Producto WHERE ID = %s"
        cursor.execute(query_get_encrypted_id, (encrypt_data(str(product_id)),))
        encrypted_id = cursor.fetchone()

        if encrypted_id:
            encrypted_id = encrypted_id[0]

            # Desencriptar y mostrar el ID
            decrypted_id = decrypt_data(encrypted_id)
            print(f"ID encriptado: {encrypted_id}")
            print(f"ID desencriptado: {decrypted_id}")
        else:
            print(f"No se encontró ningún producto con el ID: {product_id}")

        # Cerrar conexión
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error al desencriptar el ID de la base de datos: {err}")

# Llamada a la función para desencriptar un ID específico (por ejemplo, ID 1)
decrypt_specific_id("1")





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
        # Verificar que ningún campo esté vacío
        if not rut or not name or not password or not user_type:
            messagebox.showerror("Error", "No puede dejar campos vacíos")
            return

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
    window.geometry("400x300")

    login_label = tk.Label(window, text="Ingrese su RUT (1-8 dígitos) sin guion ni con el numero verificador:")
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
