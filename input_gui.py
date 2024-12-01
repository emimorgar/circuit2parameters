import tkinter as tk
from tkinter import messagebox
from circuit_class import Circuit


# Función para validar si una entrada es un número flotante
def es_numero(valor):
    try:
        float(valor)
        return True
    except ValueError:
        return False

# Función guarda la información general del circuito
def submit_grl_info():
    global box_list, i_freq, f_freq, s_freq, i_impedance, comp, input_nodes_list

    comp = nmb_comp.get()                    #guarda número de los componentes
    input_nodes = input_nodes_entry.get()    #guarda los nodos de entrada
    i_freq = init_freq_entry.get()           #guarda la frecuencia inicial
    f_freq = final_freq_entry.get()          #guarda la frecuencia final
    s_freq = steps_freq_entry.get()          #guarda los pasos que se darán
    i_impedance = charac_imp_entry.get()     #guarda eel valor de la impedancia característica

    input_nodes_list = input_nodes.strip().split()
    try:
        input_nodes_list = [int(i) for i in input_nodes_list]
    except ValueError:
        messagebox.showerror("ERROR", "Los nodos de entrada deben ser números enteros, no mas de un espacio entre ellos")
        return

    # Verificar si todos los campos están completos, si no manda un error 
    if not (comp and i_freq and i_impedance and f_freq and s_freq):
        messagebox.showwarning("ERROR", "Campos incompletos")
        return

    # Validar que las frecuencias y la impedancia sean números válidos
    if not (es_numero(i_freq) and es_numero(f_freq) and es_numero(s_freq) and es_numero(i_impedance)):
        messagebox.showwarning("ERROR", "las entradas deben ser numeros enteros")
        return

    # Crear el frame para registro de componentes
    component_reg_frame = tk.LabelFrame(frame, text="REGISTRO DE COMPONENTES")
    component_reg_frame.grid(row=1, column=0, sticky="news", padx=20, pady=20)

    # Crear las etiquetas y cajas de texto de acuerdo al número de componentes registrados 
    box_list = []  # Limpiar la lista de cajas antes de agregar nuevas
    for i in range(comp):
        label = tk.Label(component_reg_frame, text=f"Componente {i+1}:")
        label.grid(row=i, column=0, sticky="w", padx=5, pady=5)
        box = tk.Entry(component_reg_frame)
        box.grid(row=i, column=1, padx=5, pady=5)
        box_list.append(box)

    # Botón para guardar la información de los componentes (inicialmente oculto)
    submit_comp_inf_button = tk.Button(component_reg_frame, text="Guardar Información", command=save_comp_inf)    
    # Mostrar el botón para guardar la información de los componentes, justo debajo de las entradas
    submit_comp_inf_button.grid(row=comp, column=0, columnspan=2, pady=10)

# Función para guardar la información de los componentes
def save_comp_inf():
    components_info= []
    
    # Procesar cada entrada y dividirla en partes
    for i in box_list:
        texto = i.get()
        partes = texto.split()

        # Verificar si la entrada tiene 4 partes
        if partes[0] in ['R', 'L', 'C', 'S', 'O', 'T']:
            if len(partes) == 4:
                components_info.append([partes[0], float(partes[1]), int(partes[2]), int(partes[3])])
            elif len(partes) == 3:
                components_info.append([partes[0], float(partes[1]), int(partes[2])])
            else:
                messagebox.showerror("ERROR", "Descripcion del componente inválido, Ejemplo: C 1e4 1 2")
        else:
            messagebox.showerror("ERROR", "Describir el tipo de componente (R, L, C)")
    
    # Mostrar la información guardada
    if components_info:
        
        messagebox.showinfo("INFO", f"Se han guardado los siguientes componentes:\n{components_info}")

        circuit = Circuit(components = components_info,
                          input_nodes = input_nodes_list,
                          lower_freq_limit = float(i_freq),
                          upper_freq_limit = float(f_freq),
                          freq_step = float(s_freq),
                          z_charac = float(i_impedance)
                          )
        try:
            sim_circuit = circuit.run_simulation()
        except Exception as e:
            messagebox.showerror("ERROR", f"Ocurrió un error al simular el circuito: {e}")
        else:
            messagebox.showinfo("INFO", f"Se ha simulado el circuito correctamente")
            print(sim_circuit)
    else:
        messagebox.showwarning("Advertencia", "No se ha ingresado suficiente información.")

# Principal Window
ventana = tk.Tk()
ventana.title("Simulador de Circuitos - Ing Microondas I")

# Crear el marco principal
frame = tk.Frame(ventana)
frame.pack(padx=20, pady=20)

# Información general
general_info_frame = tk.LabelFrame(frame, text="INFORMACIÓN GENERAL DEL CIRCUITO") 
general_info_frame.grid(row=0, column=0, padx=20, pady=20)

# Etiquetas de información general
component_number_frame = tk.Label(general_info_frame, text="Número de componentes")
component_number_frame.grid(row=0, column=0, sticky="w")
input_nodes_label = tk.Label(general_info_frame, text="Nodos de entrada")
input_nodes_label.grid(row=1, column=0, sticky="w")
init_freq_label = tk.Label(general_info_frame, text="Frecuencia inicial (Hz)")
init_freq_label.grid(row=2, column=0, sticky="w")
final_freq_label = tk.Label(general_info_frame, text="Frecuencia final (Hz)")
final_freq_label.grid(row=3, column=0, sticky="w")
steps_freq_label = tk.Label(general_info_frame, text="Pasos de frecuencia (Hz)")
steps_freq_label.grid(row=4, column=0, sticky="w")
charac_imp_label = tk.Label(general_info_frame, text="Valor impedancia característica (Ω)")
charac_imp_label.grid(row=5, column=0, sticky="w")

# Entradas para la información general
nmb_comp = tk.IntVar()
component_number_entry = tk.Entry(general_info_frame, textvariable=nmb_comp)
input_nodes_entry = tk.Entry(general_info_frame)
init_freq_entry = tk.Entry(general_info_frame)
final_freq_entry = tk.Entry(general_info_frame)
steps_freq_entry = tk.Entry(general_info_frame)
charac_imp_entry = tk.Entry(general_info_frame)

# Ubicación de las entradas en la interfaz
component_number_entry.grid(row=0, column=1)
input_nodes_entry.grid(row=1, column=1)
init_freq_entry.grid(row=2, column=1)
final_freq_entry.grid(row=3, column=1)
steps_freq_entry.grid(row=4, column=1)
charac_imp_entry.grid(row=5, column=1)

# Botón para enviar la información general
submit_gnl_inf_button = tk.Button(general_info_frame, text="Enviar Información", command=submit_grl_info)
submit_gnl_inf_button.grid(row=6, column=0, columnspan=2, pady=10)


# Ejecutar la interfaz gráfica
ventana.mainloop()
