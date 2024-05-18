import time
import random
import pyautogui
import threading

class RFIDReader:
    # Esta clase es solo un marcador de posición, necesitarás reemplazarla con la implementación real

    def __init__(self):
        self.card_ids = [obtener_id_tarjeta() for _ in range(4)]  # Genera 4 IDs de tarjetas
        self.card_index = 0

    def read_card(self):
        # Simula la lectura de una tarjeta RFID
        card_id = self.card_ids[self.card_index]
        self.card_index = (self.card_index + 1) % 4  # Establece en bucle los 4 IDs
        return card_id

def obtener_id_tarjeta():
    # Simula la generación de un ID de tarjeta RFID (puedes cambiar esto según tus necesidades)
    return f'RFID_CARD_{random.randint(1000, 9999)}'

def escribir_en_campo_texto(texto):
    # Utiliza pyautogui para escribir en el campo de texto activo
    pyautogui.write(texto)

def simulador_rfid():
    try:
        reader = RFIDReader()  # Reemplaza con la inicialización real de tu lector RFID
        stop_event = threading.Event()

        def stop_simulacion():
            # Función para detener la simulación cuando se presiona 'q'
            input('Presiona Enter para detener la simulación...\n')
            stop_event.set()

        # Inicia un hilo para la función de detener la simulación
        stop_thread = threading.Thread(target=stop_simulacion)
        stop_thread.start()

        while not stop_event.is_set():
            # Simula la lectura de una tarjeta RFID
            card_id = reader.read_card()

            # Imprime el ID de la tarjeta leída
            print(f'Tarjeta RFID leída: {card_id}')

            # Escribe el ID de la tarjeta en el campo de texto activo
            escribir_en_campo_texto(card_id)

            # Puedes realizar acciones adicionales aquí con el ID de la tarjeta leída

            time.sleep(4)  # Espera 2 segundos antes de la próxima lectura

        print('Simulación RFID detenida.')

    except KeyboardInterrupt:
        print('Simulación RFID detenida.')

if __name__ == '__main__':
    simulador_rfid()
