"""
Interfaz gráfica de la práctica de Pandas y Matplotlib.
Estilo minimalista en blanco y negro.

    python interfaz.py

Atajos: F5 = ejecutar todo, Ctrl+L = limpiar consola.
"""

import os
import queue
import subprocess
import sys
import threading
import time
import traceback
from contextlib import redirect_stdout
import tkinter as tk

import matplotlib

matplotlib.use("Agg")  # las figuras se guardan como PNG; la vista previa la hace la interfaz

import practica_pandas as pp  # noqa: E402

try:
    from PIL import Image, ImageTk
except ImportError:  # sin Pillow se usa tk.PhotoImage
    Image = ImageTk = None


# ----------------------------------------------------------------------
# Estilo
# ----------------------------------------------------------------------
BLANCO = "#ffffff"
NEGRO = "#111111"
GRIS = "#555555"
GRIS_CLARO = "#e6e6e6"
TENUE = "#9a9a9a"
CONSOLA = "#0c0c0c"
TEXTO_CONSOLA = "#f2f2f2"

F_TITULO = ("Segoe UI", 20, "bold")
F_SUB = ("Consolas", 9, "bold")
F_BOTON = ("Segoe UI", 9, "bold")
F_BOTON_CHICO = ("Segoe UI", 8, "bold")
F_TARJETA = ("Segoe UI", 12, "bold")
F_NUM = ("Consolas", 11, "bold")
F_TAG = ("Consolas", 8, "bold")
F_DESC = ("Segoe UI", 9)
F_ARCHIVO = ("Segoe UI", 8, "bold")
F_CONSOLA = ("Consolas", 10)
F_CONSOLA_B = ("Consolas", 10, "bold")
F_BUSCAR = ("Segoe UI", 10)

ARCHIVOS_SALIDA = [
    "promedios_alumnos.csv",
    "promedio_materias.png",
    "histograma.png",
    "tendencia_unidades.png",
]

EJERCICIOS = [
    {
        "nombre": "CARGA Y REVISIÓN",
        "categoria": "DATOS",
        "desc": "Lee calificaciones_isc.csv en un DataFrame y muestra las primeras "
                "filas, filas y columnas, tipos de dato y describe() de calificacion "
                "y asistencias.",
        "archivos": [],
        "funcion": pp.ejercicio1,
    },
    {
        "nombre": "FILTROS",
        "categoria": "DATOS",
        "desc": "Tres filtros con máscaras booleanas, sin modificar df: grupo A, "
                "calificación menor a 70 y Bases de datos del grupo B con al menos 80. "
                "Conteo con len().",
        "archivos": [],
        "funcion": pp.ejercicio2,
    },
    {
        "nombre": "COLUMNA CALCULADA",
        "categoria": "ANÁLISIS",
        "desc": "Agrega la columna situacion (Aprobado / Reprobado) con np.where, "
                "sin ciclos.",
        "archivos": [],
        "funcion": pp.ejercicio3,
    },
    {
        "nombre": "RESÚMENES",
        "categoria": "ANÁLISIS",
        "desc": "groupby por materia, por grupo y materia, por alumno y por unidad; "
                "cuenta las unidades aprobadas y reprobadas y exporta el promedio de "
                "cada alumno.",
        "archivos": ["promedios_alumnos.csv"],
        "funcion": pp.ejercicio4,
    },
    {
        "nombre": "GRÁFICAS",
        "categoria": "GRÁFICAS",
        "desc": "Barras del promedio por materia, histograma con una línea en 70 y "
                "tendencia por unidad. Cada figura lleva título y ejes y se guarda "
                "como PNG.",
        "archivos": ["promedio_materias.png", "histograma.png", "tendencia_unidades.png"],
        "funcion": lambda df: pp.ejercicio5(df, mostrar=False),
    },
    {
        "nombre": "LECTURA DE RESULTADOS",
        "categoria": "ANÁLISIS",
        "desc": "Interpretación con los números obtenidos: la materia más baja, la "
                "caída de la unidad 3 y los alumnos con promedio menor a 70.",
        "archivos": [],
        "funcion": pp.ejercicio6,
    },
]

CATEGORIAS = ["TODOS", "DATOS", "ANÁLISIS", "GRÁFICAS"]


# ----------------------------------------------------------------------
# Componentes
# ----------------------------------------------------------------------
def panel_con_sombra(padre, desplazamiento=4, bg=BLANCO):
    """Marco con borde negro y sombra sólida abajo a la derecha."""
    externo = tk.Frame(padre, bg=NEGRO)
    interno = tk.Frame(
        externo, bg=bg, highlightthickness=2,
        highlightbackground=NEGRO, highlightcolor=NEGRO,
    )
    interno.pack(fill="both", expand=True, padx=(0, desplazamiento), pady=(0, desplazamiento))
    return externo, interno


class Boton(tk.Frame):
    """Botón plano con borde negro, sombra y colores invertidos al pasar el mouse."""

    def __init__(self, padre, texto, comando, primario=False, chico=False,
                 sombra=3, fondo=BLANCO):
        super().__init__(padre, bg=NEGRO if sombra else fondo)
        self.comando = comando
        self.primario = primario
        self.habilitado = True
        self.sombra = sombra
        self.lbl = tk.Label(
            self, text=texto, bd=0, cursor="hand2",
            font=F_BOTON_CHICO if chico else F_BOTON,
            padx=9 if chico else 16, pady=3 if chico else 7,
            highlightthickness=1 if chico else 2,
            highlightbackground=NEGRO, highlightcolor=NEGRO,
        )
        self.lbl.pack(padx=(0, sombra), pady=(0, sombra))
        self.lbl.bind("<Enter>", lambda e: self._pintar(hover=True))
        self.lbl.bind("<Leave>", lambda e: self._pintar())
        self.lbl.bind("<ButtonPress-1>", self._presionar)
        self.lbl.bind("<ButtonRelease-1>", self._soltar)
        self._pintar()

    def _pintar(self, hover=False):
        if not self.habilitado:
            bg, fg = GRIS_CLARO, TENUE
        elif self.primario != (hover and self.habilitado):
            bg, fg = NEGRO, BLANCO
        else:
            bg, fg = BLANCO, NEGRO
        self.lbl.config(bg=bg, fg=fg)

    def _presionar(self, _):
        if self.habilitado and self.sombra:
            self.lbl.pack_configure(padx=(self.sombra, 0), pady=(self.sombra, 0))

    def _soltar(self, evento):
        if self.sombra:
            self.lbl.pack_configure(padx=(0, self.sombra), pady=(0, self.sombra))
        dentro = 0 <= evento.x < self.lbl.winfo_width() and 0 <= evento.y < self.lbl.winfo_height()
        if self.habilitado and dentro:
            self.comando()

    def habilitar(self, valor):
        self.habilitado = valor
        self.lbl.config(cursor="hand2" if valor else "arrow")
        self._pintar()

    def marcar(self, activo):
        self.primario = activo
        self._pintar()


class Tarjeta:
    """Tarjeta de un ejercicio dentro de la lista."""

    def __init__(self, padre, indice, ejercicio, al_ejecutar):
        self.indice = indice
        self.ej = ejercicio
        self.externo, cuerpo = panel_con_sombra(padre, 4)

        fila = tk.Frame(cuerpo, bg=BLANCO)
        fila.pack(fill="x", padx=14, pady=(12, 4))
        tk.Label(fila, text=f"[{indice + 1:02d}]", font=F_NUM, bg=BLANCO, fg=NEGRO).pack(side="left")
        tk.Label(fila, text=ejercicio["nombre"], font=F_TARJETA, bg=BLANCO, fg=NEGRO).pack(
            side="left", padx=(8, 10))
        tk.Label(
            fila, text=ejercicio["categoria"], font=F_TAG, bg=BLANCO, fg=NEGRO,
            padx=6, pady=1, highlightthickness=1, highlightbackground=NEGRO,
        ).pack(side="left")
        self.lbl_estado = tk.Label(fila, text="", font=F_TAG, bg=BLANCO, fg=GRIS)
        self.lbl_estado.pack(side="left", padx=8)

        self.boton = Boton(fila, "►  EJECUTAR", lambda: al_ejecutar(indice))
        self.boton.pack(side="right")

        self.desc = tk.Label(
            cuerpo, text=ejercicio["desc"], font=F_DESC, bg=BLANCO, fg="#333333",
            justify="left", anchor="w",
        )
        self.desc.pack(fill="x", padx=14)

        if ejercicio["archivos"]:
            tk.Label(
                cuerpo, text="Archivo generado: " + ", ".join(ejercicio["archivos"]),
                font=F_ARCHIVO, bg=BLANCO, fg=NEGRO, anchor="w", justify="left",
            ).pack(fill="x", padx=14, pady=(5, 0))

        tk.Frame(cuerpo, bg=BLANCO, height=10).pack()
        cuerpo.bind("<Configure>", lambda e: self.desc.config(wraplength=max(e.width - 34, 100)))

    def coincide(self, texto, categoria):
        if categoria != "TODOS" and self.ej["categoria"] != categoria:
            return False
        contenido = f"{self.indice + 1} {self.ej['nombre']} {self.ej['desc']}".lower()
        return texto in contenido

    def estado(self, texto, color=GRIS):
        self.lbl_estado.config(text=texto, fg=color)


class EscritorCola:
    """Sustituye a sys.stdout: manda cada línea impresa a la cola de la interfaz."""

    def __init__(self, cola):
        self.cola = cola
        self.buffer = ""

    def write(self, texto):
        self.buffer += texto
        while "\n" in self.buffer:
            linea, self.buffer = self.buffer.split("\n", 1)
            self.cola.put(("linea", linea))
        return len(texto)

    def flush(self):
        if self.buffer:
            self.cola.put(("linea", self.buffer))
            self.buffer = ""


class VistaPrevia(tk.Toplevel):
    """Ventana para ver una gráfica PNG."""

    def __init__(self, padre, ruta):
        super().__init__(padre, bg=BLANCO)
        self.title(ruta.name)
        self.configure(padx=18, pady=16)
        self.transient(padre)

        tk.Label(self, text=ruta.name.upper(), font=F_TARJETA, bg=BLANCO, fg=NEGRO).pack(anchor="w")
        tk.Frame(self, bg=NEGRO, height=2).pack(fill="x", pady=(6, 12))

        externo, cuerpo = panel_con_sombra(self, 4)
        externo.pack()
        max_w = int(self.winfo_screenwidth() * 0.6)
        max_h = int(self.winfo_screenheight() * 0.6)
        if Image is not None:
            img = Image.open(ruta)
            img.thumbnail((max_w, max_h))
            self.imagen = ImageTk.PhotoImage(img)
        else:
            self.imagen = tk.PhotoImage(file=str(ruta))
            factor = max(1, -(-self.imagen.width() // max_w), -(-self.imagen.height() // max_h))
            if factor > 1:
                self.imagen = self.imagen.subsample(factor)
        tk.Label(cuerpo, image=self.imagen, bg=BLANCO, bd=0).pack()

        botones = tk.Frame(self, bg=BLANCO)
        botones.pack(fill="x", pady=(14, 0))
        Boton(botones, "CERRAR", self.destroy, primario=True).pack(side="right")
        Boton(botones, "ABRIR EN EL VISOR DEL SISTEMA", lambda: abrir_con_sistema(ruta)).pack(
            side="right", padx=10)
        self.bind("<Escape>", lambda e: self.destroy())
        self.focus_set()


def abrir_con_sistema(ruta):
    if sys.platform == "win32":
        os.startfile(ruta)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(ruta)])
    else:
        subprocess.Popen(["xdg-open", str(ruta)])


# ----------------------------------------------------------------------
# Ventana principal
# ----------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Práctica Pandas & Matplotlib")
        self.configure(bg=BLANCO)
        escala = float(self.tk.call("tk", "scaling")) / (96 / 72)
        ancho = min(int(1180 * escala), self.winfo_screenwidth() - 40)
        alto = min(int(760 * escala), self.winfo_screenheight() - 80)
        self.geometry(f"{ancho}x{alto}")
        self.minsize(int(900 * escala), int(560 * escala))

        self.cola = queue.Queue()
        self.ocupado = False
        self.categoria = "TODOS"
        self.tarjetas = []
        self.estado_actual = "●  LISTO"
        self.lote_actual = ""

        self._cabecera()
        self._cuerpo()
        self._bienvenida()
        self._actualizar_archivos()

        self.bind("<F5>", lambda e: self.ejecutar_todo())
        self.bind("<Control-l>", lambda e: self.limpiar())
        self.after(40, self._revisar_cola)

    # --- construcción -------------------------------------------------
    def _cabecera(self):
        cab = tk.Frame(self, bg=BLANCO)
        cab.pack(fill="x", padx=24, pady=(18, 12))

        textos = tk.Frame(cab, bg=BLANCO)
        textos.pack(side="left")
        tk.Label(textos, text="PRÁCTICA PANDAS & MATPLOTLIB", font=F_TITULO,
                 bg=BLANCO, fg=NEGRO).pack(anchor="w")
        tk.Label(
            textos,
            text="6 EJERCICIOS INTERACTIVOS  ·  CALIFICACIONES ISC  ·  ESTILO MINIMALISTA B&W",
            font=F_SUB, bg=BLANCO, fg=GRIS,
        ).pack(anchor="w")

        Boton(cab, "📂  CARPETA DEL PROYECTO", lambda: abrir_con_sistema(pp.CARPETA)).pack(
            side="right")
        self.btn_todo = Boton(cab, "►  EJECUTAR TODO", self.ejecutar_todo, primario=True)
        self.btn_todo.pack(side="right", padx=14)

        tk.Frame(self, bg=NEGRO, height=2).pack(fill="x", padx=24)

    def _cuerpo(self):
        cuerpo = tk.Frame(self, bg=BLANCO)
        cuerpo.pack(fill="both", expand=True, padx=24, pady=(16, 20))
        cuerpo.columnconfigure(0, weight=5, uniform="col")
        cuerpo.columnconfigure(1, weight=6, uniform="col")
        cuerpo.rowconfigure(0, weight=1)

        izq = tk.Frame(cuerpo, bg=BLANCO)
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        der = tk.Frame(cuerpo, bg=BLANCO)
        der.grid(row=0, column=1, sticky="nsew")

        self._panel_lista(izq)
        self._panel_consola(der)

    def _panel_lista(self, padre):
        # Buscador
        externo, caja = panel_con_sombra(padre, 3)
        externo.pack(fill="x")
        tk.Label(caja, text="🔍", font=F_BUSCAR, bg=BLANCO, fg=NEGRO).pack(side="left", padx=(10, 4))
        self.var_buscar = tk.StringVar()
        self.entrada = tk.Entry(
            caja, textvariable=self.var_buscar, font=F_BUSCAR, bd=0,
            bg=BLANCO, fg=TENUE, insertbackground=NEGRO, relief="flat",
        )
        self.entrada.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 10))
        self._marcador = "Buscar ejercicio..."
        self.entrada.insert(0, self._marcador)
        self.entrada.bind("<FocusIn>", self._quitar_marcador)
        self.entrada.bind("<FocusOut>", self._poner_marcador)
        self.var_buscar.trace_add("write", lambda *_: self.filtrar())

        # Pestañas de categoría
        pestanas = tk.Frame(padre, bg=BLANCO)
        pestanas.pack(fill="x", pady=(12, 12))
        self.botones_cat = {}
        for cat in CATEGORIAS:
            b = Boton(pestanas, cat, lambda c=cat: self.elegir_categoria(c),
                      chico=True, sombra=0, primario=(cat == "TODOS"))
            b.pack(side="left", padx=(0, 6))
            self.botones_cat[cat] = b

        # Lista desplazable de tarjetas
        marco = tk.Frame(padre, bg=BLANCO)
        marco.pack(fill="both", expand=True)
        self.lienzo = tk.Canvas(marco, bg=BLANCO, highlightthickness=0, bd=0)
        barra = tk.Scrollbar(marco, orient="vertical", command=self.lienzo.yview)
        self.lienzo.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.lienzo.pack(side="left", fill="both", expand=True)

        self.lista = tk.Frame(self.lienzo, bg=BLANCO)
        ventana = self.lienzo.create_window((0, 0), window=self.lista, anchor="nw")
        self.lista.bind("<Configure>",
                        lambda e: self.lienzo.configure(scrollregion=self.lienzo.bbox("all")))
        self.lienzo.bind("<Configure>", lambda e: self.lienzo.itemconfigure(ventana, width=e.width))
        self.lienzo.bind("<Enter>", lambda e: self.lienzo.bind_all("<MouseWheel>", self._rueda))
        self.lienzo.bind("<Leave>", lambda e: self.lienzo.unbind_all("<MouseWheel>"))

        for i, ej in enumerate(EJERCICIOS):
            self.tarjetas.append(Tarjeta(self.lista, i, ej, self.ejecutar_uno))
        self.sin_resultados = tk.Label(self.lista, text="Ningún ejercicio coincide con la búsqueda.",
                                       font=F_DESC, bg=BLANCO, fg=GRIS)
        self.filtrar()

    def _panel_consola(self, padre):
        externo, consola = panel_con_sombra(padre, 4, bg=CONSOLA)
        externo.pack(fill="both", expand=True)

        barra = tk.Frame(consola, bg=CONSOLA)
        barra.pack(fill="x", padx=12, pady=(10, 8))
        self.lbl_estado = tk.Label(barra, text=self.estado_actual, font=F_CONSOLA_B,
                                   bg=CONSOLA, fg=TEXTO_CONSOLA)
        self.lbl_estado.pack(side="left")
        Boton(barra, "⧉  COPIAR", self.copiar, chico=True, sombra=0, fondo=CONSOLA).pack(side="right")
        Boton(barra, "✕  LIMPIAR", self.limpiar, chico=True, sombra=0, fondo=CONSOLA).pack(
            side="right", padx=8)
        tk.Frame(consola, bg="#2e2e2e", height=1).pack(fill="x")

        zona = tk.Frame(consola, bg=CONSOLA)
        zona.pack(fill="both", expand=True)
        self.texto = tk.Text(
            zona, bg=CONSOLA, fg=TEXTO_CONSOLA, font=F_CONSOLA, bd=0, wrap="none",
            padx=14, pady=10, insertbackground=TEXTO_CONSOLA, selectbackground="#444444",
            highlightthickness=0, state="disabled",
        )
        sy = tk.Scrollbar(zona, orient="vertical", command=self.texto.yview)
        sx = tk.Scrollbar(zona, orient="horizontal", command=self.texto.xview)
        self.texto.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")
        self.texto.pack(side="left", fill="both", expand=True)
        self.texto.tag_configure("sep", foreground="#5a5a5a")
        self.texto.tag_configure("titulo", font=F_CONSOLA_B, foreground=BLANCO)
        self.texto.tag_configure("negrita", font=F_CONSOLA_B)
        self.texto.tag_configure("ok", font=F_CONSOLA_B, foreground=BLANCO)
        self.texto.tag_configure("error", font=F_CONSOLA_B, foreground="#ff6b6b")
        self.texto.tag_configure("tenue", foreground="#8c8c8c")

        # Barra de archivos generados
        externo, caja = panel_con_sombra(padre, 3)
        externo.pack(fill="x", pady=(14, 0))
        tk.Label(caja, text="📁  ARCHIVOS:", font=F_BOTON, bg=BLANCO, fg=NEGRO).pack(
            side="left", padx=(12, 8), pady=9)
        self.zona_archivos = tk.Frame(caja, bg=BLANCO)
        self.zona_archivos.pack(side="left", fill="x", expand=True, pady=4, padx=(0, 8))
        self.chips = []
        self.zona_archivos.bind("<Configure>", self._acomodar_archivos)

    # --- buscador y pestañas -----------------------------------------
    def _quitar_marcador(self, _):
        if self.entrada.get() == self._marcador and self.entrada.cget("fg") == TENUE:
            self.entrada.delete(0, "end")
            self.entrada.config(fg=NEGRO)

    def _poner_marcador(self, _):
        if not self.entrada.get():
            self.entrada.config(fg=TENUE)
            self.entrada.insert(0, self._marcador)

    def _texto_busqueda(self):
        if self.entrada.cget("fg") == TENUE:
            return ""
        return self.var_buscar.get().strip().lower()

    def elegir_categoria(self, categoria):
        self.categoria = categoria
        for cat, boton in self.botones_cat.items():
            boton.marcar(cat == categoria)
        self.filtrar()

    def filtrar(self):
        texto = self._texto_busqueda()
        visibles = 0
        for t in self.tarjetas:
            t.externo.pack_forget()
        self.sin_resultados.pack_forget()
        for t in self.tarjetas:
            if t.coincide(texto, self.categoria):
                t.externo.pack(fill="x", padx=(2, 10), pady=(0, 14))
                visibles += 1
        if not visibles:
            self.sin_resultados.pack(anchor="w", pady=10)
        self.lienzo.yview_moveto(0)

    def _rueda(self, evento):
        if self.lista.winfo_height() > self.lienzo.winfo_height():
            self.lienzo.yview_scroll(int(-evento.delta / 120), "units")

    # --- consola ------------------------------------------------------
    def escribir(self, linea, etiqueta=None):
        if etiqueta is None:
            s = linea.strip()
            if s.startswith("===="):
                etiqueta = "sep"
            elif s.startswith("Ejercicio "):
                etiqueta = "titulo"
            elif s.startswith("Archivo creado"):
                etiqueta = "negrita"
            elif s.startswith("Traceback") or s.startswith("[ERROR]"):
                etiqueta = "error"
        self.texto.configure(state="normal")
        self.texto.insert("end", linea + "\n", etiqueta or ())
        self.texto.configure(state="disabled")
        self.texto.see("end")

    def _bienvenida(self):
        self.escribir("Análisis y visualización de calificaciones con Pandas y Matplotlib", "titulo")
        self.escribir(f"Carpeta: {pp.CARPETA}", "tenue")
        if pp.ARCHIVO_CSV.exists():
            self.escribir(f"Datos:   {pp.ARCHIVO_CSV.name}", "tenue")
        else:
            self.escribir(f"[ERROR] No se encontró {pp.ARCHIVO_CSV.name} en la carpeta.", "error")
        self.escribir("")
        self.escribir("Elige un ejercicio y presiona ► EJECUTAR, o usa ► EJECUTAR TODO (F5).")
        self.escribir("Los archivos generados aparecen abajo: haz clic para abrirlos.")

    def _poner_estado(self, texto):
        self.estado_actual = texto
        self.lbl_estado.config(text=texto)

    def limpiar(self):
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.configure(state="disabled")
        if not self.ocupado:
            self._poner_estado("●  LISTO")

    def copiar(self):
        self.clipboard_clear()
        self.clipboard_append(self.texto.get("1.0", "end-1c"))
        anterior = self.estado_actual
        self.lbl_estado.config(text="●  COPIADO AL PORTAPAPELES")
        self.after(1400, lambda: self.lbl_estado.config(text=self.estado_actual)
                   if self.estado_actual == anterior else None)

    def _actualizar_archivos(self):
        for w in self.zona_archivos.winfo_children():
            w.destroy()
        self.chips = []
        existentes = [n for n in ARCHIVOS_SALIDA if (pp.CARPETA / n).exists()]
        if not existentes:
            self.chips.append(tk.Label(self.zona_archivos, text="Aún no hay archivos generados.",
                                       font=F_DESC, bg=BLANCO, fg=GRIS))
        for nombre in existentes:
            icono = "▣" if nombre.endswith(".png") else "▤"
            self.chips.append(Boton(self.zona_archivos, f"{icono}  {nombre}",
                                    lambda n=nombre: self.abrir_archivo(n), chico=True, sombra=0))
        self._acomodar_archivos(forzar=True)

    def _acomodar_archivos(self, evento=None, forzar=False):
        """Acomoda los botones de archivo en renglones según el ancho disponible."""
        self.zona_archivos.update_idletasks()
        ancho = self.zona_archivos.winfo_width()
        if ancho <= 1 or (not forzar and ancho == getattr(self, "_ancho_archivos", None)):
            return
        self._ancho_archivos = ancho
        fila = col = usado = 0
        for chip in self.chips:
            w = chip.winfo_reqwidth() + 6
            if usado and usado + w > ancho:
                fila, col, usado = fila + 1, 0, 0
            chip.grid(row=fila, column=col, padx=(0, 6), pady=4, sticky="w")
            col += 1
            usado += w

    def abrir_archivo(self, nombre):
        ruta = pp.CARPETA / nombre
        if not ruta.exists():
            self._actualizar_archivos()
            return
        if ruta.suffix == ".png":
            VistaPrevia(self, ruta)
        else:
            abrir_con_sistema(ruta)

    # --- ejecución ----------------------------------------------------
    def ejecutar_uno(self, indice):
        self._ejecutar([indice], EJERCICIOS[indice]["nombre"])

    def ejecutar_todo(self):
        self._ejecutar(list(range(len(EJERCICIOS))), "TODOS LOS EJERCICIOS")

    def _habilitar(self, valor):
        self.btn_todo.habilitar(valor)
        for t in self.tarjetas:
            t.boton.habilitar(valor)

    def _ejecutar(self, indices, nombre_lote):
        if self.ocupado:
            return
        self.ocupado = True
        self.lote_actual = nombre_lote
        self._habilitar(False)
        for i in indices:
            self.tarjetas[i].estado("EN COLA", TENUE)
        threading.Thread(target=self._trabajo, args=(indices,), daemon=True).start()

    def _trabajo(self, indices):
        """Corre en un hilo aparte para no congelar la ventana."""
        escritor = EscritorCola(self.cola)
        inicio_total = time.perf_counter()
        todo_ok = True
        with redirect_stdout(escritor):
            try:
                df = pp.cargar_datos()  # un df nuevo por cada ejecución
            except Exception as exc:
                print(f"[ERROR] No se pudo leer {pp.ARCHIVO_CSV.name}: {exc}")
                escritor.flush()
                for i in indices:
                    self.cola.put(("fin", i, False, 0.0))
                self.cola.put(("terminado", False, 0.0))
                return
            for i in indices:
                self.cola.put(("inicio", i))
                t0 = time.perf_counter()
                try:
                    EJERCICIOS[i]["funcion"](df)
                    ok = True
                except Exception:
                    traceback.print_exc(file=sys.stdout)
                    ok = todo_ok = False
                escritor.flush()
                self.cola.put(("fin", i, ok, time.perf_counter() - t0))
        self.cola.put(("terminado", todo_ok, time.perf_counter() - inicio_total))

    def _revisar_cola(self):
        try:
            for _ in range(500):
                msg = self.cola.get_nowait()
                tipo = msg[0]
                if tipo == "linea":
                    self.escribir(msg[1])
                elif tipo == "inicio":
                    nombre = EJERCICIOS[msg[1]]["nombre"]
                    self._poner_estado(f"◌  EJECUTANDO: {nombre}...")
                    self.tarjetas[msg[1]].estado("EJECUTANDO...", NEGRO)
                elif tipo == "fin":
                    _, i, ok, dt = msg
                    nombre = EJERCICIOS[i]["nombre"].capitalize()
                    if ok:
                        self.escribir("")
                        self.escribir(f"[OK] {nombre} finalizado con éxito en {dt:.2f}s.", "ok")
                        self.tarjetas[i].estado(f"✓ {dt:.2f}s", NEGRO)
                    else:
                        self.escribir(f"[ERROR] {nombre} terminó con errores.", "error")
                        self.tarjetas[i].estado("✕ ERROR", "#c62828")
                    self._actualizar_archivos()
                elif tipo == "terminado":
                    _, ok, dt = msg
                    marca = "●  COMPLETADO" if ok else "✕  CON ERRORES"
                    self._poner_estado(f"{marca}: {self.lote_actual} ({dt:.2f}s)")
                    self.ocupado = False
                    self._habilitar(True)
        except queue.Empty:
            pass
        self.after(40, self._revisar_cola)


def main():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # texto nítido en pantallas escaladas
        except Exception:
            pass
    App().mainloop()


if __name__ == "__main__":
    main()
