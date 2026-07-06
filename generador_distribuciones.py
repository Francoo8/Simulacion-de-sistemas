import tkinter as tk
from tkinter import ttk, messagebox
import random
import numpy as np
import math

# Librerías para integrar gráficos en la interfaz de Tkinter
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# =====================================================================
# ALGORITMOS DE GENERACIÓN DE NÚMEROS PSEUDOALEATORIOS (ri)
# =====================================================================
def generar_cuadrados_medios(semilla, cantidad):
    lista_ri = []
    x_actual = semilla
    d = len(str(semilla))
    
    for _ in range(cantidad):
        cuadrado = x_actual ** 2
        cadena_cuadrado = str(cuadrado)
        
        longitud_esperada = 2 * d
        if len(cadena_cuadrado) < longitud_esperada:
            cadena_cuadrado = cadena_cuadrado.zfill(longitud_esperada)
            
        inicio = (len(cadena_cuadrado) - d) // 2
        fin = inicio + d
        centro = cadena_cuadrado[inicio:fin]
        
        x_actual = int(centro)
        ri = x_actual / (10 ** d)
        lista_ri.append(ri)
        
    return lista_ri


# =====================================================================
# INTERFAZ GRÁFICA PRINCIPAL
# =====================================================================
class CalculadoraSimulacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Simulación y Modelos")
        self.root.geometry("1050x750")
        
        # --- PANEL IZQUIERDO: Configuración y Datos ---
        self.panel_izquierdo = ttk.Frame(self.root, padding=10)
        self.panel_izquierdo.pack(side=tk.LEFT, fill=tk.Y)
        
        # 1. Configuración del Generador de Números Pseudoaleatorios (ri)
        lbl_gen = ttk.Label(self.panel_izquierdo, text="1. Generador de Base (ri)", font=("Arial", 11, "bold"))
        lbl_gen.pack(pady=(5, 2), anchor=tk.W)
        
        self.combo_gen = ttk.Combobox(self.panel_izquierdo, values=["Nativo de Python", "Cuadrados Medios"], state="readonly", width=28)
        self.combo_gen.pack(pady=2)
        self.combo_gen.current(0)
        self.combo_gen.bind("<<ComboboxSelected>>", self.toggle_campos_generador)
        
        # Frame para la semilla
        self.frame_semilla = ttk.Frame(self.panel_izquierdo)
        ttk.Label(self.frame_semilla, text="Semilla (X0 de 4 dígitos):").pack(side=tk.LEFT, padx=2)
        self.entry_seed = ttk.Entry(self.frame_semilla, width=10)
        self.entry_seed.pack(side=tk.LEFT, padx=2)
        self.entry_seed.insert(0, "3708")
        
        # 2. Configuración de la Distribución de Probabilidad (Continuas y Discretas)
        self.lbl_menu = ttk.Label(self.panel_izquierdo, text="2. Distribución a Simular", font=("Arial", 11, "bold"))
        self.lbl_menu.pack(pady=(15, 2), anchor=tk.W)
        
        self.opciones_dist = [
            "Distribución Uniforme (Continua)", 
            "Distribución Exponencial",
            "Distribución k-Erlang",
            "Distribución Normal",
            "Distribución Uniforme Discreta",
            "Distribución Bernoulli",
            "Distribución Binomial"
        ]
        self.combo_dist = ttk.Combobox(self.panel_izquierdo, values=self.opciones_dist, state="readonly", width=28)
        self.combo_dist.pack(pady=2)
        self.combo_dist.current(0) 
        self.combo_dist.bind("<<ComboboxSelected>>", self.cambiar_interfaz_dinamica)
        
        # Contenedor dinámico para parámetros específicos de las variables
        self.frame_variables = ttk.LabelFrame(self.panel_izquierdo, text=" Parámetros de Entrada ", padding=10)
        self.frame_variables.pack(pady=15, fill=tk.X)
        
        # Botón principal para ejecutar cálculos
        self.btn_calcular = ttk.Button(self.panel_izquierdo, text="Generar, Probar y Graficar", command=self.ejecutar_simulacion)
        self.btn_calcular.pack(pady=10, fill=tk.X)
        
        # --- PANEL DERECHO: Histograma y Resultados ---
        self.panel_derecho = ttk.Frame(self.root, padding=10)
        self.panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Canvas de Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(5, 3.5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.panel_derecho)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Panel Inferior de Reportes Estadísticos
        self.frame_reporte = ttk.LabelFrame(self.panel_derecho, text=" Reporte de Pruebas Estadísticas (95% Confianza) ", padding=10)
        self.frame_reporte.pack(fill=tk.BOTH, expand=False, pady=(10, 0))
        
        self.txt_reporte = tk.Text(self.frame_reporte, height=8, width=50, font=("Courier", 10), state="disabled")
        self.txt_reporte.pack(fill=tk.BOTH, expand=True)
        
        self.cambiar_interfaz_dinamica(None)

    def toggle_campos_generador(self, event):
        if self.combo_gen.get() == "Cuadrados Medios":
            self.frame_semilla.pack(pady=5, fill=tk.X, before=self.lbl_menu)
        else:
            self.frame_semilla.pack_forget()

    def cambiar_interfaz_dinamica(self, event):
        for widget in self.frame_variables.winfo_children():
            widget.destroy()
            
        seleccion = self.combo_dist.get()
        
        ttk.Label(self.frame_variables, text="Cantidad de simulaciones (N):").pack(anchor=tk.W)
        self.entry_n = ttk.Entry(self.frame_variables)
        self.entry_n.pack(pady=2, fill=tk.X)
        self.entry_n.insert(0, "1000")
        
        if seleccion in ["Distribución Uniforme (Continua)", "Distribución Uniforme Discreta"]:
            ttk.Label(self.frame_variables, text="Parámetro a (Mínimo):").pack(anchor=tk.W)
            self.entry_a = ttk.Entry(self.frame_variables)
            self.entry_a.pack(pady=2, fill=tk.X)
            self.entry_a.insert(0, "10")
            
            ttk.Label(self.frame_variables, text="Parámetro b (Máximo):").pack(anchor=tk.W)
            self.entry_b = ttk.Entry(self.frame_variables)
            self.entry_b.pack(pady=2, fill=tk.X)
            self.entry_b.insert(0, "50")
            
        elif seleccion == "Distribución Exponencial":
            ttk.Label(self.frame_variables, text="Parámetro Lambda (λ):").pack(anchor=tk.W)
            self.entry_lambda = ttk.Entry(self.frame_variables)
            self.entry_lambda.pack(pady=2, fill=tk.X)
            self.entry_lambda.insert(0, "2.0")
            
        elif seleccion == "Distribución k-Erlang":
            ttk.Label(self.frame_variables, text="Parámetro k (Entero de forma):").pack(anchor=tk.W)
            self.entry_k = ttk.Entry(self.frame_variables)
            self.entry_k.pack(pady=2, fill=tk.X)
            self.entry_k.insert(0, "3")
            
            ttk.Label(self.frame_variables, text="Parámetro Lambda (λ):").pack(anchor=tk.W)
            self.entry_lambda_er = ttk.Entry(self.frame_variables)
            self.entry_lambda_er.pack(pady=2, fill=tk.X)
            self.entry_lambda_er.insert(0, "0.5")
            
        elif seleccion == "Distribución Normal":
            ttk.Label(self.frame_variables, text="Media (μ):").pack(anchor=tk.W)
            self.entry_mu = ttk.Entry(self.frame_variables)
            self.entry_mu.pack(pady=2, fill=tk.X)
            self.entry_mu.insert(0, "100")
            
            ttk.Label(self.frame_variables, text="Desviación Estándar (σ):").pack(anchor=tk.W)
            self.entry_sigma = ttk.Entry(self.frame_variables)
            self.entry_sigma.pack(pady=2, fill=tk.X)
            self.entry_sigma.insert(0, "15")
            
        elif seleccion == "Distribución Bernoulli":
            ttk.Label(self.frame_variables, text="Probabilidad de éxito (p):").pack(anchor=tk.W)
            self.entry_p_bern = ttk.Entry(self.frame_variables)
            self.entry_p_bern.pack(pady=2, fill=tk.X)
            self.entry_p_bern.insert(0, "0.6")
            
        elif seleccion == "Distribución Binomial":
            ttk.Label(self.frame_variables, text="Número de ensayos (n):").pack(anchor=tk.W)
            self.entry_n_binom = ttk.Entry(self.frame_variables)
            self.entry_n_binom.pack(pady=2, fill=tk.X)
            self.entry_n_binom.insert(0, "10")
            
            ttk.Label(self.frame_variables, text="Probabilidad de éxito (p):").pack(anchor=tk.W)
            self.entry_p_binom = ttk.Entry(self.frame_variables)
            self.entry_p_binom.pack(pady=2, fill=tk.X)
            self.entry_p_binom.insert(0, "0.5")

    def realizar_pruebas_estadisticas(self, ri):
        n = len(ri)
        z_critico = 1.96
        
        media_muestral = sum(ri) / n
        media_esperada = 0.5
        varianza_esperada = 1/12
        
        z_promedios = ((media_muestral - media_esperada) * math.sqrt(n)) / math.sqrt(varianza_esperada)
        pasa_promedio = abs(z_promedios) < z_critico
        
        suma_cuadrados = sum((r - media_muestral) ** 2 for r in ri)
        varianza_muestral = suma_cuadrados / (n - 1) if n > 1 else 0
        
        sigma_varianza = math.sqrt(7 / (120 * n))
        z_varianza = (varianza_muestral - varianza_esperada) / sigma_varianza
        pasa_varianza = abs(z_varianza) < z_critico
        
        reporte =  "============= RESULTADOS DE VALIDACIÓN (ri) =============\n"
        reporte += f"Cantidad total de números base generados: {n}\n\n"
        reporte += f"1. PRUEBA DE PROMEDIOS:\n"
        reporte += f"   - Media Muestral: {media_muestral:.4f} (Esperada: 0.5000)\n"
        reporte += f"   - Estadístico Z:  {z_promedios:.4f} (Límite: ±1.96)\n"
        reporte += f"   - CONCLUSIÓN:     {'PASÓ' if pasa_promedio else 'RECHAZADO'} la prueba de uniformidad.\n\n"
        reporte += f"2. PRUEBA DE VARIANZA:\n"
        reporte += f"   - Varianza Muestral: {varianza_muestral:.4f} (Esperada: {varianza_esperada:.4f})\n"
        reporte += f"   - Estadístico Z:     {z_varianza:.4f} (Límite: ±1.96)\n"
        reporte += f"   - CONCLUSIÓN:        {'PASÓ' if pasa_varianza else 'RECHAZADO'} la prueba de variabilidad.\n"
        reporte += "========================================================="
        
        self.txt_reporte.config(state="normal")
        self.txt_reporte.delete("1.0", tk.END)
        self.txt_reporte.insert(tk.END, reporte)
        self.txt_reporte.config(state="disabled")

    def ejecutar_simulacion(self):
        try:
            n_simulaciones = int(self.entry_n.get())
            metodo_ri = self.combo_gen.get()
            seleccion_dist = self.combo_dist.get()
            
            # --- CÁCULO DE CANTIDAD DE RI REQUERIDOS ---
            if seleccion_dist == "Distribución k-Erlang":
                k_val = int(self.entry_k.get())
                n_ri_necesarios = n_simulaciones * k_val 
            elif seleccion_dist == "Distribución Normal":
                n_ri_necesarios = n_simulaciones * 12 
            elif seleccion_dist == "Distribución Binomial":
                n_ensayos = int(self.entry_n_binom.get())
                n_ri_necesarios = n_simulaciones * n_ensayos
            else:
                n_ri_necesarios = n_simulaciones
                
            # 1. GENERAR LOS RI BASE
            if metodo_ri == "Nativo de Python":
                ri_base = [random.random() for _ in range(n_ri_necesarios)]
            else:
                seed = int(self.entry_seed.get())
                if seed <= 0: raise ValueError
                ri_base = generar_cuadrados_medios(seed, n_ri_necesarios)
            
            self.realizar_pruebas_estadisticas(ri_base)
            
            self.ax.clear()
            datos_transformados = []
            es_discreta = False
            
            # 2. APLICAR TRANSFORMACIONES MATEMÁTICAS DEL FORMULARIO
            if seleccion_dist == "Distribución Uniforme (Continua)":
                a = float(self.entry_a.get())
                b = float(self.entry_b.get())
                datos_transformados = [a + (b - a) * r for r in ri_base]
                self.ax.hist(datos_transformados, bins=25, color='#3498db', edgecolor='black', density=True)
                self.ax.set_title(f"Histograma Uniforme Continua U({a}, {b})")
                
            elif seleccion_dist == "Distribución Exponencial":
                lam = float(self.entry_lambda.get())
                datos_transformados = [- (1 / lam) * np.log(1 - r if r < 1 else 0.9999) for r in ri_base]
                self.ax.hist(datos_transformados, bins=25, color='#2ecc71', edgecolor='black', density=True)
                self.ax.set_title(f"Histograma Exponencial (λ = {lam})")
                
            elif seleccion_dist == "Distribución k-Erlang":
                k_val = int(self.entry_k.get())
                lam = float(self.entry_lambda_er.get())
                if k_val <= 0 or lam <= 0: raise ValueError
                
                for i in range(n_simulaciones):
                    sub_ri = ri_base[i * k_val : (i + 1) * k_val]
                    productoria = 1.0
                    for r in sub_ri:
                        productoria *= (1.0 - r if r < 1 else 0.9999)
                    xi = - (1 / (k_val * lam)) * np.log(productoria)
                    datos_transformados.append(xi)
                    
                self.ax.hist(datos_transformados, bins=25, color='#9b59b6', edgecolor='black', density=True)
                self.ax.set_title(f"Histograma k-Erlang (k={k_val}, λ={lam})")
                
            elif seleccion_dist == "Distribución Normal":
                mu = float(self.entry_mu.get())
                sigma = float(self.entry_sigma.get())
                
                for i in range(n_simulaciones):
                    sub_ri = ri_base[i * 12 : (i + 1) * 12]
                    xi = (sum(sub_ri) - 6) * sigma + mu
                    datos_transformados.append(xi)
                    
                self.ax.hist(datos_transformados, bins=25, color='#e67e22', edgecolor='black', density=True)
                self.ax.set_title(f"Histograma Normal N(μ={mu}, σ={sigma})")
                
            elif seleccion_dist == "Distribución Uniforme Discreta":
                es_discreta = True
                a = int(self.entry_a.get())
                b = int(self.entry_b.get())
                if a > b: raise ValueError
                datos_transformados = [int(a + math.floor((b - a + 1) * r)) for r in ri_base]
                
            elif seleccion_dist == "Distribución Bernoulli":
                es_discreta = True
                p = float(self.entry_p_bern.get())
                if not (0 <= p <= 1): raise ValueError
                datos_transformados = [1 if r <= p else 0 for r in ri_base]
                
            elif seleccion_dist == "Distribución Binomial":
                es_discreta = True
                n_ensayos = int(self.entry_n_binom.get())
                p = float(self.entry_p_binom.get())
                if n_ensayos <= 0 or not (0 <= p <= 1): raise ValueError
                
                for i in range(n_simulaciones):
                    sub_ri = ri_base[i * n_ensayos : (i + 1) * n_ensayos]
                    exitos = sum(1 if r <= p else 0 for r in sub_ri)
                    datos_transformados.append(exitos)

            # Renderizado específico si la variable es discreta (Gráfico de barras centradas)
            if es_discreta:
                valores, conteos = np.unique(datos_transformados, return_counts=True)
                densidad = conteos / n_simulaciones
                self.ax.bar(valores, densidad, color='#1abc9c', edgecolor='black', width=0.6)
                self.ax.set_title(f"Diagrama de Frecuencias: {seleccion_dist}")
                self.ax.set_xticks(valores)
            
            self.ax.set_ylabel("Probabilidad / Densidad")
            self.canvas.draw()
            
        except ValueError:
            messagebox.showerror("Campos Inválidos", "Por favor, revise que todos los parámetros y la semilla cumplan con las restricciones matemáticas.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraSimulacion(root)
    root.mainloop()