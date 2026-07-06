import tkinter as tk
from tkinter import ttk, messagebox
import random

# =====================================================================
# CONFIGURACIÓN LÓGICA DE LA RULETA (Americana: 38 casillas)
# =====================================================================
NUMEROS_ROJOS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
NUMEROS_NEGROS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

def obtener_color(numero_str):
    if numero_str in ["0", "00"]:
        return "Verde"
    elif int(numero_str) in NUMEROS_ROJOS:
        return "Rojo"
    else:
        return "Negro"

def es_par(numero_str):
    if numero_str in ["0", "00"]:
        return None
    return int(numero_str) % 2 == 0


# =====================================================================
# INTERFAZ GRÁFICA PRINCIPAL DEL JUEGO
# =====================================================================
class SimuladorRuleta:
    def __init__(self, root):
        self.root = root
        self.root.title("Casino Simulador - Ruleta Americana")
        self.root.geometry("680x560")
        self.root.resizable(False, False)
        
        # Estado del jugador
        self.capital = 500.0
        self.historial_tiros = []
        
        # --- ESTILOS DE LA INTERFAZ ---
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 11))
        self.style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        self.style.configure("Capital.TLabel", font=("Arial", 16, "bold"), foreground="#27ae60")
        
        # --- PANEL SUPERIOR: Estado Económico ---
        self.frame_top = ttk.LabelFrame(self.root, text=" Estado del Jugador ", padding=15)
        self.frame_top.pack(pady=10, padx=15, fill=tk.X)
        
        ttk.Label(self.frame_top, text="Capital Disponible:").pack(side=tk.LEFT, padx=5)
        self.lbl_capital = ttk.Label(self.frame_top, text=f"${self.capital:.2f}", style="Capital.TLabel")
        self.lbl_capital.pack(side=tk.LEFT, padx=5)
        
        # --- PANEL CENTRAL: Configuración de la Apuesta ---
        self.frame_apuesta = ttk.LabelFrame(self.root, text=" Realizar Apuesta ", padding=15)
        self.frame_apuesta.pack(pady=10, padx=15, fill=tk.X)
        
        # Cantidad de dinero a apostar
        ttk.Label(self.frame_apuesta, text="Cantidad a apostar ($):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_monto = ttk.Entry(self.frame_apuesta, width=15, font=("Arial", 11))
        self.entry_monto.grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        self.entry_monto.insert(0, "50") # Apuesta inicial por defecto
        
        # Tipo de apuesta
        ttk.Label(self.frame_apuesta, text="Tipo de Apuesta:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.tipos_apuesta = ["A Color: Rojo", "A Color: Negro", "A Par / Impar: Par", "A Par / Impar: Impar"]
        self.combo_tipo = ttk.Combobox(self.frame_apuesta, values=self.tipos_apuesta, state="readonly", width=25, font=("Arial", 10))
        self.combo_tipo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        self.combo_tipo.current(0)
        
        # Botón Girar
        self.btn_girar = tk.Button(self.frame_apuesta, text="¡GIRAR RULETA!", font=("Arial", 12, "bold"), bg="#c0392b", fg="white", command=self.girar_ruleta, relief=tk.RAISED, bd=3)
        self.btn_girar.grid(row=0, column=2, rowspan=2, padx=25, pady=5, sticky=tk.NSEW)
        
        # --- PANEL INFERIOR: Resultados de la tirada ---
        self.frame_resultado = ttk.LabelFrame(self.root, text=" Resultado de la Tirada ", padding=15)
        self.frame_resultado.pack(pady=10, padx=15, fill=tk.X)
        
        self.lbl_bola = tk.Label(self.frame_resultado, text="--", font=("Arial", 36, "bold"), bg="#34495e", fg="white", width=4, height=1, relief=tk.SUNKEN)
        self.lbl_bola.pack(side=tk.LEFT, padx=15)
        
        self.lbl_detalle = ttk.Label(self.frame_resultado, text="¡Haz tu apuesta y gira la ruleta para comenzar!", font=("Arial", 12, "italic"))
        self.lbl_detalle.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # --- PANEL HISTORIAL ---
        self.frame_historial = ttk.LabelFrame(self.root, text=" Historial de Giros ", padding=10)
        self.frame_historial.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        
        self.txt_historial = tk.Text(self.frame_historial, height=6, font=("Courier", 10), state="disabled")
        self.txt_historial.pack(fill=tk.BOTH, expand=True)

    def girar_ruleta(self):
        # 1. Validaciones de entrada de dinero
        try:
            monto_apuesta = float(self.entry_monto.get())
            if monto_apuesta <= 0:
                raise ValueError
            if monto_apuesta > self.capital:
                messagebox.showwarning("Fondos Insuficientes", "No tienes suficiente capital para realizar esa apuesta.")
                return
        except ValueError:
            messagebox.showerror("Error de Apuesta", "Por favor ingresa un monto numérico válido y mayor a 0.")
            return
            
        # 2. Generar la lista de opciones de la Ruleta Americana
        # Números del 0 al 36 más el '00'
        opciones_ruleta = [str(i) for i in range(37)] + ["00"]
        
        # Simular la aleatoriedad eligiendo un número al azar de la ruleta
        numero_ganador = random.choice(opciones_ruleta)
        color_ganador = obtener_color(numero_ganador)
        paridad_ganador = es_par(numero_ganador)
        
        # 3. Actualizar interfaz visual del número de la bola
        bg_color = "#27ae60" if color_ganador == "Verde" else ("#c0392b" if color_ganador == "Rojo" else "#2c3e50")
        self.lbl_bola.config(text=numero_ganador, bg=bg_color)
        
        # 4. Determinar si el jugador gana o pierde
        tipo_seleccionado = self.combo_tipo.get()
        gano = False
        
        if tipo_seleccionado == "A Color: Rojo" and color_ganador == "Rojo":
            gano = True
        elif tipo_seleccionado == "A Color: Negro" and color_ganador == "Negro":
            gano = True
        elif tipo_seleccionado == "A Par / Impar: Par" and paridad_ganador is True:
            gano = True
        elif tipo_seleccionado == "A Par / Impar: Impar" and paridad_ganador is False:
            gano = True
            
        # 5. Modificar el capital basado en el resultado
        if gano:
            # Duplica la apuesta: recuperas lo tuyo y ganas el equivalente
            self.capital += monto_apuesta
            msg_resultado = f"¡GANASTE! El número es {numero_ganador} ({color_ganador}). Ganaste ${monto_apuesta:.2f}"
            detalle_color = "#27ae60"
        else:
            self.capital -= monto_apuesta
            msg_resultado = f"¡PERDISTE! El número es {numero_ganador} ({color_ganador}). Perdiste ${monto_apuesta:.2f}"
            detalle_color = "#c0392b"
            
        # Actualizar etiquetas de texto principales
        self.lbl_capital.config(text=f"${self.capital:.2f}")
        self.lbl_detalle.config(text=msg_resultado, foreground=detalle_color)
        
        # 6. Guardar en el cuadro de historial técnico
        paridad_str = "Par" if paridad_ganador is True else ("Impar" if paridad_ganador is False else "Cero")
        registro = f"Giro: [{numero_ganador.zfill(2)} - {color_ganador.upper()} - {paridad_str}] | Apostó: ${monto_apuesta:.2f} a '{tipo_seleccionado}' -> Capital: ${self.capital:.2f}\n"
        self.historial_tiros.insert(0, registro) # Inserta al principio
        
        self.txt_historial.config(state="normal")
        self.txt_historial.delete("1.0", tk.END)
        self.txt_historial.insert(tk.END, "".join(self.historial_tiros))
        self.txt_historial.config(state="disabled")
        
        # Fin de juego si se queda sin dinero
        if self.capital <= 0:
            messagebox.showinfo("Bancarrota", "Te has quedado sin dinero. El casino siempre gana. ¡Vuelve a abrir para reiniciar!")
            self.btn_girar.config(state="disabled")

# =====================================================================
# ARRANQUE DE LA APLICACIÓN
# =====================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorRuleta(root)
    root.mainloop()