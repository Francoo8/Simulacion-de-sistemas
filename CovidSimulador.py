import tkinter as tk
from tkinter import ttk, messagebox
import random

# Librerías para el gráfico de evolución temporal (Requisito 2 y 5)
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# =====================================================================
# CONSTANTES DEL AUTÓMATA CELULAR (REQUISITO 6: REGLAS DE ESTADO)
# =====================================================================
VACIO = 0       # Espacio vacío / Persona Inmunizada (Bloquea el virus)
SANO = 1        # Persona sana susceptible
INFECTADO = 2   # Persona infectada activa
RECUPERADO = 3  # Persona recuperada con inmunidad natural
FALLECIDO = 4   # Persona fallecida

COLORES = {
    VACIO: "#34495e",       # Azul Oscuro
    SANO: "#bdc3c7",        # Gris
    INFECTADO: "#e74c3c",   # Rojo
    RECUPERADO: "#2ecc71",  # Verde
    FALLECIDO: "#000000"    # Negro
}

class SimuladorCOVIDCompleto:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Propagación COVID-19 - Autómatas Celulares")
        self.root.geometry("1180x750")
        self.root.resizable(False, False)
        
        # Variables lógicas de control
        self.corriendo = False
        self.generacion = 0
        self.matriz = []
        self.tiempo_enfermo = []
        
        # Historiales para la gráfica de evolución temporal (Requisito 5)
        self.hist_dias = []
        self.hist_sanos = []
        self.hist_infectados = []
        self.hist_recuperados = []
        self.hist_muertos = []
        
        self.configurar_interfaz_grafica()
        self.inicializar_grafica_matplotlib()
        self.crear_nuevo_escenario()

    def configurar_interfaz_grafica(self):
        """Cumple con el Requisito 2: Interfaz gráfica interactiva y robusta."""
        self.panel_izquierdo = ttk.Frame(self.root, padding=12)
        self.panel_izquierdo.pack(side=tk.LEFT, fill=tk.Y)
        
        self.panel_derecho = ttk.Frame(self.root, padding=12)
        self.panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # --- PANEL DE PARÁMETROS CONFIGURABLES (REQUISITO 4) ---
        frame_config = ttk.LabelFrame(self.panel_izquierdo, text=" Configuración de Parámetros ", padding=10)
        frame_config.pack(fill=tk.X, pady=5)
        
        # Tamaño de la cuadrícula
        ttk.Label(frame_config, text="Tamaño de la Cuadrícula (N x N):", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.scale_dimension = tk.Scale(frame_config, from_=15, to=40, orient=tk.HORIZONTAL, command=lambda e: self.crear_nuevo_escenario())
        self.scale_dimension.set(25)
        self.scale_dimension.pack(fill=tk.X, pady=2)
        
        # Número inicial de infectados
        ttk.Label(frame_config, text="Infectados Iniciales (% de población):").pack(anchor=tk.W, pady=(5,0))
        self.scale_inf_ini = tk.Scale(frame_config, from_=1, to=25, orient=tk.HORIZONTAL)
        self.scale_inf_ini.set(5)
        self.scale_inf_ini.pack(fill=tk.X, pady=2)
        
        # Espacios vacíos / Inmunes
        ttk.Label(frame_config, text="Espacios Vacíos / Vacunados (%):").pack(anchor=tk.W, pady=(5,0))
        self.scale_vacios = tk.Scale(frame_config, from_=0, to=40, orient=tk.HORIZONTAL)
        self.scale_vacios.set(10)
        self.scale_vacios.pack(fill=tk.X, pady=2)
        
        # Probabilidad de contagio
        ttk.Label(frame_config, text="Probabilidad de Contagio (0.0 - 1.0):").pack(anchor=tk.W, pady=(5,0))
        self.entry_p_contagio = ttk.Entry(frame_config)
        self.entry_p_contagio.pack(fill=tk.X, pady=2)
        self.entry_p_contagio.insert(0, "0.30")
        
        # Tiempo de recuperación
        ttk.Label(frame_config, text="Tiempo de Recuperación (Días / Pasos):").pack(anchor=tk.W, pady=(5,0))
        self.entry_t_recup = ttk.Entry(frame_config)
        self.entry_t_recup.pack(fill=tk.X, pady=2)
        self.entry_t_recup.insert(0, "6")
        
        # Probabilidad de fallecimiento
        ttk.Label(frame_config, text="Probabilidad de Fallecimiento (0.0 - 1.0):").pack(anchor=tk.W, pady=(5,0))
        self.entry_p_muerte = ttk.Entry(frame_config)
        self.entry_p_muerte.pack(fill=tk.X, pady=2)
        self.entry_p_muerte.insert(0, "0.03")

        # --- BOTONES DE CONTROL ---
        frame_botones = ttk.Frame(self.panel_izquierdo, padding=5)
        frame_botones.pack(fill=tk.X, pady=5)
        
        self.btn_generar = ttk.Button(frame_botones, text="Reiniciar / Aplicar Parámetros", command=self.crear_nuevo_escenario)
        self.btn_generar.pack(fill=tk.X, pady=3)
        
        self.btn_play = ttk.Button(frame_botones, text="Iniciar Simulación", command=self.toggle_simulacion)
        self.btn_play.pack(fill=tk.X, pady=3)
        
        self.btn_paso = ttk.Button(frame_botones, text="Avanzar 1 Día", command=self.avanzar_un_ciclo)
        self.btn_paso.pack(fill=tk.X, pady=3)

        # --- PANEL DE RESULTADOS EN TIEMPO REAL (REQUISITO 5) ---
        self.frame_resultados = ttk.LabelFrame(self.panel_izquierdo, text=" Resultados en Tiempo Real ", padding=10)
        self.frame_resultados.pack(fill=tk.X, pady=10)
        
        self.lbl_dia = ttk.Label(self.frame_resultados, text="Días Simulados: 0", font=("Arial", 10, "bold"))
        self.lbl_dia.pack(anchor=tk.W, pady=3)
        self.lbl_sanos = ttk.Label(self.frame_resultados, text="Personas Sanas: 0", foreground="#7f8c8d", font=("Arial", 9, "bold"))
        self.lbl_sanos.pack(anchor=tk.W, pady=1)
        self.lbl_infectados = ttk.Label(self.frame_resultados, text="Personas Infectadas: 0", foreground="#c0392b", font=("Arial", 9, "bold"))
        self.lbl_infectados.pack(anchor=tk.W, pady=1)
        self.lbl_recuperados = ttk.Label(self.frame_resultados, text="Personas Recuperadas: 0", foreground="#27ae60", font=("Arial", 9, "bold"))
        self.lbl_recuperados.pack(anchor=tk.W, pady=1)
        self.lbl_muertos = ttk.Label(self.frame_resultados, text="Personas Fallecidas: 0", foreground="#000000", font=("Arial", 9, "bold"))
        self.lbl_muertos.pack(anchor=tk.W, pady=1)

        # --- REQUISITO 3: TABLERO VISUAL (CANVAS) ---
        self.canvas_celdas = tk.Canvas(self.panel_derecho, bg="#2c3e50", bd=2, relief=tk.RIDGE)
        self.canvas_celdas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

    def inicializar_grafica_matplotlib(self):
        """Cumple con el Requisito 5: Mostrar la evolución de los contagios durante el tiempo."""
        self.fig, self.ax = plt.subplots(figsize=(5, 2.4))
        self.fig.patch.set_facecolor('#f4f6f7')
        self.ax.set_facecolor('#ffffff')
        
        self.canvas_grafica = FigureCanvasTkAgg(self.fig, master=self.panel_derecho)
        self.canvas_grafica.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    def crear_nuevo_escenario(self):
        """Inicializa dinámicamente el tamaño de la población basándose en la configuración."""
        if self.corriendo:
            self.toggle_simulacion()
            
        self.dimension = self.scale_dimension.get()
        self.tamano_celda = min(460 // self.dimension, 25)
        
        self.canvas_celdas.config(width=self.dimension * self.tamano_celda, height=self.dimension * self.tamano_celda)
        
        p_inf = self.scale_inf_ini.get() / 100.0
        p_vac = self.scale_vacios.get() / 100.0
        
        # Generación de la cuadrícula de Autómatas Celulares
        self.matriz = [[SANO for _ in range(self.dimension)] for _ in range(self.dimension)]
        self.tiempo_enfermo = [[0 for _ in range(self.dimension)] for _ in range(self.dimension)]
        
        for f in range(self.dimension):
            for c in range(self.dimension):
                prob = random.random()
                if prob < p_inf:
                    self.matriz[f][c] = INFECTADO
                    self.tiempo_enfermo[f][c] = 1
                elif prob < (p_inf + p_vac):
                    self.matriz[f][c] = VACIO

        self.generacion = 0
        
        # Resetear vectores para las curvas epidemiológicas
        self.hist_dias = [0]
        self.hist_sanos = []
        self.hist_infectados = []
        self.hist_recuperados = []
        self.hist_muertos = []
        
        self.redibujar_tablero_visual()
        self.actualizar_censo_y_grafico()

    def redibujar_tablero_visual(self):
        self.canvas_celdas.delete("all")
        for f in range(self.dimension):
            for c in range(self.dimension):
                x1 = c * self.tamano_celda
                y1 = f * self.tamano_celda
                x2 = x1 + self.tamano_celda
                y2 = y1 + self.tamano_celda
                
                estado = self.matriz[f][c]
                self.canvas_celdas.create_rectangle(x1, y1, x2, y2, fill=COLORES[estado], outline="#34495e")

    def contar_vecinos_infectados(self, f, c):
        """Vecindad de Moore (8 celdas adyacentes locales)"""
        enfermos = 0
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0:
                    continue
                nf, nc = f + i, c + j
                if 0 <= nf < self.dimension and 0 <= nc < self.dimension:
                    if self.matriz[nf][nc] == INFECTADO:
                        enfermos += 1
        return enfermos

    def avanzar_un_turno_logico(self, p_contagio, t_recup, p_muerte):
        """Mapeo del Requisito 6: Reglas de transición matemática local."""
        nueva_matriz = [[SANO for _ in range(self.dimension)] for _ in range(self.dimension)]
        nuevo_tiempo = [[0 for _ in range(self.dimension)] for _ in range(self.dimension)]
        
        for f in range(self.dimension):
            for c in range(self.dimension):
                estado_actual = self.matriz[f][c]
                
                if estado_actual in [VACIO, FALLECIDO, RECUPERADO]:
                    # Estados absorbentes o estables permanentes
                    nueva_matriz[f][c] = estado_actual
                    
                elif estado_actual == INFECTADO:
                    # Regla: Puede fallecer según la probabilidad definida
                    if random.random() < p_muerte:
                        nueva_matriz[f][c] = FALLECIDO
                    else:
                        dias_cursados = self.tiempo_enfermo[f][c]
                        # Regla: Se recupera después de cierto número de días
                        if dias_cursados >= t_recup:
                            nueva_matriz[f][c] = RECUPERADO
                        else:
                            nueva_matriz[f][c] = INFECTADO
                            nuevo_tiempo[f][c] = dias_cursados + 1
                            
                elif estado_actual == SANO:
                    # Regla: Se infecta si se encuentra cerca de vecinos infectados
                    enfermos = self.contar_vecinos_infectados(f, c)
                    if enfermos > 0:
                        prob_contagio_total = 1 - (1 - p_contagio) ** enfermos
                        if random.random() < prob_contagio_total:
                            nueva_matriz[f][c] = INFECTADO
                            nuevo_tiempo[f][c] = 1
                        else:
                            nueva_matriz[f][c] = SANO
                    else:
                        nueva_matriz[f][c] = SANO
                        
        self.matriz = nueva_matriz
        self.tiempo_enfermo = nuevo_tiempo
        self.generacion += 1

    def avanzar_un_ciclo(self):
        # Validación estricta de parámetros ingresados para evitar caídas del programa
        try:
            p_contagio = float(self.entry_p_contagio.get())
            t_recup = int(self.entry_t_recup.get())
            p_muerte = float(self.entry_p_muerte.get())
            
            if not (0 <= p_contagio <= 1) or t_recup <= 0 or not (0 <= p_muerte <= 1):
                raise ValueError
        except ValueError:
            if self.corriendo:
                self.toggle_simulacion()
            messagebox.showerror("Error en Parámetros", "Verifique que las probabilidades estén entre 0.0 y 1.0, y los días de recuperación sean un entero mayor a 0.")
            return

        self.avanzar_un_turno_logico(p_contagio, t_recup, p_muerte)
        self.redibujar_tablero_visual()
        self.actualizar_censo_y_grafico()

    def actualizar_censo_y_grafico(self):
        sanos = sum(fila.count(SANO) for fila in self.matriz)
        infectados = sum(fila.count(INFECTADO) for fila in self.matriz)
        recuperados = sum(fila.count(RECUPERADO) for fila in self.matriz)
        muertos = sum(fila.count(FALLECIDO) for fila in self.matriz)
        
        # Actualizar textos del Censo (Requisito 5)
        self.lbl_dia.config(text=f"Días Simulados (Iteraciones): {self.generacion}")
        self.lbl_sanos.config(text=f"Personas Sanas: {sanos}")
        self.lbl_infectados.config(text=f"Personas Infectadas: {infectados}")
        self.lbl_recuperados.config(text=f"Personas Recuperadas: {recuperados}")
        self.lbl_muertos.config(text=f"Personas Fallecidas: {muertos}")
        
        # Insertar registros analíticos en el tiempo
        if len(self.hist_sanos) < self.generacion + 1:
            self.hist_sanos.append(sanos)
            self.hist_infectados.append(infectados)
            self.hist_recuperados.append(recuperados)
            self.hist_muertos.append(muertos)
            
        # Actualización de curvas matemáticas en el objeto de Matplotlib
        self.ax.clear()
        dias = range(len(self.hist_infectados))
        self.ax.plot(dias, self.hist_sanos, color='#7f8c8d', label='Sanas')
        self.ax.plot(dias, self.hist_infectados, color='#e74c3c', label='Infectadas')
        self.ax.plot(dias, self.hist_recuperados, color='#2ecc71', label='Recuperadas')
        self.ax.plot(dias, self.hist_muertos, color='#000000', label='Fallecidas')
        
        self.ax.set_title("Evolución Temporal de las Curvas Epidemiológicas", fontsize=9, fontweight="bold")
        self.ax.set_ylabel("Cantidad de Celdas", fontsize=8)
        self.ax.set_xlabel("Iteraciones (Días)", fontsize=8)
        self.ax.legend(loc='upper right', fontsize=7)
        self.ax.grid(True, linestyle=':', alpha=0.6)
        self.fig.tight_layout()
        self.canvas_grafica.draw()
        
        # Parada automática inteligente
        if infectados == 0 and self.corriendo:
            self.toggle_simulacion()
            messagebox.showinfo("Brote Finalizado", f"La simulación se detuvo en el día {self.generacion}. No quedan vectores activos de contagio.")

    def bucle_tiempo(self):
        if self.corriendo:
            self.avanzar_un_ciclo()
            self.root.after(350, self.bucle_tiempo)

    def toggle_simulacion(self):
        self.corriendo = not self.corriendo
        if self.corriendo:
            self.btn_play.config(text="Pausar Simulación")
            self.bucle_tiempo()
        else:
            self.btn_play.config(text="Iniciar Simulación")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorCOVIDCompleto(root)
    root.mainloop()