import numpy as np
import matplotlib.pyplot as plt
import skrf as rf
import customtkinter as ctk
from tkinter import ttk, messagebox


# Función para mostrar la matriz seleccionada
def mostrar():
    # Obtener el nombre de la matriz seleccionada
    matriz_seleccionada = combobox_matrices.get()

    if matriz_seleccionada in matrices:
        matriz_valores = matrices[matriz_seleccionada]
        mostrar_ventana_matriz(matriz_seleccionada, matriz_valores, freq)
    else:
        ctk.CTkMessagebox.show_info("Error", "Selecciona una matriz válida")

# Función para crear la ventana emergente que muestra la matriz
def mostrar_ventana_matriz(nombre, matriz, freqs):
    ventana_matriz = ctk.CTkToplevel()  # Crear una ventana secundaria
    ventana_matriz.title(f"Valores de {nombre}")
    ventana_matriz.geometry("300x200")
    
    # Crear un texto con la información de cada matriz para cada frecuencia
    texto = ""
    for i, matriz in enumerate(matriz):
        texto += f"Frecuencia: {freqs[i] / 1e6:.2f} MHz\n"
        texto += "\n".join(["\t".join(map(str, fila)) for fila in matriz])
        texto += "\n\n"
    
    # Mostrar el nombre de la matriz y sus valores
    etiqueta_nombre = ctk.CTkLabel(ventana_matriz, text=f"Matriz: {nombre}", font=("Arial", 14, "bold"))
    etiqueta_nombre.pack(pady=10)

    # Usar un cuadro de texto con scroll para mostrar matrices grandes
    text_box = ctk.CTkTextbox(ventana_matriz, wrap="none", height=300)
    text_box.insert("1.0", texto)
    text_box.configure(state="disabled")  # Hacerlo de solo lectura
    text_box.pack(padx=10, pady=10, fill="both", expand=True)

    # Botón para cerrar la ventana
    boton_cerrar = ctk.CTkButton(ventana_matriz, text="Cerrar", command=ventana_matriz.destroy)
    boton_cerrar.pack(pady=10)
    
#Función para leer un archivo s2p
def read_s2p(filename):
    """
    Lee un archivo .s2p y extrae la frecuencia, los parámetros S y la resistencia de referencia.
    
    Args:
        filename (str): Ruta del archivo .s2p.
    
    Returns:
        tuple: 
            - freq (numpy.ndarray): Vector de frecuencias.
            - s_params (numpy.ndarray): Matriz de parámetros S (complejos).
            - z_ref (float): Resistencia de referencia.
    """
    frequencies = []
    s_parameters = []
    z_ref = None  # Inicializa la resistencia de referencia

    try:
        with open(filename, 'r') as file:
            for line in file:
                # Ignora comentarios y líneas vacías
                if line.startswith('!') or line.strip() == '':
                    continue
                
                # Procesa la línea de encabezado
                if line.startswith('#'):
                    header_parts = line.split()
                    try:
                        z_ref = float(header_parts[5])
                    except (IndexError, ValueError):
                        raise ValueError("El formato de la línea de encabezado no es válido.")
                    continue
                
                # Procesa los datos de los parámetros S
                parts = line.split()
                if len(parts) >= 9:
                    try:
                        freq = float(parts[0])
                        s11 = complex(float(parts[1]), float(parts[2]))
                        s21 = complex(float(parts[3]), float(parts[4]))
                        s12 = complex(float(parts[5]), float(parts[6]))
                        s22 = complex(float(parts[7]), float(parts[8]))
                    except ValueError:
                        raise ValueError("El formato de los datos de parámetros S no es válido.")
                    
                    #Matriz S para determinada frecuencia
                    matriz_s = np.array([[s11, s12], [s21, s22]], dtype=complex)
                    
                    #Guardar la frecuencia y la matriz
                    frequencies.append(freq)
                    s_parameters.append(matriz_s)

        # Verifica que se haya leído la resistencia de referencia
        if z_ref is None:
            raise ValueError("No se encontró la resistencia de referencia en el archivo.")
        
        return frequencies, s_parameters, z_ref
    
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {filename}")
    except Exception as e:
        raise RuntimeError(f"Ocurrió un error al procesar el archivo: {e}")

#Función para convertir parámetros S a ABCD
def s2ABCD(param, z_ref):
    
    if len(param) != 4:
        raise ValueError("Error")
    
    
    s11, s12, s21, s22 = param
    
    abcd_mat = [0]*4
    
    denom = 2 * s21
        
    abcd_mat[0] = complex(((1+s11) * (1-s22) + (s12*s21)) / (denom))
    abcd_mat[1] = complex(z_ref * ((1+s11) * (1+s22) - (s12*s21)) / (denom))
    abcd_mat[2] = complex((1/z_ref) * ((1+s11) * (1+s22) - (s12*s21)) / (denom)) 
    abcd_mat[3] = complex(((1-s11) * (1+s22) + (s12*s21)) / (denom))
    
    
    return abcd_mat

#Función para convertir parámetros ABCD a red de dos puertos    
def ABCD_2Port(param, freq):
    
    if len(param) != 4:
        raise ValueError("Error")
    
    A, B, C, D = param
    
    Yc = complex(1 / B)
    Ya = complex((D/B) - 1)
    Yb = complex((A/B) - 1)
    
    return Yc, Ya, Yb
    
#Función para convertir a dB
def parameter2dB(parameter):
    mag = np.abs(parameter)
    
    if mag == 0:
        return -np.inf
    #Conversión de magnitud a dB
    dB = 20 * np.log10(mag)
    
    return dB

#Función para convertir a Fase
def parameter2Phase(parameter):
    #Convierte el parámetro a fase en radianes
    phase = np.angle(parameter)
    
    #Convierte la fase en radianes a grados
    phase_degrees = np.degrees(phase)
    
    return phase_degrees

#Funcion para sacar parte real 
def parameter2real(parameter):
    real = parameter.real
    
    return real

#Funcion para sacar parte imaginaria 
def parameter2img(parameter):
    img = parameter.imag
    
    return img


# Función para graficar las magnitudes de las posiciones (1,1), (1,2), (2,1) y (2,2) de cada matriz
def plot_mag(matriz_seleccionada, freq):

    if matriz_seleccionada in matrices:
        
        matriz_valores = matrices[matriz_seleccionada]

        mag_1_1 = [np.abs(matriz[0, 0]) for matriz in matriz_valores]  # Magnitud de la posición (1,1)
        mag_1_2 = [np.abs(matriz[0, 1]) for matriz in matriz_valores]  # Magnitud de la posición (1,2)
        mag_2_1 = [np.abs(matriz[1, 0]) for matriz in matriz_valores]  # Magnitud de la posición (2,1)
        mag_2_2 = [np.abs(matriz[1, 1]) for matriz in matriz_valores]  # Magnitud de la posición (2,2)
    
        # Crear la figura con subgráficos
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Magnitud vs Frecuencia para cada posición', fontsize=16)

        # Graficar cada posición
        axs[0, 0].plot(freq, mag_1_1, marker='o', label='Posición (1,1)')
        axs[0, 0].set_title('Posición (1,1)')
        axs[0, 0].set_xlabel('Frecuencia (Hz)')
        axs[0, 0].set_ylabel('Magnitud')
        axs[0, 0].legend()

        axs[0, 1].plot(freq, mag_1_2, marker='o', label='Posición (1,2)')
        axs[0, 1].set_title('Posición (1,2)')
        axs[0, 1].set_xlabel('Frecuencia (Hz)')
        axs[0, 1].set_ylabel('Magnitud')
        axs[0, 1].legend()

        axs[1, 0].plot(freq, mag_2_1, marker='o', label='Posición (2,1)')
        axs[1, 0].set_title('Posición (2,1)')
        axs[1, 0].set_xlabel('Frecuencia (Hz)')
        axs[1, 0].set_ylabel('Magnitud')
        axs[1, 0].legend()

        axs[1, 1].plot(freq, mag_2_2, marker='o', label='Posición (2,2)')
        axs[1, 1].set_title('Posición (2,2)')
        axs[1, 1].set_xlabel('Frecuencia (Hz)')
        axs[1, 1].set_ylabel('Magnitud')
        axs[1, 1].legend()
        
        # Ajustar diseño para evitar superposición
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()
    else:
        ctk.CTkMessagebox.show_info("Error", "Selecciona una matriz válida")
       
# Función para graficar fase de las posiciones (1,1), (1,2), (2,1) y (2,2) de cada matriz
def plot_Phase(matriz_seleccionada, freq):
    
    if matriz_seleccionada in matrices:
        
        matriz_valores = matrices[matriz_seleccionada]

        Phase_1_1 = [parameter2Phase(matriz[0, 0]) for matriz in matriz_valores]  # Fase de la posición (1,1)
        Phase_1_2 = [parameter2Phase(matriz[0, 1]) for matriz in matriz_valores]  # Fase de la posición (1,2)
        Phase_2_1 = [parameter2Phase(matriz[1, 0]) for matriz in matriz_valores]  # Fase de la posición (2,1)
        Phase_2_2 = [parameter2Phase(matriz[1, 1]) for matriz in matriz_valores]  # Fase de la posición (2,2)
    
        # Crear la figura con subgráficos
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Fase vs Frecuencia para cada posición', fontsize=16)

        # Graficar cada posición
        axs[0, 0].plot(freq, Phase_1_1, marker='o', label='Posición (1,1)')
        axs[0, 0].set_title('Posición (1,1)')
        axs[0, 0].set_xlabel('Frecuencia (Hz)')
        axs[0, 0].set_ylabel('Fase')
        axs[0, 0].legend()

        axs[0, 1].plot(freq, Phase_1_2, marker='o', label='Posición (1,2)')
        axs[0, 1].set_title('Posición (1,2)')
        axs[0, 1].set_xlabel('Frecuencia (Hz)')
        axs[0, 1].set_ylabel('Fase')
        axs[0, 1].legend()

        axs[1, 0].plot(freq, Phase_2_1, marker='o', label='Posición (2,1)')
        axs[1, 0].set_title('Posición (2,1)')
        axs[1, 0].set_xlabel('Frecuencia (Hz)')
        axs[1, 0].set_ylabel('Fase')
        axs[1, 0].legend()

        axs[1, 1].plot(freq, Phase_2_2, marker='o', label='Posición (2,2)')
        axs[1, 1].set_title('Posición (2,2)')
        axs[1, 1].set_xlabel('Frecuencia (Hz)')
        axs[1, 1].set_ylabel('Fase')
        axs[1, 1].legend()
        
        # Ajustar diseño para evitar superposición
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()
    else:
        ctk.CTkMessagebox.show_info("Error", "Selecciona una matriz válida")

# Función para graficar dB de las posiciones (1,1), (1,2), (2,1) y (2,2) de cada matriz
def plot_dB(matriz_seleccionada, freq):
    
    if matriz_seleccionada in matrices:
        
        matriz_valores = matrices[matriz_seleccionada]

        dB_1_1 = [parameter2dB(matriz[0, 0]) for matriz in matriz_valores]  
        dB_1_2 = [parameter2dB(matriz[0, 1]) for matriz in matriz_valores]  
        dB_2_1 = [parameter2dB(matriz[1, 0]) for matriz in matriz_valores]  
        dB_2_2 = [parameter2dB(matriz[1, 1]) for matriz in matriz_valores]  

        # Crear la figura con subgráficos
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('dB vs Frecuencia para cada posición', fontsize=16)

        # Graficar cada posición
        axs[0, 0].plot(freq, dB_1_1, marker='o', label='Posición (1,1)')
        axs[0, 0].set_title('Posición (1,1)')
        axs[0, 0].set_xlabel('Frecuencia (Hz)')
        axs[0, 0].set_ylabel('Fase')
        axs[0, 0].legend()

        axs[0, 1].plot(freq, dB_1_2, marker='o', label='Posición (1,2)')
        axs[0, 1].set_title('Posición (1,2)')
        axs[0, 1].set_xlabel('Frecuencia (Hz)')
        axs[0, 1].set_ylabel('Fase')
        axs[0, 1].legend()

        axs[1, 0].plot(freq, dB_2_1, marker='o', label='Posición (2,1)')
        axs[1, 0].set_title('Posición (2,1)')
        axs[1, 0].set_xlabel('Frecuencia (Hz)')
        axs[1, 0].set_ylabel('Fase')
        axs[1, 0].legend()

        axs[1, 1].plot(freq, dB_2_2, marker='o', label='Posición (2,2)')
        axs[1, 1].set_title('Posición (2,2)')
        axs[1, 1].set_xlabel('Frecuencia (Hz)')
        axs[1, 1].set_ylabel('Fase')
        axs[1, 1].legend()
        
        # Ajustar diseño para evitar superposición
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()
    else:
        ctk.CTkMessagebox.show_info("Error", "Selecciona una matriz válida")
    
# Función para graficar parte real de las posiciones (1,1), (1,2), (2,1) y (2,2) de cada matriz
def plot_real(matriz_seleccionada, freq):

    
    if matriz_seleccionada in matrices:
        
        matriz_valores = matrices[matriz_seleccionada]
        
        real_1_1 = [parameter2real(matriz[0, 0]) for matriz in matriz_valores]  
        real_1_2 = [parameter2real(matriz[0, 1]) for matriz in matriz_valores]  
        real_2_1 = [parameter2real(matriz[1, 0]) for matriz in matriz_valores]  
        real_2_2 = [parameter2real(matriz[1, 1]) for matriz in matriz_valores]  

        # Crear la figura con subgráficos
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Real vs Frecuencia para cada posición', fontsize=16)

        # Graficar cada posición
        axs[0, 0].plot(freq, real_1_1, marker='o', label='Posición (1,1)')
        axs[0, 0].set_title('Posición (1,1)')
        axs[0, 0].set_xlabel('Frecuencia (Hz)')
        axs[0, 0].set_ylabel('Real')
        axs[0, 0].legend()

        axs[0, 1].plot(freq, real_1_2, marker='o', label='Posición (1,2)')
        axs[0, 1].set_title('Posición (1,2)')
        axs[0, 1].set_xlabel('Frecuencia (Hz)')
        axs[0, 1].set_ylabel('Real')
        axs[0, 1].legend()

        axs[1, 0].plot(freq, real_2_1, marker='o', label='Posición (2,1)')
        axs[1, 0].set_title('Posición (2,1)')
        axs[1, 0].set_xlabel('Frecuencia (Hz)')
        axs[1, 0].set_ylabel('Real')
        axs[1, 0].legend()

        axs[1, 1].plot(freq, real_2_2, marker='o', label='Posición (2,2)')
        axs[1, 1].set_title('Posición (2,2)')
        axs[1, 1].set_xlabel('Frecuencia (Hz)')
        axs[1, 1].set_ylabel('Real')
        axs[1, 1].legend()
        
        # Ajustar diseño para evitar superposición
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()
    else:
        ctk.CTkMessagebox.show_info("Error", "Selecciona una matriz válida")

# Función para graficar parte imaginaria de las posiciones (1,1), (1,2), (2,1) y (2,2) de cada matriz
def plot_img(matriz_seleccionada, freq):

    
    if matriz_seleccionada in matrices:
        
        matriz_valores = matrices[matriz_seleccionada]
        
        img_1_1 = [parameter2img(matriz[0, 0]) for matriz in matriz_valores]  
        img_1_2 = [parameter2img(matriz[0, 1]) for matriz in matriz_valores]  
        img_2_1 = [parameter2img(matriz[1, 0]) for matriz in matriz_valores]  
        img_2_2 = [parameter2img(matriz[1, 1]) for matriz in matriz_valores]  
        
        # Crear la figura con subgráficos
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Imaginario vs Frecuencia para cada posición', fontsize=16)

        # Graficar cada posición
        axs[0, 0].plot(freq, img_1_1, marker='o', label='Posición (1,1)')
        axs[0, 0].set_title('Posición (1,1)')
        axs[0, 0].set_xlabel('Frecuencia (Hz)')
        axs[0, 0].set_ylabel('Imaginario')
        axs[0, 0].legend()

        axs[0, 1].plot(freq, img_1_2, marker='o', label='Posición (1,2)')
        axs[0, 1].set_title('Posición (1,2)')
        axs[0, 1].set_xlabel('Frecuencia (Hz)')
        axs[0, 1].set_ylabel('Imaginario')
        axs[0, 1].legend()

        axs[1, 0].plot(freq, img_2_1, marker='o', label='Posición (2,1)')
        axs[1, 0].set_title('Posición (2,1)')
        axs[1, 0].set_xlabel('Frecuencia (Hz)')
        axs[1, 0].set_ylabel('Imaginario')
        axs[1, 0].legend()

        axs[1, 1].plot(freq, img_2_2, marker='o', label='Posición (2,2)')
        axs[1, 1].set_title('Posición (2,2)')
        axs[1, 1].set_xlabel('Frecuencia (Hz)')
        axs[1, 1].set_ylabel('Imaginario')
        axs[1, 1].legend()
        
        # Ajustar diseño para evitar superposición
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()
    else:
        ctk.CTkMessagebox.show_info("Error", "Selecciona una matriz válida")

# Función para graficar las fases de las posiciones (1,1), (1,2), (2,1) y (2,2) de cada matriz en plano polar
def plot_polar(matriz_seleccionada, freq):
    
    if matriz_seleccionada in matrices:
        
        matriz_valores = matrices[matriz_seleccionada]

        fases_1_1 = [parameter2Phase(matriz[0, 0]) for matriz in matriz_valores]  # Fase de la posición (1,1)
        fases_1_2 = [parameter2Phase(matriz[0, 1]) for matriz in matriz_valores]  # Fase de la posición (1,2)
        fases_2_1 = [parameter2Phase(matriz[1, 0]) for matriz in matriz_valores]  # Fase de la posición (2,1)
        fases_2_2 = [parameter2Phase(matriz[1, 1]) for matriz in matriz_valores]  # Fase de la posición (2,2)
 
    # Crear la figura con subgráficos polares
    fig, axs = plt.subplots(2, 2, subplot_kw={'projection': 'polar'}, figsize=(12, 12))
    fig.suptitle('Fases en Coordenadas Polares para cada Posición', fontsize=16)

    # Graficar cada posición en su propio subgráfico
    axs[0, 0].plot(fases_1_1, freq, marker='o', label='Posición (1,1)')
    axs[0, 0].set_title('Posición (1,1)', va='bottom')
    axs[0, 0].legend(loc='upper right')

    axs[0, 1].plot(fases_1_2, freq, marker='o', label='Posición (1,2)')
    axs[0, 1].set_title('Posición (1,2)', va='bottom')
    axs[0, 1].legend(loc='upper right')

    axs[1, 0].plot(fases_2_1, freq, marker='o', label='Posición (2,1)')
    axs[1, 0].set_title('Posición (2,1)', va='bottom')
    axs[1, 0].legend(loc='upper right')

    axs[1, 1].plot(fases_2_2, freq, marker='o', label='Posición (2,2)')
    axs[1, 1].set_title('Posición (2,2)', va='bottom')
    axs[1, 1].legend(loc='upper right')

    # Ajustar el diseño para evitar superposición
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

# Función para graficar las posiciones (1,1), (1,2), (2,1) y (2,2) de cada matriz en Carta de Smith
def plot_smith(matriz_seleccionada, freq):
    
    if matriz_seleccionada in matrices:
        matriz_valores = matrices[matriz_seleccionada]
        
        s_param = np.array(matriz_valores)
    
        frequency = rf.Frequency.from_f(freq, unit='hz')
        network = rf.Network(frequency= frequency, s=s_param)
        
        # Crear una figura con subgráficos de 2x2
        fig, axs = plt.subplots(2, 2, figsize=(12, 12))
        
        # Títulos de las subgráficas para cada parámetro S
        parametros = [
            ("S11", 0, 0, "S11 en Carta de Smith"),
            ("S21", 1, 0, "S21 en Carta de Smith"),
            ("S12", 0, 1, "S12 en Carta de Smith"),
            ("S22", 1, 1, "S22 en Carta de Smith")
        ]

        # Graficar cada parámetro S en su respectivo subgráfico
        for label, m, n, title in parametros:
            ax = axs[m, n]
            network.plot_s_smith(m=m, n=n, ax=ax, label=label)
            ax.set_title(title)
            ax.legend()

        # Ajustar el diseño y la disposición de los subgráficos
        plt.tight_layout()
        plt.show()

    else:
        # Mostrar mensaje de error si la matriz seleccionada no es válida
        ctk.CTkMessagebox.show_info("Error", "Selecciona una matriz válida")

#Función selectora para graficar
def graficar():
    try:
        # Obtener la función seleccionada
        sel_mat_i = combobox_matrices.get()
        sel_plot_i = sel_plot.get()
        
        if sel_mat_i != "Archivo S2P":
            freq_plot = frecuencias
        elif sel_mat_i == "Archivo S2P":
            freq_plot = s2p_freq
            
        # Elegir la función según la selección del usuario
        if sel_mat_i == "Z":
            if sel_plot_i == "Magnitud vs Frecuencia":
                plot_mag(sel_mat_i, freq_plot)
            elif sel_plot_i == "Fase vs Frecuencia":
                plot_Phase(sel_mat_i, freq_plot) 
            elif sel_plot_i == "dB vs Frecuencia":
                plot_dB(sel_mat_i, freq_plot)
            elif sel_plot_i == "Real vs Frecuencia":
                plot_real(sel_mat_i, freq_plot)
            elif sel_plot_i == "Imaginario vs Frecuencia":
                plot_img(sel_mat_i, freq_plot)
            elif sel_plot_i == "Gráfica Polar":
                plot_polar(sel_mat_i, freq_plot)
            elif sel_plot_i == "Carta de Smith":
                messagebox.showerror("Error", "Selecciona una función válida.")
                return
            else:
                messagebox.showerror("Error", "Selecciona una función válida.")
                return
        elif sel_mat_i == "Y":
            if sel_plot_i == "Magnitud vs Frecuencia":
                plot_mag(sel_mat_i, freq_plot)
            elif sel_plot_i == "Fase vs Frecuencia":
                plot_Phase(sel_mat_i, freq_plot) 
            elif sel_plot_i == "db vs Frecuencia":
                plot_dB(sel_mat_i, freq_plot)
            elif sel_plot_i == "Real vs Frecuencia":
                plot_real(sel_mat_i, freq_plot)
            elif sel_plot_i == "Imaginario vs Frecuencia":
                plot_img(sel_mat_i, freq_plot)
            elif sel_plot_i == "Gráfica Polar":
                plot_polar(sel_mat_i, freq_plot)
            elif sel_plot_i == "Carta de Smith":
                messagebox.showerror("Error", "Selecciona una función válida.")
                return
            else:
                messagebox.showerror("Error", "Selecciona una función válida.")
                return
        elif sel_mat_i == "ABCD":
            if sel_plot_i == "Magnitud vs Frecuencia":
                plot_mag(sel_mat_i, freq_plot)
            elif sel_plot_i == "Fase vs Frecuencia":
                plot_Phase(sel_mat_i, freq_plot) 
            elif sel_plot_i == "db vs Frecuencia":
                plot_dB(sel_mat_i, freq_plot)
            elif sel_plot_i == "Real vs Frecuencia":
                plot_real(sel_mat_i, freq_plot)
            elif sel_plot_i == "Imaginario vs Frecuencia":
                plot_img(sel_mat_i, freq_plot)
            elif sel_plot_i == "Gráfica Polar":
                plot_polar(sel_mat_i, freq_plot)
            elif sel_plot_i == "Carta de Smith":
                messagebox.showerror("Error", "Selecciona una función válida.")
                return
            else:
                messagebox.showerror("Error", "Selecciona una función válida.")
                return
        elif sel_mat_i == "S":
            if sel_plot_i == "Magnitud vs Frecuencia":
                plot_mag(sel_mat_i, freq_plot)
            elif sel_plot_i == "Fase vs Frecuencia":
                plot_Phase(sel_mat_i, freq_plot) 
            elif sel_plot_i == "db vs Frecuencia":
                plot_dB(sel_mat_i, freq_plot)
            elif sel_plot_i == "Real vs Frecuencia":
                plot_real(sel_mat_i, freq_plot)
            elif sel_plot_i == "Imaginario vs Frecuencia":
                plot_img(sel_mat_i, freq_plot)
            elif sel_plot_i == "Gráfica Polar":
                plot_polar(sel_mat_i, freq_plot)
            elif sel_plot_i == "Carta de Smith":
                plot_smith(sel_mat_i, freq_plot)
                return
            else:
                messagebox.showerror("Error", "Selecciona una función válida.")
                return
        elif sel_mat_i == "Archivo S2P":
            if sel_plot_i == "Magnitud vs Frecuencia":
                plot_mag(sel_mat_i, freq_plot)
            elif sel_plot_i == "Fase vs Frecuencia":
                plot_Phase(sel_mat_i, freq_plot) 
            elif sel_plot_i == "db vs Frecuencia":
                plot_dB(sel_mat_i, freq_plot)
            elif sel_plot_i == "Real vs Frecuencia":
                plot_real(sel_mat_i, freq_plot)
            elif sel_plot_i == "Imaginario vs Frecuencia":
                plot_img(sel_mat_i, freq_plot)
            elif sel_plot_i == "Gráfica Polar":
                plot_polar(sel_mat_i, freq_plot)
            elif sel_plot_i == "Carta de Smith":
                plot_smith(sel_mat_i, freq_plot)
                return
            else:
                messagebox.showerror("Error", "Selecciona una función válida.")
                return                 
        else:
            messagebox.showerror("Error", "Selecciona una función válida.")
            return    
    except Exception as e:
        messagebox.showerror("Error", f"Hubo un error al graficar: {e}")


# Lista de frecuencias
frecuencias = [1e6, 5e6, 10e6, 50e6, 100e6]  # Frecuencias en Hz

# Diccionario de matrices dependientes de frecuencia
matrices = {
    "Z": [np.array([[1 + 1j * f, 2 + 0.5j * f], [3 - 0.5j * f, 4 + 1j * f]]) for f in frecuencias],
    "Y": [np.array([[0.5 - 0.2j * f, 1.5 + 0.3j * f], [-0.5 + 0.7j * f, 0.7 - 0.4j * f]]) for f in frecuencias],
    "ABCD": [np.array([[2 + 0.5j * f, 1 - 0.3j * f], [-1 + 0.2j * f, 3 - 0.6j * f]]) for f in frecuencias],
    "S": [np.array([[2 + 0.5j * f, 1 - 0.3j * f], [-1 + 0.2j * f, 3 - 0.6j * f]]) for f in frecuencias],
}

#Archivo s2p
filename = 'Line.s2p'
s2p_freq, s2p_params, z_ref = read_s2p(filename)

#Agregar archivo s2p al diccionario de matrices
matrices['Archivo S2P'] = s2p_params

# Configuración de customtkinter
ctk.set_appearance_mode("Dark")  # Modo de apariencia: "Light", "Dark", "System"
ctk.set_default_color_theme("dark-blue")  # Tema de color: "blue", "green", "dark-blue"

# Crear la ventana principal
ventana_4 = ctk.CTk()
ventana_4.title("Resultados")
ventana_4.geometry("400x300")

# Etiqueta informativa
etiqueta = ctk.CTkLabel(ventana_4, text="Selecciona una matriz y la acción que desea realizar. Si desea graficar, seleccione también el tipo de gráfica")
etiqueta.pack(pady=10)

# Combobox para seleccionar la matriz
combobox_matrices = ctk.CTkComboBox(ventana_4, values=list(matrices.keys()))
combobox_matrices.set(list(matrices.keys())[0])  # Seleccionar la primera opción por defecto
combobox_matrices.pack(pady=10)

# Crear un combobox (selector) para elegir el tipo de gráfica
sel_plot = ctk.CTkComboBox(
    ventana_4,
    values=["Magnitud vs Frecuencia", "Fase vs Frecuencia", 
            "dB vs Frecuencia", "Real vs Frecuencia", 
            "Imaginario vs Frecuencia", "Gráfica Polar", "Carta de Smith"]
)
sel_plot.set("Magnitud vs Frecuencia")  # Valor predeterminado
sel_plot.pack(pady=10)

# Botón para graficar
boton_graficar = ctk.CTkButton(ventana_4, text="Graficar", command=graficar)
boton_graficar.pack(pady=20)

# Botón para mostrar la matriz seleccionada
boton_mostrar = ctk.CTkButton(ventana_4, text="Mostrar Matriz", command=mostrar)
boton_mostrar.pack(pady=20)

# Iniciar la GUI
ventana_4.mainloop()

