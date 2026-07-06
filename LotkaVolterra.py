import sys
import customtkinter as ctk
import numpy as np
from scipy.integrate import odeint

# Configuración de Matplotlib para su integración limpia en interfaces gráficas
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

# Configuración de apariencia de CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")  # Color temático acorde a la Quinua

# =====================================================================
# LÓGICA MATEMÁTICA DEL MODELO (LOTKA-VOLTERRA INDUSTRIAL)
# =====================================================================
def modelo_planta_quinua(y, t, alpha, beta, delta, gamma):
    """
    Ecuaciones base del modelo aplicadas a la planta procesadora (Requisito 3).
    y[0] = x(t) -> Stock de quinua en almacén (kg)
    y[1] = y(t) -> Nivel de procesamiento de la planta (kg/día)
    """
    stock = y[0]
    procesamiento = y[1]

    # dx/dt = alpha*x - beta*x*y (Reposición de productores menos consumo de la planta)
    d_stock_dt = alpha * stock - beta * stock * procesamiento
    
    # dy/dt = delta*x*y - gamma*y (Crecimiento por stock disponible menos reducción por fallas/mantenimiento)
    d_procesamiento_dt = delta * stock * procesamiento - gamma * procesamiento

    return [d_stock_dt, d_procesamiento_dt]


class SimuladorPlantaQuinua(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Simulador Lotka-Volterra - Planta Procesadora de Quinua")
        self.geometry("1280x760")
        
        # --- ESTRUCTURACIÓN DE DISEÑO DE PANELES ---
        self.grid_columnconfigure(0, weight=0, minsize=320)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Panel Izquierdo: Parámetros del Modelo
        self.panel_parametros = ctk.CTkFrame(self, corner_radius=10, width=320)
        self.panel_parametros.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Panel Derecho: Resultados Gráficos y Numéricos
        self.panel_visual = ctk.CTkFrame(self, corner_radius=10)
        self.panel_visual.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        self.construir_interfaz_parametros()
        self.construir_interfaz_resultados()
        
        # Ejecutar una simulación inicial por defecto
        self.ejecutar_simulacion()

    def construir_interfaz_parametros(self):
        """Cumple con el Requisito 3: Permitir ingresar parámetros del modelo dinámicamente."""
        # Título principal del panel
        label_titulo = ctk.CTkLabel(self.panel_parametros, text="Parámetros de Planta", font=ctk.CTkFont(size=16, weight="bold"))
        label_titulo.pack(pady=15, padx=10)

        # Contenedor con scroll para evitar problemas de espacio en pantallas pequeñas
        scroll_inputs = ctk.CTkScrollableFrame(self.panel_parametros, width=280, height=480, fg_color="transparent")
        scroll_inputs.pack(fill="both", expand=True, padx=5, pady=5)

        # --- VARIABLES DE ESTADO INICIAL ---
        self.input_stock0 = self.crear_input_numerico(scroll_inputs, "Stock Inicial Quinua (x0 - kg):", "10000")
        self.input_proc0 = self.crear_input_numerico(scroll_inputs, "Procesamiento Inicial (y0 - kg/día):", "2000")
        
        # --- PARÁMETROS AGROINDUSTRIALES ---
        self.input_alpha = self.crear_input_numerico(scroll_inputs, "Tasa reposición/llegada (α):", "0.15")
        self.input_beta = self.crear_input_numerico(scroll_inputs, "Tasa consumo procesamiento (β):", "0.00005")
        self.input_delta = self.crear_input_numerico(scroll_inputs, "Tasa conversión a producción (δ):", "0.00002")
        self.input_gamma = self.crear_input_numerico(scroll_inputs, "Reducción por fallas/costos (γ):", "0.20")
        
        # --- TIEMPOS DE OPERACIÓN ---
        self.input_tiempo = self.crear_input_numerico(scroll_inputs, "Tiempo Total Simulación (Días):", "100")
        self.input_pasos = self.crear_input_numerico(scroll_inputs, "Paso de tiempo (Puntos de datos):", "1000")

        # Botón de simulación principal
        self.btn_simular = ctk.CTkButton(self.panel_parametros, text="Calcular Escenario", font=ctk.CTkFont(weight="bold"), command=self.ejecutar_simulacion)
        self.btn_simular.pack(pady=15, padx=20, fill="x")

    def crear_input_numerico(self, master, label_text, default_value):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        lbl = ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=12))
        lbl.pack(anchor="w", padx=5)
        
        entry = ctk.CTkEntry(frame)
        entry.insert(0, default_value)
        entry.pack(fill="x", padx=5, pady=2)
        return entry

    def construir_interfaz_resultados(self):
        """Prepara las secciones para Gráficos (Requisito 4) y Tabla Numérica (Requisito 5)."""
        self.panel_visual.grid_rowconfigure(0, weight=3) # Gráfico superior
        self.panel_visual.grid_rowconfigure(1, weight=1) # Tabla numérica inferior
        self.panel_visual.grid_columnconfigure(0, weight=1)

        # -----------------------------------------------------------------
        # CONTENEDOR DE GRÁFICOS (MATPLOTLIB)
        # -----------------------------------------------------------------
        self.frame_grafico = ctk.CTkFrame(self.panel_visual, fg_color="white")
        self.frame_grafico.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.fig, self.axs = plt.subplots(1, 2, figsize=(9, 4))
        self.fig.patch.set_facecolor('#ffffff')
        
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas_plot.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # -----------------------------------------------------------------
        # CONTENEDOR DE RESULTADOS NUMÉRICOS (REQUISITO 5)
        # -----------------------------------------------------------------
        # Reemplazo de CTkLabelFrame por un CTkFrame estándar con su etiqueta interna
        self.frame_tabla = ctk.CTkFrame(self.panel_visual)
        self.frame_tabla.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        
        # Etiqueta que hace la función de título del recuadro
        self.lbl_titulo_tabla = ctk.CTkLabel(
            self.frame_tabla, 
            text=" Reporte y Analítica del Comportamiento del Sistema ", 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.lbl_titulo_tabla.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Grid interno para mostrar métricas clave de inventario de forma organizada
        self.txt_resumen = ctk.CTkTextbox(self.frame_tabla, font=ctk.CTkFont(family="Courier", size=12))
        self.txt_resumen.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    def ejecutar_simulacion(self):
        """Extrae parámetros, valida, ejecuta odeint e interactúa con el canvas y la tabla."""
        try:
            # Parseo y validación estricta de datos ingresados
            x0 = float(self.input_stock0.get())
            y0 = float(self.input_proc0.get())
            alpha = float(self.input_alpha.get())
            beta = float(self.input_beta.get())
            delta = float(self.input_delta.get())
            gamma = float(self.input_gamma.get())
            t_max = float(self.input_tiempo.get())
            pasos = int(self.input_pasos.get())

            if min(x0, y0, alpha, beta, delta, gamma, t_max, pasos) < 0:
                raise ValueError("No se admiten coeficientes negativos.")
                
        except ValueError as err:
            messagebox.showerror("Error en Parámetros", f"Entrada inválida detectada. Revise los valores.\nDetalle: {err}")
            return

        # Construir vector de tiempo y resolver ecuaciones diferenciales
        t = np.linspace(0, t_max, pasos)
        condiciones_iniciales = [x0, y0]
        
        solucion = odeint(modelo_planta_quinua, condiciones_iniciales, t, args=(alpha, beta, delta, gamma))
        
        stock_t = solucion[:, 0]
        proc_t = solucion[:, 1]

        # -----------------------------------------------------------------
        # ACTUALIZACIÓN DE GRÁFICOS (REQUISITO 4)
        # -----------------------------------------------------------------
        for ax in self.axs:
            ax.clear()

        # Gráfico 1: Evolución Temporal Coherente
        self.axs[0].plot(t, stock_t, color='#d35400', linewidth=2.5, label="Stock de Quinua (kg)")
        self.axs[0].plot(t, proc_t, color='#27ae60', linewidth=2.5, label="Procesamiento (kg/día)")
        self.axs[0].set_title("Evolución Dinámica en Almacén", fontsize=10, fontweight='bold')
        self.axs[0].set_xlabel("Tiempo (Días)", fontsize=9)
        self.axs[0].set_ylabel("Magnitud / Cantidades", fontsize=9)
        self.axs[0].legend(loc="upper right", fontsize=8)
        self.axs[0].grid(True, linestyle=":", alpha=0.6)

        # Gráfico 2: Plano / Espacio de Fase Industrial
        self.axs[1].plot(stock_t, proc_t, color='#2c3e50', linestyle="-", alpha=0.8)
        self.axs[1].scatter(stock_t[0], proc_t[0], color='red', s=40, label="Punto de Partida", zorder=5)
        
        # Calcular el punto crítico de equilibrio estacionario no trivial del sistema
        if delta > 0 and beta > 0:
            eq_stock = gamma / delta
            eq_proc = alpha / beta
            self.axs[1].scatter(eq_stock, eq_proc, color='purple', marker='*', s=120, label="Estabilidad Teórica", zorder=5)
            
        self.axs[1].set_title("Espacio de Fase (Stock vs Capacidad)", fontsize=10, fontweight='bold')
        self.axs[1].set_xlabel("Stock en Almacén (kg)", fontsize=9)
        self.axs[1].set_ylabel("Nivel de Procesamiento (kg/día)", fontsize=9)
        self.axs[1].legend(loc="upper right", fontsize=8)
        self.axs[1].grid(True, linestyle=":", alpha=0.6)

        self.fig.tight_layout()
        self.canvas_plot.draw()

        # -----------------------------------------------------------------
        # REPORTE NUMÉRICO ADAPTADO AL NEGOCIO (REQUISITO 5)
        # -----------------------------------------------------------------
        # Cálculo de analíticas clave del escenario simulado
        max_stock, min_stock = np.max(stock_t), np.min(stock_t)
        max_proc, min_proc = np.max(proc_t), np.min(proc_t)
        promedio_stock = np.mean(stock_t)
        promedio_proc = np.mean(proc_t)

        reporte_texto = (
            f"{'='*64}\n"
            f"          RESUMEN NUMÉRICO DE SIMULACIÓN OPERATIVA (SIR)\n"
            f"{'='*64}\n"
            f"  * Stock Máximo en Almacén:      {max_stock:,.2f} kg\n"
            f"  * Stock Mínimo Crítico:         {min_stock:,.2f} kg\n"
            f"  * Promedio Inventario Quinua:   {promedio_stock:,.2f} kg\n"
            f"----------------------------------------------------------------\n"
            f"  * Capacidad de Procesado Máx:   {max_proc:,.2f} kg/día\n"
            f"  * Capacidad de Procesado Mín:   {min_proc:,.2f} kg/día\n"
            f"  * Promedio de Operación Planta: {promedio_proc:,.2f} kg/día\n"
            f"----------------------------------------------------------------\n"
            f" DIAGNÓSTICO INDUSTRIAL:\n"
        )
        
        # Lógica de interpretación automatizada del sistema (Para sumar en creatividad)
        if min_stock < (x0 * 0.15):
            reporte_texto += "  ALERTA: Peligro de desabastecimiento severo en almacén.\n" \
                             "  La planta consume la materia prima más rápido de lo que se repone."
        elif max_proc > (y0 * 2.5):
            reporte_texto += "  Escenario de Alta Demanda. La planta experimenta picos de sobreproducción\n" \
                             "  por exceso de stock. Se sugiere programar mantenimientos."
        else:
            reporte_texto += "  Operación Cíclica Estable. El flujo de abastecimiento de productores\n" \
                             "  mantiene una oscilación segura que amortigua paradas técnicas."
                             
        self.txt_resumen.delete("1.0", "end")
        self.txt_resumen.insert("1.0", reporte_texto)


if __name__ == "__main__":
    # Asegura una correcta visualización en sistemas de alta densidad de pixeles (HiDPI)
    if sys.platform.startswith("win"):
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
        
    app = SimuladorPlantaQuinua()
    app.mainloop()