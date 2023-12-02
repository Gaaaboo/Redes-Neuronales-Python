#Importaciones
import tkinter as tk
import os
import subprocess
from tkinter import PhotoImage

#Contenido de la clase
class InterfazPDI:
    def __init__(self, master):
        self.master = master
        master.title("PDI Sistema de Seguridad")

        #Colocar imagen de fondo a interfaz
        self.imagen_de_fondo = PhotoImage(file="unitec.ppm") #ppm admitido por Tkinter
        self.etiqueta = tk.Label(master, image=self.imagen_de_fondo)
        self.etiqueta.place(x=0, y=0, relwidth=1, relheight=1)  # Ocupa toda la ventana

        #Etiqueta de bienvenida
        self.label_bienvenida = tk.Label(master, text="Bienvenido al Sistema de Seguridad", font=("Helvetica", 15), fg='black')
        self.label_bienvenida.place(relx=0.5, rely=0.2, anchor='center') #Posicionamiento y centrado

        #Configurando el botón A
        self.boton_a = tk.Button(master, text="Iniciar cámara", font=("Helvetica", 15), command=self.iniciar_camara)
        self.boton_a.place(relx=0.5, rely=0.4, anchor='center')

        #Configurando el botón B
        self.boton_b = tk.Button(master, text="Acceder a grabaciones", font=("Helvetica", 15), command=self.acceder_grabaciones)
        self.boton_b.place(relx=0.5, rely=0.6, anchor='center')

        #Configurando el botón C
        self.boton_c = tk.Button(master, text="Salir", font=("Helvetica", 15),  command=self.salir)
        self.boton_c.place(relx=0.5, rely=0.8, anchor='center')

        #Ruta a tomar para visualizar contenidos con C
        self.carpeta_de_grabaciones = r"C:\Users\Gaaboo\Documents\Python\Grabaciones_Auditorio"

        #Se redimensiona el tamaño de la ventana con el de la imagen 
        width, height = self.imagen_de_fondo.width(), self.imagen_de_fondo.height()
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        #Realizando el ajuste con base a la redimension
        if width > screen_width or height > screen_height:
            master.geometry(f"{screen_width}x{screen_height}")
        else:
            master.geometry(f"{width}x{height}")

        #Acciones a realizar al presionar los botones
    def iniciar_camara(self):
        try:
            # Inicia el programa en un nuevo proceso sin bloquear
            subprocess.Popen(["python", r"C:\Users\Gaaboo\Documents\Python\Final_Proyecto.py"], shell=True)
        except Exception as e:
            print(f"Error al ejecutar el programa: {e}")
        finally:
            # Cierra la interfaz gráfica
            self.master.destroy()


    def acceder_grabaciones(self):
        #Se muestra la carpeta donde se almacenan las grabaciones obtenidas
        os.startfile(self.carpeta_de_grabaciones)

    def salir(self):
        #Finalica/Cierra la interfáz
        self.master.destroy()

#Muestra lo que esté en la clase (PDI) al ejecutarlo directamente
if __name__ == "__main__":
    root = tk.Tk()
    interfaz = InterfazPDI(root)
    root.mainloop()
