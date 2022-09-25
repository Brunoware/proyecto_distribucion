import pandas as pd
from tkinter import Tk
from tkinter.filedialog import asksaveasfile

def guardar_ruta(df_in):
    root = Tk()  # abrir cuadro de dialogo
    try:
        file_dialog=asksaveasfile(mode='w',title='Hallo', defaultextension='.xlsx',filetypes=[('xlsx file','.xlsx'),('csv file','.csv')])
        with file_dialog as file:
            df_in.to_excel(file.name)
        print(file_dialog.name)
        
    except AttributeError:
        # si el usuario cancela guardar, filedialog devuelve None en lugar de un objeto de archivo, 
        # y el 'with' generará un error
        pass

    root.destroy() # cerrar cuadro de dialogo