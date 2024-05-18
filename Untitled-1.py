from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tkinter import *

def consultar_nombre():
    # Devolver el nombre mediante el RUT
    # Se declaran variables globales
    rut = None
    nombre = None

    # Inicia el navegador
    driver = webdriver.Chrome()  # o webdriver.Firefox(), dependiendo de tu navegador

    # Se hace la consulta GET a la API SII
    rut = entry_rut.get()
    driver.get("https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js")

    # Utiliza By.ID para encontrar el elemento por ID
    txt_rut = driver.find_element(By.ID, "txtRut")
    txt_rut.send_keys(rut)
    txt_rut.send_keys(Keys.TAB)  # Simula el evento de perder el foco
    time.sleep(1)  # Espera un poco para asegurarte de que la consulta se complete

    # Obtiene el nombre desde la página
    nombre_element = driver.find_element(By.ID, "bodyNombre")
    nombre = nombre_element.text

    # Actualiza la etiqueta de saludo
    label_saludo.config(text=f"Hola {nombre}")

    # Cierra el navegador
    driver.quit()

# Crea la interfaz gráfica
root = Tk()
root.title("Consulta de Nombre por RUT")

# Etiqueta y entrada para ingresar el RUT
label_rut = Label(root, text="Ingrese el RUT:")
label_rut.pack()

entry_rut = Entry(root)
entry_rut.pack()

# Botón para realizar la consulta
button_consultar = Button(root, text="Consultar Nombre", command=consultar_nombre)
button_consultar.pack()

# Etiqueta para mostrar el saludo
label_saludo = Label(root, text="")
label_saludo.pack()

# Función para cerrar la aplicación
def cerrar_aplicacion():
    root.destroy()

# Botón para cerrar la aplicación
button_cerrar = Button(root, text="Cerrar", command=cerrar_aplicacion)
button_cerrar.pack()

# Ejecuta el bucle principal de la interfaz gráfica
root.mainloop()
