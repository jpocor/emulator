from tkinter import ttk, messagebox
import tkinter as tk
from sense_emu import SenseHat

from datetime import datetime

# TODO - Crear fichero de configuración y utilizarlo en esta clase
# Añadir path respecto a la ejecución de este fichero para que en ese mismo directorio cree
# el fichero *.csv con los datos monitorizados --> utilizar sys u os para encontrar el path actual

class Monitor():
    def __init__(self, window):
        # VARIABLES DE CONTROL
        self.dimensions = '800x600'
        self.style_button = {
            'iniciar': {
                'bg': '#CCFF99',
                'fg': 'black',
                'relief': 'flat',
                'text': 'Iniciar',
            },
            'parar': {
                'bg': '#FF6666',
                'fg': 'black',
                'relief': 'flat',
                'text': 'Parar',
            } 
        }
        # Inicializamos con valor 1 INT
        self.medida_selected = tk.IntVar(value=1)
        # Incicalizamos con valor 0 FALSE
        self.add_in_list = tk.IntVar(value=0)
        # Valor defecto periodo
        self.period_default = 1000
        # Contador registros
        self.counter = 1
         # DataStore para gestionar los datos mostrados en la tabla
        self.data_store = []

        # Instancia Tkinter para poder gestionar los widgets
        self.window = window
        # Instancia SenseHat para gestionar comunicacion con el emulador
        self.emulator = sense

        # Métodos para construir la interfaz
        self.sizer()
        self.title_window()
        self.main_menu()
        self.tabs()
        
    def sizer(self):
        self.window.geometry(self.dimensions)

    def title_window(self):
        self.window.title('Práctica GUI SenseHat')
    
    def main_menu(self):
        opciones_list = tk.Menu()
        opciones_list.add_command(label='Propiedades', command=self.options)

        root_menu = tk.Menu()
        root_menu.add_cascade(label='Opciones', menu=opciones_list)
        self.window.config(menu=root_menu)

    def options(self):
        # New Window over main window
        self.win_option = tk.Toplevel()
        self.win_option.title('Editor de opciones')
        self.win_option.geometry('300x150')

        tk.Label(self.win_option, text='Período: ').grid(row=0, column=0, padx=25, pady=20)
        periodo = tk.Entry(self.win_option)
        periodo.grid(row=0, column=1)

        tk.Button(self.win_option, text='Guardar', command=lambda: self.config_periodo(periodo.get())).grid(row=1, column=0, padx=20, sticky=tk.W)
    
    def config_periodo(self, value):
        operation_valid = False
        try:
            num = int(value)
            operation_valid = True
            # Modificamos el label Período con el nuevo valor
            self.marcador['text'] = str(value)
            # Modificamos el valor default para período
            self.period_default = num
                
        except ValueError as e:
            # TODO --> lanzar una ventana message alerta diciendo que solo introduzca valores numéricos
            messagebox.showerror(title='Error datos introducidos', message='Debe introducir un valor numérico - digitos(0-9)')
            print(e)
        
        # Una vez ejecutada la acción al pulsar el botón cerramos ventana auxiliar
        if operation_valid:
            self.win_option.destroy()

    def tabs(self):
        # Create widget Notebook --> Container tabs
        notebook = ttk.Notebook(self.window)
        # Create tabs
        sheet1 = ttk.Frame(notebook)
        sheet2 = ttk.Frame(notebook)
        # Add tabs to Notebook
        notebook.add(sheet1, text='Monitorizacion')
        notebook.add(sheet2, text='Gráfica')
        # Add all widgets to each tab
        self.containter_widgets_monitorizacion(sheet1)
        self.container_widgets_grafica(sheet2)
        notebook.pack(fill='both', expand='yes')

    def containter_widgets_monitorizacion(self, win_reference):
        self.frame_control(win_reference)
        self.frame_medidas(win_reference)
        self.frame_historico(win_reference)

    def container_widgets_grafica(self, win_reference):
        pass

    def frame_control(self, window):
        # Create a frame container
        frame = tk.LabelFrame(window, text='Control')
        frame.grid(row=0, column=0, columnspan=3, padx=140, pady=20)

        # Button Start/Stop
        self.action_app = tk.Button(frame, **self.style_button['iniciar'], command=self.start_app)
        self.action_app.grid(row=1, columnspan=2)
    
        # Labels
        tk.Label(frame, text='Período: ').grid(row=2, column=0)
        self.marcador = tk.Label(frame, text='1000')
        self.marcador.grid(row=2, column=1)

    def start_app(self):
        # Obtener estado del botón através del texto indicado --> ultima posición tupla
        state_button = self.action_app.config('text')[-1]
        if state_button == 'Iniciar':
            self.action_app.config(self.style_button['parar'])
            self.get_values_from_emu()
        elif state_button == 'Parar':
            self.abortar = True
            self.action_app.config(self.style_button['iniciar'])

        
    def get_values_from_emu(self):
        self.temp = self.emulator.temperature
        self.pres = self.emulator.pressure
        self.humd = self.emulator.humidity
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
       
        target_data = self.add_in_list.get()
        option = self.medida_selected.get()
        if target_data == 1:
            # Insert data in tree widget
            register = {
                'id': self.counter,
                'valor': self.temp,
                'datetime': date_time,
            }
            if option == 1:
                register['tipo'] = 'Temperatura'
                self.tree.insert('', 'end', text=self.counter, values=(self.temp, date_time, 'Temperatura'))
            elif option == 2:
                register['tipo'] = 'Presión'
                self.tree.insert('', 'end', text=self.counter, values=(self.pres, date_time, 'Presión'))
            elif option == 3:
                register['tipo'] = 'Humedad'
                self.tree.insert('', 'end', text=self.counter, values=(self.humd, date_time, 'Humedad'))
            
            self.data_store.append(register)
            self.counter +=1
            
        elif target_data == 0:
            # Limpiamos el contenido
            self.medida.delete(0,tk.END)
            # Añadir valor al Entry del Frame Medidas
            if option == 1:
                self.medida.insert(0, self.temp)
            elif option == 2:
                self.medida.insert(0, self.pres)
            elif option == 3:
                self.medida.insert(0, self.humd)
        
        print(self.data_store)

    def frame_medidas(self, window):
         # Create a frame container
        frame = tk.LabelFrame(window, text='Medidas')
        frame.grid(row=1, column=0, columnspan=3, pady=10)

        # Widget Input data
        self.medida = tk.Entry(frame, justify=tk.CENTER)
        self.medida.grid(row=2, column=0, columnspan=4)
        temp = tk.Radiobutton(frame, text='Temperartura', variable=self.medida_selected, value=1)
        temp.grid(row=3, column=0)
        pres = tk.Radiobutton(frame, text='Presión', variable=self.medida_selected, value=2)
        pres.grid(row=3, column=1)
        humd = tk.Radiobutton(frame, text='Humedad', variable=self.medida_selected, value=3)
        humd.grid(row=3, column=2)

    def frame_historico(self, win_reference):
        # Creat a frame container
        frame = tk.LabelFrame(win_reference, text='Historico')
        frame.grid(row=4, column=0, columnspan=8, pady=10)

        # Create Table using widget Treeview with 10 rows and 4 columns
        self.tree = ttk.Treeview(frame, height=13, columns=4)
        self.tree.grid(row=4, column=0, columnspan=3)
        self.tree["columns"] = ('Valor', 'DateTime', 'Tipo')
        # La primera columna es la referencia '#0'
        # El resto de referencias se obtiene de tree['columns']
        # anchor --> centrar texto cabecera
        self.tree.heading('#0', text='#Num', anchor=tk.CENTER)
        self.tree.heading('Valor', text='Valor', anchor=tk.CENTER)
        self.tree.heading('DateTime', text='Fecha/Hora', anchor=tk.CENTER)
        self.tree.heading('Tipo', text='Tipo', anchor=tk.CENTER)

        # Actions Buttons
        self.action_limpiar = tk.Button(frame, text='Limpiar', command=self.reset_table)
        self.action_limpiar.grid(row=5, column=0, sticky=tk.W + tk.E)
        self.action_media = tk.Button(frame, text='Calcular Media')
        self.action_media.grid(row=5, column=1, sticky=tk.W + tk.E)
        self.action_exportar = tk.Button(frame, text='Exportar', command=self.export_list)
        self.action_exportar.grid(row=5, column=2, sticky=tk.W + tk.E)

        # Action Checbox
        action_list = tk.Checkbutton(frame, text='Añadir a lista', variable=self.add_in_list)
        action_list.grid(row=6, column=0, columnspan=4)

    def reset_table(self):
        # Obtener todos los registros de nuestra tabla TREE
        records = self.tree.get_children()
        # Si la tabla TREE no está vacía, la vaciamos
        for element in records:
            self.tree.delete(element)

    def export_list(self):
        pass



if __name__ == '__main__':
    window = tk.Tk()
    sense = SenseHat()
    application = Monitor(window)
    window.mainloop()