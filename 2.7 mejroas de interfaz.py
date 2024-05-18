import tkinter as tk
import tkinter.ttk as ttk
from ttkthemes import ThemedStyle  
from tkcalendar import DateEntry
from datetime import date
import re 
import sv_ttk
from tkinter import messagebox
import mysql.connector
from cryptography.fernet import Fernet
import base64
from itertools import cycle
from ttkthemes import ThemedTk, THEMES
from ttkwidgets import ScaleEntry
from ttkwidgets.autocomplete import AutocompleteCombobox
from PIL import Image
from tkinter import PhotoImage


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
get_user_permissions = " "
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
        if not product_id or not product_name or not description or not stock:
            messagebox.showerror("Error", "No puede dejar campos vacíos")
            return
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
        # Manejar el error específico relacionado con el tipo de dato incorrecto para 'StockActual'
        if err.errno == 1366:
            messagebox.showerror("Error", "Error al añadir el producto: Favor ingrese un valor válido para el Stock")
        else:
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

# Funcion parar revisar inventario 2.0
def check_inventory_content(content_frame):
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


        # Etiquetas y entradas para el nombre y la descripción (Búsqueda)
        name_label = tk.Label(content_frame, text="Nombre del Producto:"  ,font=("Roboto Cn",16))
        name_label.pack()

        name_entry = tk.Entry(content_frame)
        name_entry.pack()

        description_label = tk.Label(content_frame, text="Descripción del Producto:")
        description_label.pack()

        description_entry = tk.Entry(content_frame)
        description_entry.pack()

        # Función para abrir un mensaje con el ID encriptado
        def show_encrypted_id_message(encrypted_id):
            messagebox.showinfo("ID Encriptado", f"El producto tiene el ID encriptado: {encrypted_id}")


        # Función para mostrar inventario desencriptando tanto el ID como los otros datos
        def show_inventory(search_name="", search_description=""):
            try:
                nonlocal rows, cursor  # Acceder a las variables externas 'rows' y 'cursor'

                # Limpiar el contenido previo en la ventana de inventario
                for widget in content_frame.winfo_children():
                    widget.destroy()

                # Etiqueta para mostrar resultados de búsqueda
                search_result_label = tk.Label(content_frame, text=f"Resultados para {search_name} {search_description}"  ,font=("Roboto Cn",16))
                search_result_label.pack(pady=10)

                # Etiquetas y entradas para el nombre y la descripción (Búsqueda)
                name_label = tk.Label(content_frame, text="Nombre del Producto:",font=("Roboto Cn",16))
                name_label.pack()

                name_entry = tk.Entry(content_frame,font=("Roboto Cn",18))
                name_entry.pack()

                description_label = tk.Label(content_frame, text="Descripción del Producto:",font=("Roboto Cn",16))
                description_label.pack()

                description_entry = tk.Entry(content_frame,font=("Roboto Cn",18))
                description_entry.pack()

                # Botón para realizar la búsqueda
                search_button = tk.Button(
                    content_frame, 
                    text="Buscar", 
                    command=lambda: show_inventory(name_entry.get(), description_entry.get())
                    ,font=("Roboto Cn",18)
                    , bg="#4DA900"
                    , fg="white"
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
                    not_found_label = tk.Label(content_frame, text="Producto no encontrado", font=("Roboto Cn",16) )
                    not_found_label.pack(pady=10)
                else:
                    # Crear el Treeview para mostrar la información como una tabla
                    columns = ("ID (Encriptado)", "ID (Desencriptado)", "Nombre", "Descripción", "Stock")
                    tree = ttk.Treeview(content_frame, columns=columns, show="headings")

                    # Configurar encabezados de columna
                    for col in columns:
                        tree.heading(col, text=col)
                        tree.column(col, width=100)

                    # Insertar datos en el Treeview
                    for row in rows:
                        encrypted_id = row[0]
                        decrypted_id = decrypt_data(encrypted_id)
                        tree.insert("", "end", values=(encrypted_id, decrypted_id, row[1], row[2], row[3]), tags=(decrypted_id,))

                        # Configurar evento de clic para mostrar el mensaje
                        if current_user_permissions == "admin":
                            tree.tag_bind(decrypted_id, '<ButtonRelease-1>', lambda event, encrypted_id=encrypted_id: admin_menu(encrypted_id))
                        else:
                            messagebox.showerror("Error", "Error, solo administradores pueden usar esta función")
                        

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
            content_frame.destroy()
            cursor.close()
            connection.close()

        content_frame.protocol("WM_DELETE_WINDOW", close_inventory_window)

def check_inventory_handler(content_frame):
    # Limpiar el contenido existente en el frame
    for widget in content_frame.winfo_children():
        widget.destroy()

    check_inventory_content(content_frame)


def check_inventory_eliminado(content_frame):
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



        # Función para abrir un mensaje con el ID encriptado
        def show_encrypted_id_message(encrypted_id):
            messagebox.showinfo("ID Encriptado", f"El producto tiene el ID encriptado: {encrypted_id}")


        # Función para mostrar inventario desencriptando tanto el ID como los otros datos
        def show_inventory(search_name="", search_description="", search_date=""):
            try:
                nonlocal rows, cursor  # Acceder a las variables externas 'rows' y 'cursor'

                # Limpiar el contenido previo en la ventana de inventario
                for widget in content_frame.winfo_children():
                    widget.destroy()

                # Etiqueta para mostrar resultados de búsqueda
                search_result_label = tk.Label(content_frame, text=f"Resultados para {search_name} {search_description}",font=("Roboto Cn",16))
                search_result_label.pack(pady=10)

                # Etiquetas y entradas para el nombre y la descripción (Búsqueda)
                name_label = tk.Label(content_frame, text="Nombre del Producto:", font=("Roboto Cn",16))
                name_label.pack()

                name_entry = tk.Entry(content_frame, font=("Roboto Cn",18))
                name_entry.pack()

                description_label = tk.Label(content_frame, text="Descripción del Producto:", font=("Roboto Cn",16))
                description_label.pack()

                description_entry = tk.Entry(content_frame, font=("Roboto Cn",18))
                description_entry.pack()

                date_label = tk.Label(content_frame, text="Fecha:", font=("Roboto Cn",16))
                date_label.pack()

                date_entry = DateEntry(content_frame, date_pattern='yyyy-mm-dd', font=("Roboto Cn",18))
                date_entry.pack()


                # Botón para realizar la búsqueda
                search_button = tk.Button(
                    content_frame, 
                    text="Buscar", 
                    command=lambda: show_inventory(name_entry.get(), description_entry.get(),date_entry.get())
                    ,font=("Roboto Cn",18)
                    , bg="#4DA900"
                    , fg="white"
                )
                search_button.pack()

                # Construir la consulta SQL para obtener inventario con filtros de búsqueda
                if search_name and search_description and search_date:
                    query = "SELECT * FROM producto_respaldo WHERE Nombre LIKE %s AND Descripcion LIKE %s AND fecha_eliminacion = %s"
                    cursor.execute(query, (f"%{search_name}%", f"%{search_description}%", search_date))
                elif search_name and search_description:
                    query = "SELECT * FROM producto_respaldo WHERE Nombre LIKE %s AND Descripcion LIKE %s"
                    cursor.execute(query, (f"%{search_name}%", f"%{search_description}%"))
                elif search_name and search_date:
                    query = "SELECT * FROM producto_respaldo WHERE Nombre LIKE %s AND fecha_eliminacion = %s"
                    cursor.execute(query, (f"%{search_name}%", search_date))
                elif search_description and search_date:
                    query = "SELECT * FROM producto_respaldo WHERE Descripcion LIKE %s AND fecha_eliminacion = %s"
                    cursor.execute(query, (f"%{search_description}%", search_date))
                elif search_name:
                    query = "SELECT * FROM producto_respaldo WHERE Nombre LIKE %s"
                    cursor.execute(query, (f"%{search_name}%",))
                elif search_description:
                    query = "SELECT * FROM producto_respaldo WHERE Descripcion LIKE %s"
                    cursor.execute(query, (f"%{search_description}%",))
                elif search_date:
                    query = "SELECT * FROM producto_respaldo WHERE fecha_eliminacion = %s"
                    cursor.execute(query, (search_date,))
                else:
                    query = "SELECT * FROM producto_respaldo"
                    cursor.execute(query)

                rows = cursor.fetchall()

                # Verificar si se encontraron productos
                if not rows:
                    not_found_label = tk.Label(content_frame, text="Producto no encontrado", font=("Roboto Cn",16))
                    not_found_label.pack(pady=10)
                else:
                    # Crear el Treeview para mostrar la información como una tabla
                    columns = ("ID (Encriptado)", "ID (Desencriptado)", "Nombre", "Descripción", "Stock", "Fecha", "Usuario")
                    tree = ttk.Treeview(content_frame, columns=columns, show="headings")

                    # Configurar encabezados de columna
                    for col in columns:
                        tree.heading(col, text=col)
                        tree.column(col, width=120)

                    # Insertar datos en el Treeview
                    for row in rows:
                        encrypted_id = row[0]
                        decrypted_id = decrypt_data(encrypted_id)
                        tree.insert("", "end", values=(encrypted_id, decrypted_id, row[1], row[2], row[3],row[4],row[5]), tags=(decrypted_id,))


                        

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
            content_frame.destroy()
            cursor.close()
            connection.close()

        content_frame.protocol("WM_DELETE_WINDOW", close_inventory_window)

def check_inventory_ELIMINADO_handler(content_frame):
    # Limpiar el contenido existente en el frame
    for widget in content_frame.winfo_children():
        widget.destroy()

    check_inventory_eliminado(content_frame)


def check_inventory_lector(content_frame):
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

        # Etiquetas y entradas para el nombre y la descripción (Búsqueda)
        name_label = tk.Label(content_frame, text="Nombre del Producto:")
        name_label.pack()

        name_entry = tk.Entry(content_frame)
        name_entry.pack()

        description_label = tk.Label(content_frame, text="Descripción del Producto:")
        description_label.pack()

        description_entry = tk.Entry(content_frame)
        description_entry.pack()

        # Función para abrir un mensaje con el ID encriptado
        # Función para abrir un mensaje con el ID encriptado
        def show_encrypted_id_message(encrypted_id):
            messagebox.showinfo("ID Encriptado", f"El producto tiene el ID encriptado: {encrypted_id}")


        # Función para mostrar inventario desencriptando tanto el ID como los otros datos
        def show_inventory(search_name="", search_description=""):
            try:
                nonlocal rows, cursor  # Acceder a las variables externas 'rows' y 'cursor'

                # Limpiar el contenido previo en la ventana de inventario
                for widget in content_frame.winfo_children():
                    widget.destroy()

                # Etiqueta para mostrar resultados de búsqueda
                search_result_label = tk.Label(content_frame, text=f"Resultados para {search_name} {search_description}",font=("Roboto Cn",16))
                search_result_label.pack(pady=10)

                # Etiquetas y entradas para el nombre y la descripción (Búsqueda)
                name_label = tk.Label(content_frame, text="Nombre del Producto:",font=("Roboto Cn",16))
                name_label.pack()

                name_entry = tk.Entry(content_frame,font=("Roboto Cn",18))
                name_entry.pack()

                description_label = tk.Label(content_frame, text="Descripción del Producto:",font=("Roboto Cn",16))
                description_label.pack()

                description_entry = tk.Entry(content_frame,font=("Roboto Cn",18))
                description_entry.pack()

                # Botón para realizar la búsqueda
                search_button = tk.Button(
                    content_frame, 
                    text="Buscar", 
                    command=lambda: show_inventory(name_entry.get(), description_entry.get())
                    ,font=("Roboto Cn",18)
                    , bg="#4DA900"
                    , fg="white"
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
                    not_found_label = tk.Label(content_frame, text="Producto no encontrado", font=("Roboto Cn",16))
                    not_found_label.pack(pady=10)
                else:
                    # Crear el Treeview para mostrar la información como una tabla
                    columns = ("ID (Encriptado)", "ID (Desencriptado)", "Nombre", "Descripción", "Stock")
                    tree = ttk.Treeview(content_frame, columns=columns, show="headings")

                    # Configurar encabezados de columna
                    for col in columns:
                        tree.heading(col, text=col)
                        tree.column(col, width=100)

                    # Insertar datos en el Treeview
                    for row in rows:
                        encrypted_id = row[0]
                        decrypted_id = decrypt_data(encrypted_id)
                        tree.insert("", "end", values=(encrypted_id, decrypted_id, row[1], row[2], row[3]), tags=(decrypted_id,))


                        

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
            content_frame.destroy()
            cursor.close()
            connection.close()

        content_frame.protocol("WM_DELETE_WINDOW", close_inventory_window)

def check_inventory_lector_handler(content_frame):
    # Limpiar el contenido existente en el frame
    for widget in content_frame.winfo_children():
        widget.destroy()

    check_inventory_lector(content_frame)


def edit_product_window(product_id):
    edit_window = tk.Toplevel()
    edit_window.title("Editar Producto")
    edit_window.geometry("400x350")

    # Labels e Inputs para mostrar y editar los datos del producto
    product_name_label = tk.Label(edit_window, text="Nuevo Nombre del Producto:", font=("Roboto Cn",16))
    product_name_label.pack()

    product_name_entry = tk.Entry(edit_window, font=("Roboto Cn",18))
    product_name_entry.pack()

    description_label = tk.Label(edit_window, text="Nueva Descripción:", font=("Roboto Cn",16))
    description_label.pack()

    description_entry = tk.Entry(edit_window, font=("Roboto Cn",18))
    description_entry.pack()

    stock_label = tk.Label(edit_window, text="Nuevo Stock Actual:", font=("Roboto Cn",16))
    stock_label.pack()

    # Asignar la función de validación para aceptar solo valores numéricos
    vcmd = (edit_window.register(validate_numeric_input), '%S')
    product_id_entry = tk.Entry(edit_window, validate="key", validatecommand=vcmd, font=("Roboto Cn",18))
    product_id_entry.pack()

    # Botón para aplicar los cambios
    apply_button = tk.Button(edit_window, text="Aplicar Cambios", command=lambda: apply_changes(
        product_id,
        product_name_entry.get().lower(),  # Convertir el nombre a minúsculas
        description_entry.get().lower(),  # Convertir la descripción a minúsculas
        int(product_id_entry.get()),  # Convertir el stock a entero
        edit_window
    )
    , font=("Roboto Cn",18),
    bg='#4DA900', fg='white'
    )
    apply_button.pack()



def apply_changes(product_id, updated_name, updated_description, updated_stock, edit_window):
    try:
        # Conexión a la base de datos
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="pruebas_inventario"
        )
        cursor = connection.cursor()

        # Ejecutar consulta SQL para actualizar los datos del producto
        query_update_product = "UPDATE Producto SET Nombre = %s, Descripcion = %s, StockActual = %s WHERE ID = %s"
        cursor.execute(query_update_product, (
            updated_name.lower(),
            updated_description.lower(),
            updated_stock,
            product_id
        ))
        connection.commit()

        messagebox.showinfo("Éxito", "Cambios aplicados exitosamente")

        # Cerrar conexión
        cursor.close()
        connection.close()

        # Cerrar la ventana de edición
        edit_window.destroy()

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al aplicar los cambios: {err}")

# ...
#funcion nueva 2
def admin_menu(encrypted_id):
    admin_menu_window = tk.Toplevel()
    admin_menu_window.title("Menú de Administrador")
    admin_menu_window.geometry("200x150")

    # Función para cerrar la ventana "Menú de Administrador" y abrir la nueva ventana
    def close_admin_menu():
        admin_menu_window.destroy()
        # Aquí puedes abrir la nueva ventana que desees después de cerrar el menú de administrador
        # Por ejemplo, abrir la ventana principal de edición
        edit_product_window(encrypted_id)
    def close_admin_menu_delete():
        admin_menu_window.destroy()
        # Aquí puedes abrir la nueva ventana que desees después de cerrar el menú de administrador
        # Por ejemplo, abrir la ventana principal de edición
        delete_product(encrypted_id)

    # Botón para Editar
    edit_button = tk.Button(admin_menu_window, text="Editar", command=close_admin_menu)
    edit_button.pack(pady=10)

    # Botón para Borrar (stand by por ahora)
    delete_button = tk.Button(admin_menu_window, text="Borrar",  command=close_admin_menu_delete)
    delete_button.pack(pady=10)

# Función para configurar el evento de clic en una fila del Treeview
def open_message(event):
    item = event.widget.selection()
    event.widget.item(item, open=True)

def delete_product(encrypted_id):
    global current_user_name
    print(current_user_name)
    try:
        # Conexión a la base de datos
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="pruebas_inventario"
        )
        cursor = connection.cursor()

        # Obtener datos del producto antes de borrar
        query_get_product_data = "SELECT * FROM Producto WHERE ID = %s"
        cursor.execute(query_get_product_data, (encrypted_id,))
        product_data = cursor.fetchone()

        if product_data:
            # Almacenar datos en la tabla de respaldo
            query_insert_into_respaldo = "INSERT INTO producto_respaldo (ID, Nombre, Descripcion, StockActual, fecha_eliminacion,usuario) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query_insert_into_respaldo, (product_data[0], product_data[1], product_data[2], product_data[3], date.today(),current_user_name))

            # Borrar datos de la tabla principal
            query_delete_product = "DELETE FROM Producto WHERE ID = %s"
            cursor.execute(query_delete_product, (encrypted_id,))

            connection.commit()
            messagebox.showinfo("Éxito", "Producto eliminado exitosamente")
        else:
            messagebox.showerror("Error", "No se encontró el producto con el ID proporcionado")

        # Cerrar conexión
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al borrar el producto: {err}")




# Función para manejar la selección del menú principal
def menu_handler(option, user_label, content_frame,window):
    global current_user_permissions, current_user_name

    # Limpiar el contenido existente en el frame
    for widget in content_frame.winfo_children():
        widget.destroy()

    if option == 1:
        if current_user_permissions == "admin":
            add_product_handler(content_frame)
        else:
            content = "Permisos Denegados Para Ingreso De Productos"
            
    elif option == 2:
        
        if current_user_permissions == "admin":
            check_inventory_handler(content_frame)
        else:
            content = "Permisos Denegados Para Revisar El Inventario De Admninistrador"
    elif option == 3:
        # Lógica para la opción "Revisar Inventario(Lector)"
        check_inventory_lector_handler(content_frame)
    elif option == 4:
        if current_user_permissions == "admin":
            check_inventory_ELIMINADO_handler(content_frame)
        else:
            content = "Permisos Denegados Para Revisar Inventario De Productos Eliminados"
    elif option == 5:
        # Lógica para la opción "Crear Usuario"
        if current_user_permissions == "admin":
            create_user_handler(content_frame)
        else:
            content = "Permisos Denegados Para Crear Usuario"
        
    elif option == 6:
        window.destroy()  # Cerrar la ventana del menú principal y volver a la ventana de inicio de sesión
        main_window()
    elif option == 7:
        window.destroy()  # Cerrar la ventana del menú principal y volver a la ventana de inicio de sesión
        
    else:
        content = "Opción no reconocida"

    # Actualizar la etiqueta del usuario
    user_label.config(text=f"Bienvenido, {current_user_permissions} {current_user_name}")

    # Mostrar el contenido en el marco
    display_content(content_frame, content)

# Monntrar contenido
def display_content(content_frame, content):
    # Limpiar el marco antes de mostrar nuevo contenido
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Mostrar el nuevo contenido en el marco
    label = tk.Label(content_frame, text=content, font=('calibri', 14))
    label.pack(padx=20, pady=20)  

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
    
    global current_user_name, current_user_permissions  # Agrega current_user_permissions
    rut = rut_entry.get()
    password = password_entry.get()
    result = verify_rut(rut)

    if "-" in result:
        # Verificar el RUT en la base de datos
        if check_credentials_in_database(result, password):
            current_user_name = get_user_name(result)  # Almacenar el nombre del usuario globalmente
            current_user_permissions = get_user_permissions(result)  # Almacenar los permisos del usuario globalmente
            user_label.config(text=f"Bienvenido, {current_user_permissions} {current_user_name}")
            
            window.destroy()  # Cerrar la ventana de inicio de sesión
            
            menu_window()  # Abrir la ventana del menú principal
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")
    else:
        messagebox.showerror("Error", "No ha ingresado ningun RUT")

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
        if err.errno == 1366:  # El código de error 1366 corresponde a problemas de conversión
            messagebox.showerror("Error", "Error relacionado con el RUT")
        else:
            messagebox.showerror("Error", f"Error al verificar las credenciales en la base de datos: {err}")

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


def get_user_permissions(rut):
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
        query = "SELECT permisos FROM usuario WHERE rut = %s"
        cursor.execute(query, (rut,))
        user_name = cursor.fetchone()[0]

        # Cerrar conexión
        cursor.close()
        connection.close()

        return user_name

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al obtener el permiso del usuario desde la base de datos: {err}")
        return ""

# Función para cerrar la sesión
def close_session(user_label, menu_window):
    global current_user_name  # Restablecer la variable global del nombre del usuario
    current_user_name = ""
    user_label.config(text="")
    menu_window.destroy()  # Cerrar la ventana del menú principal
    main_window()  # Abrir la ventana de inicio de sesión nuevamente

# Función para crear la ventana de añadir productos
def validate_numeric_input(char):
    # Función de validación para permitir solo caracteres numéricos
    return char.isdigit() or char == ""

def add_product_content(content_frame):
    # Contenido de "Añadir Productos"
    product_id_label = tk.Label(content_frame, text="ID del Producto:", font=("Roboto Cn",16) )
    product_id_label.pack()

    # Utilizar la validación de entrada para permitir solo valores numéricos
    vcmd = (content_frame.register(validate_numeric_input), '%S')
    product_id_entry = tk.Entry(content_frame, validate="key", validatecommand=vcmd, font=("Roboto Cn",18))
    product_id_entry.pack()

    product_name_label = tk.Label(content_frame, text="Nombre del Producto:", font=("Roboto Cn",16))
    product_name_label.pack()

    product_name_entry = tk.Entry(content_frame, font=("Roboto Cn",18))
    product_name_entry.pack()

    description_label = tk.Label(content_frame, text="Descripción:", font=("Roboto Cn",16))
    description_label.pack()

    description_entry = tk.Entry(content_frame, font=("Roboto Cn",18))
    description_entry.pack()

    stock_label = tk.Label(content_frame, text="Stock Actual:", font=("Roboto Cn",16))
    stock_label.pack()

    # Validación de entrada para permitir solo valores numéricos en stock_actual


    # Utilizar la validación de entrada para permitir solo valores numéricos
    vcmd = (content_frame.register(validate_numeric_input), '%S')
    product_id_entry = tk.Entry(content_frame, validate="key", validatecommand=vcmd, font=("Roboto Cn",18))
    product_id_entry.pack()


    submit_button = tk.Button(content_frame, text="Añadir Producto", command=lambda: add_product(
        product_id_entry.get(),
        product_name_entry.get(),
        description_entry.get(),
        product_id_entry.get()
    )
    , font=("Roboto Cn",18),
    bg='#4DA900', fg='white'
    )
    submit_button.pack()


def add_product_handler(content_frame):
    # Limpiar el contenido existente en el frame
    for widget in content_frame.winfo_children():
        widget.destroy()

    add_product_content(content_frame)



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
def create_user_window(content_frame):
    

    
    rut_label = tk.Label(content_frame, text="RUT (1-8 dígitos):" , font=("Roboto Cn",16))
    rut_label.pack()

    rut_entry = tk.Entry(content_frame, font=("Roboto Cn",18))
    rut_entry.pack()

    name_label = tk.Label(content_frame, text="Nombre:", font=("Roboto Cn",16))
    name_label.pack()

    name_entry = tk.Entry(content_frame, font=("Roboto Cn",18))
    name_entry.pack()

    password_label = tk.Label(content_frame, text="Contraseña:", font=("Roboto Cn",16))
    password_label.pack()

    password_entry = tk.Entry(content_frame, show="*", font=("Roboto Cn",18))
    password_entry.pack()

    user_type_label = tk.Label(content_frame, text="Tipo de Usuario:")
    user_type_label.pack()

    # Definir las opciones y la variable de la opción seleccionada
    user_type_var = tk.StringVar(content_frame)
    user_type_var.set("admin")  # Valor predeterminado
    user_type_options = ["admin", "lector"]

    # Crear el OptionMenu con personalización de fuente y color
    user_type_menu = tk.OptionMenu(content_frame, user_type_var, *user_type_options)
    user_type_menu.config(font=("Roboto Cn",14), bg="#4DA900", fg="white")  # Personalizar la fuente y el color del texto
    user_type_menu.pack()
    submit_button = tk.Button(content_frame, text="Crear Usuario", font=("Roboto Cn",18), bg="#4DA900", fg="white", command=lambda: create_user(
        rut_entry.get(),
        name_entry.get(),
        password_entry.get(),
        user_type_var.get()
        
    )

    )
    
    submit_button.pack()

def create_user_handler(content_frame):
    # Limpiar el contenido existente en el frame
    for widget in content_frame.winfo_children():
        widget.destroy()

    create_user_window(content_frame)



# Función para crear un usuario
def create_user(rut, name, password, user_type):
    try:
        # Verificar que ningún campo esté vacío
        if not rut or not name or not password or not user_type:
            messagebox.showerror("Error", "No puede dejar campos vacíos")
            return
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$', password):
            messagebox.showerror("Error", "La contraseña debe tener al menos 12 caracteres, 1 número, 1 mayuscula y 1 caracter especial")
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
    def create_content_frame():
        # Crear y devolver un marco para mostrar el contenido
        frame = tk.Frame(menu_window, bg='#ffffff', bd=5)
        frame.place(relx=0.7, rely=0.2, relwidth=0.7, relheight=0.7, anchor='n')
        return frame

    menu_window = tk.Tk()
    menu_window.title("Menú Principal")
    #menu_window.attributes('-fullscreen',True)
    menu_window.geometry("1400x700")
    menu_window.configure(bg='#f0f0f0')  # Fondo de color gris claro

    user_label = tk.Label(menu_window, text=f"Bienvenido, {current_user_permissions} {current_user_name}", anchor="w", bg='#f0f0f0', padx=10)
    user_label.pack(pady=10, fill='x')  # Ajuste el ancho de acuerdo con el contenido

    # Crear un marco para mostrar el contenido de las opciones del menú
    content_frame = create_content_frame()

    # Botones para las opciones del menú
    options = ["Añadir Productos", "Revisar Inventario(ADMIN)", "Revisar Inventario(Lector)",
               "Revisar datos eliminados", "Crear Usuario", "Cerrar Sesión", "Cerrar Aplicacion"]

    for i, option in enumerate(options, start=1):
        button = tk.Button(menu_window, text=option, command=lambda i=i: menu_handler(i, user_label, content_frame,menu_window),
                           bg='#4CAF50', fg='white', padx=10, pady=5, anchor='w', width=40, font=("Roboto Cn",16))
        button.pack(pady=5, padx=10, anchor='w')  # Agregado espacio a la izquierda y arriba de los botones

    # Estilo moderno para los botones
    style = ttk.Style()
    style.configure('TButton', borderwidth='5',)

    menu_window.mainloop()


# Función para crear la ventana principal

def main_window():
    window = tk.Tk()
    window.title("Gestor de Inventario - Inicio de Sesión")
    window.geometry("1400x700")
    #window.attributes('-fullscreen',True)
    window.configure(bg='#f0f0f0')  # Fondo de color gris claro

    # Función de validación para el RUT
    def validate_rut_input(char, current_value):
        return (char.isdigit() or char == "") and len(current_value) <= 8

    validate_rut = window.register(validate_rut_input)

    user_image = PhotoImage(file="C:/Users/Theal/Videos/PROYECTO INTEGRACION(RFID)/Software/user.png")  # Reemplaza "ruta_de_la_imagen.png" con la ruta de tu imagen
    resized_image = user_image.subsample(3, 3)  # Ajusta el tamaño según tus necesidades
    user_image_label = tk.Label(window, image=resized_image, bg='#f0f0f0')
    user_image_label.pack(pady=5)
    user_image_label.pack(pady=5)
    # Etiqueta e entrada para el RUT
    login_label = tk.Label(window, text="Ingrese su RUT (1-8 dígitos):", bg='#f0f0f0',font=("Roboto Cn",16),anchor="w", justify="left")
    login_label.pack(pady=10)

    rut_entry = tk.Entry(window, validate="key", validatecommand=(validate_rut, "%S", "%P"), font=("Roboto Cn",16))
    rut_entry.pack(pady=10)

    # Etiqueta e entrada para la contraseña
    password_label = tk.Label(window, text="Ingrese su Contraseña:", bg='#f0f0f0', font=("Roboto Cn",16),justify="left")
    password_label.pack(pady=10)

    password_entry = tk.Entry(window, show="*",font=("Roboto Cn",16))
    password_entry.pack(pady=10)

    # Etiqueta para el mensaje de usuario
    user_label = tk.Label(window, text="", anchor="e", bg='#f0f0f0')
    user_label.pack(pady=5, padx=5)

    # Botón de inicio de sesión
    login_button = tk.Button(window, text="Iniciar Sesión", command=lambda: login_handler(window, user_label, rut_entry, password_entry),
                             bg='#4CAF50', fg='white', padx=10, pady=5, font=("Roboto Cn",18))
    login_button.pack(pady=10)

    #A
    close_label = tk.Label(window, text="", anchor="e", bg='#f0f0f0')
    close_label.pack(pady=5, padx=5)

    # Botón de inicio de sesión
    login_button = tk.Button(window, text="Cerrar Aplicacion", command=lambda: window.destroy(),
                             bg='#940909', fg='white', padx=10, pady=5, font=("Roboto Cn",18                                            ))
    login_button.pack(pady=10)
    
    # Estilo moderno para el botón
    style = ttk.Style()
    style.configure('TButton', font=('calibri', 10, 'bold'), borderwidth='4')

    window.mainloop()


# Iniciar la aplicación

main_window()
