import tkinter as tk
from tkinter import messagebox

# Función para validar si una entrada es un número flotante
def es_numero(valor):
    try:
        float(valor)
        return True
    except ValueError:
        return False

# Función para manejar la entrada de los datos generales
def submit_grl_info():
    global box_list
    comp = nmb_comp.get()
    i_freq = init_freq_entry.get()
    f_freq = final_freq_entry.get()
    s_freq = steps_freq_entry.get()
    i_impedance = charac_imp_entry.get()

    # Verificar si todos los campos están completos
    if not (comp and i_freq and i_impedance and f_freq and s_freq):
        messagebox.showwarning("Error", "Campos incompletos")
        return

    # Validar que las frecuencias y la impedancia sean números válidos
    if not (es_numero(i_freq) and es_numero(f_freq) and es_numero(s_freq) and es_numero(i_impedance)):
        messagebox.showwarning("Error", "Las frecuencias y la impedancia deben ser números válidos")
        return

    # Crear el frame para registro de componentes
    component_reg_frame = tk.LabelFrame(frame, text="Registro de componentes")
    component_reg_frame.grid(row=1, column=0, sticky="news", padx=20, pady=20)

    # Crear las etiquetas y cajas de texto para los componentes
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
    svd_info = []
    
    # Procesar cada entrada y dividirla en partes
    for i in box_list:
        texto = i.get()
        partes = texto.split()

        # Verificar si la entrada tiene 4 partes
        if len(partes) == 4:
            var1, var2, var3, var4 = partes[:4]
            if (var1 == 'R' or var1 == 'L' or var1== 'C'):
                svd_info.append((var1, var2, var3, var4))
            else:
                messagebox.showerror("Error", "Valor inválido")
            
        else:
            messagebox.showerror("No hay suficiente información")
    
    # Mostrar la información guardada
    if svd_info:
        info_mensaje = "\n".join([f"Componente {i+1}: {', '.join(info)}" for i, info in enumerate(svd_info)])
        messagebox.showinfo("Información Guardada", info_mensaje)
    else:
        messagebox.showwarning("Advertencia", "No se ha ingresado suficiente información.")

# Principal Window
ventana = tk.Tk()
ventana.title("Proyecto - Ingeniería de Microondas I")

# Crear el marco principal
frame = tk.Frame(ventana)
frame.pack(padx=20, pady=20)

# Información general
general_info_frame = tk.LabelFrame(frame, text="Información general del circuito")
general_info_frame.grid(row=0, column=0, padx=20, pady=20)

# Etiquetas de información general
component_number_frame = tk.Label(general_info_frame, text="Número de componentes")
component_number_frame.grid(row=0, column=0, sticky="w")

init_freq_label = tk.Label(general_info_frame, text="Frecuencia inicial (Hz)")
init_freq_label.grid(row=1, column=0, sticky="w")
final_freq_label = tk.Label(general_info_frame, text="Frecuencia final (Hz)")
final_freq_label.grid(row=2, column=0, sticky="w")
steps_freq_label = tk.Label(general_info_frame, text="Pasos de frecuencia")
steps_freq_label.grid(row=3, column=0, sticky="w")
charac_imp_label = tk.Label(general_info_frame, text="Valor impedancia característica (Ω)")
charac_imp_label.grid(row=4, column=0, sticky="w")

# Entradas para la información general
nmb_comp = tk.IntVar()
component_number_entry = tk.Entry(general_info_frame, textvariable=nmb_comp)
init_freq_entry = tk.Entry(general_info_frame)
final_freq_entry = tk.Entry(general_info_frame)
steps_freq_entry = tk.Entry(general_info_frame)
charac_imp_entry = tk.Entry(general_info_frame)

# Ubicación de las entradas en la interfaz
component_number_entry.grid(row=0, column=1)
init_freq_entry.grid(row=1, column=1)
final_freq_entry.grid(row=2, column=1)
steps_freq_entry.grid(row=3, column=1)
charac_imp_entry.grid(row=4, column=1)

# Botón para enviar la información general
submit_gnl_inf_button = tk.Button(general_info_frame, text="Enviar Información", command=submit_grl_info)
submit_gnl_inf_button.grid(row=5, column=0, columnspan=2, pady=10)


# Ejecutar la interfaz gráfica
ventana.mainloop()
