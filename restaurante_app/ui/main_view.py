# ui/main_view.py
# Panel principal con navegacion lateral (sidebar) y area de contenido.
# Cada seccion usa contenedores (Frame, LabelFrame) para separar
# navegacion, formulario y presentacion de informacion. Las vistas
# nunca leen ni escriben productos.json/usuarios.json directamente:
# siempre piden la operacion a self.restaurante_servicio.

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


class MainView(tk.Frame):
    def __init__(self, master, restaurante_servicio, usuario_actual, al_cerrar_sesion):
        super().__init__(master, bg="#f7fafc")
        self.restaurante_servicio = restaurante_servicio
        self.usuario_actual = usuario_actual
        self.al_cerrar_sesion = al_cerrar_sesion

        self.contenido = None
        self.etiqueta_estado = None
        self.botones_menu = {}
        self.iconos = {}

        # Referencias a los campos del formulario de productos.
        self.producto_codigo_entry = None
        self.producto_nombre_entry = None
        self.producto_categoria_entry = None
        self.producto_precio_entry = None
        self.producto_stock_entry = None
        self.tabla_productos = None
        self.tabla_usuarios = None

        self.definir_estilos()
        self.construir_interfaz()

    # -------------------------------------------------------------------------
    # Configuracion general: colores, estilos e iconos.
    # -------------------------------------------------------------------------
    def definir_estilos(self):
        self.color_fondo = "#f7fafc"
        self.color_panel = "#ffffff"
        self.color_encabezado = "#1f2a44"
        self.color_texto = "#243447"
        self.color_secundario = "#dbeafe"
        self.color_resaltado = "#2563eb"

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "MenuApp.TButton",
            background="#334155",
            foreground="#ffffff",
            font=("Arial", 10, "bold"),
            padding=(12, 10),
            borderwidth=0,
            anchor="w",
        )
        estilo.map("MenuApp.TButton", background=[("active", "#475569")])
        estilo.configure(
            "MenuActivo.TButton",
            background=self.color_resaltado,
            foreground="#ffffff",
            font=("Arial", 10, "bold"),
            padding=(12, 10),
            borderwidth=0,
            anchor="w",
        )
        estilo.map("MenuActivo.TButton", background=[("active", "#1d4ed8")])
        estilo.configure(
            "Secundario.TButton",
            background="#1f2a44",
            foreground="#ffffff",
            font=("Arial", 10, "bold"),
            padding=(10, 7),
            borderwidth=0,
        )
        estilo.map("Secundario.TButton", background=[("active", "#334155")])
        estilo.configure(
            "Accion.TButton",
            background=self.color_resaltado,
            foreground="#ffffff",
            font=("Arial", 10, "bold"),
            padding=(10, 7),
            borderwidth=0,
        )
        estilo.map("Accion.TButton", background=[("active", "#1d4ed8")])
        estilo.configure(
            "Eliminar.TButton",
            background="#e11d48",
            foreground="#ffffff",
            font=("Arial", 10, "bold"),
            padding=(10, 7),
            borderwidth=0,
        )
        estilo.map("Eliminar.TButton", background=[("active", "#be123c")])
        estilo.configure(
            "Treeview.Heading",
            background=self.color_secundario,
            foreground=self.color_encabezado,
            font=("Arial", 10, "bold"),
        )

    def cargar_icono(self, nombre_archivo):
        # Carga un icono desde assets/icons si existe. Si no existe (o la
        # carpeta assets no esta presente), se continua sin icono: los
        # botones funcionan igual, solo se muestran con texto.
        if nombre_archivo in self.iconos:
            return self.iconos[nombre_archivo]

        ruta_base = Path(__file__).resolve().parent.parent
        ruta_icono = ruta_base / "assets" / "icons" / nombre_archivo

        if not ruta_icono.exists():
            return None

        try:
            icono = tk.PhotoImage(file=str(ruta_icono))
        except tk.TclError:
            return None

        self.iconos[nombre_archivo] = icono
        return icono

    def crear_boton(self, contenedor, texto, comando, estilo, icono=None):
        imagen = self.cargar_icono(icono) if icono else None

        if imagen is not None:
            boton = ttk.Button(
                contenedor, text=texto, command=comando, style=estilo,
                image=imagen, compound="left",
            )
        else:
            boton = ttk.Button(contenedor, text=texto, command=comando, style=estilo)

        return boton

    # -------------------------------------------------------------------------
    # Estructura principal: sidebar (navegacion) + area de contenido.
    # -------------------------------------------------------------------------
    def construir_interfaz(self):
        frame_sidebar = tk.Frame(self, bg=self.color_encabezado, width=190, padx=16, pady=18)
        frame_sidebar.pack(side="left", fill="y")
        frame_sidebar.pack_propagate(False)

        tk.Label(
            frame_sidebar, text="RESTAURANTE", bg=self.color_encabezado,
            fg="#ffffff", font=("Arial", 16, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(
            frame_sidebar, text=self.usuario_actual.nombre, bg=self.color_encabezado,
            fg="#dbeafe", font=("Arial", 10), wraplength=150, justify="left",
        ).pack(anchor="w", pady=(0, 24))

        self.crear_boton_menu(frame_sidebar, "Inicio", self.mostrar_inicio, "home.png")
        self.crear_boton_menu(frame_sidebar, "Usuarios", self.mostrar_usuarios, "users.png")
        self.crear_boton_menu(frame_sidebar, "Productos", self.mostrar_productos, "products.png")

        tk.Frame(frame_sidebar, bg=self.color_encabezado).pack(fill="both", expand=True)

        self.crear_boton(
            frame_sidebar, "Cerrar sesion", self.cerrar_sesion, "Eliminar.TButton", "logout.png",
        ).pack(fill="x", pady=(16, 0))

        frame_principal = tk.Frame(self, bg=self.color_fondo)
        frame_principal.pack(side="left", fill="both", expand=True)

        self.contenido = tk.Frame(frame_principal, bg=self.color_fondo, padx=28, pady=24)
        self.contenido.pack(fill="both", expand=True)

        barra_estado = tk.Frame(frame_principal, bg=self.color_secundario, padx=18, pady=8)
        barra_estado.pack(fill="x", side="bottom")

        self.etiqueta_estado = tk.Label(
            barra_estado, bg=self.color_secundario, fg=self.color_texto, font=("Arial", 10),
        )
        self.etiqueta_estado.pack(side="left")

        self.mostrar_inicio()

    def crear_boton_menu(self, contenedor, texto, comando, icono):
        boton = self.crear_boton(contenedor, texto, comando, "MenuApp.TButton", icono)
        boton.pack(fill="x", pady=(0, 8))
        self.botones_menu[texto] = boton

    def marcar_seccion(self, seccion):
        for texto, boton in self.botones_menu.items():
            estilo = "MenuActivo.TButton" if texto == seccion else "MenuApp.TButton"
            boton.configure(style=estilo)

    def limpiar_contenido(self):
        assert self.contenido is not None
        for widget in self.contenido.winfo_children():
            widget.destroy()

    def actualizar_barra_estado(self):
        assert self.etiqueta_estado is not None
        self.etiqueta_estado.config(
            text=(
                f"Productos: {self.restaurante_servicio.contar_productos()} | "
                f"Usuarios: {self.restaurante_servicio.cantidad_usuarios()} | "
                "Datos JSON locales"
            )
        )

    # -------------------------------------------------------------------------
    # Vista de inicio: resumen general del sistema.
    # -------------------------------------------------------------------------
    def mostrar_inicio(self):
        self.marcar_seccion("Inicio")
        self.limpiar_contenido()
        self.actualizar_barra_estado()

        assert self.contenido is not None

        tk.Label(
            self.contenido, text="Panel principal", bg=self.color_fondo,
            fg=self.color_encabezado, font=("Arial", 20, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(
            self.contenido, text="Consulte usuarios y gestione productos desde el menú lateral.",
            bg=self.color_fondo, fg=self.color_texto, font=("Arial", 12),
        ).pack(anchor="w", pady=(0, 22))

        resumen = tk.Frame(self.contenido, bg=self.color_fondo)
        resumen.pack(fill="x")
        self.crear_tarjeta_resumen(resumen, "Usuarios registrados", self.restaurante_servicio.cantidad_usuarios())
        self.crear_tarjeta_resumen(resumen, "Productos registrados", self.restaurante_servicio.contar_productos())

    def crear_tarjeta_resumen(self, contenedor, titulo, valor):
        tarjeta = tk.Frame(contenedor, bg=self.color_panel, padx=18, pady=16)
        tarjeta.pack(side="left", fill="x", expand=True, padx=(0, 14))

        tk.Label(
            tarjeta, text=titulo, bg=self.color_panel, fg=self.color_texto,
            font=("Arial", 10, "bold"),
        ).pack(anchor="w")
        tk.Label(
            tarjeta, text=str(valor), bg=self.color_panel, fg=self.color_resaltado,
            font=("Arial", 24, "bold"),
        ).pack(anchor="w", pady=(8, 0))

    # -------------------------------------------------------------------------
    # Vista de usuarios: solo consulta (no forma parte del CRUD de esta semana).
    # -------------------------------------------------------------------------
    def mostrar_usuarios(self):
        self.marcar_seccion("Usuarios")
        self.limpiar_contenido()

        assert self.contenido is not None

        self.crear_titulo_seccion("Usuarios registrados")
        listado = self.crear_listado(self.contenido, "Consulta de usuarios")
        self.tabla_usuarios = self.crear_tabla(
            listado,
            ("identificacion", "nombre", "usuario"),
            ("Identificación", "Nombre", "Usuario"),
        )
        self.refrescar_usuarios()

    def refrescar_usuarios(self):
        assert self.tabla_usuarios is not None

        self.limpiar_tabla(self.tabla_usuarios)
        for usuario in self.restaurante_servicio.listar_usuarios():
            self.tabla_usuarios.insert(
                "", tk.END, values=(usuario.identificacion, usuario.nombre, usuario.usuario),
            )
        self.actualizar_barra_estado()

    # -------------------------------------------------------------------------
    # Vista de productos: formulario + tabla + operaciones mediante botones.
    # -------------------------------------------------------------------------
    def mostrar_productos(self):
        self.marcar_seccion("Productos")
        self.limpiar_contenido()

        assert self.contenido is not None

        self.crear_titulo_seccion("Gestión de productos")

        cuerpo = tk.Frame(self.contenido, bg=self.color_fondo)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        formulario = tk.LabelFrame(
            cuerpo, text="Datos del producto", bg=self.color_panel, fg=self.color_encabezado,
            font=("Arial", 10, "bold"), padx=14, pady=14,
        )
        formulario.grid(row=0, column=0, sticky="n", padx=(0, 18))

        self.producto_codigo_entry = self.crear_campo(formulario, "Código", 0)
        self.producto_nombre_entry = self.crear_campo(formulario, "Nombre", 1)
        self.producto_categoria_entry = self.crear_campo(formulario, "Categoría", 2)
        self.producto_precio_entry = self.crear_campo(formulario, "Precio", 3)
        self.producto_stock_entry = self.crear_campo(formulario, "Stock", 4)

        acciones = tk.Frame(formulario, bg=self.color_panel)
        acciones.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        botones = (
            ("Registrar", self.registrar_producto, "Accion.TButton", "add.png"),
            ("Cargar por código", self.cargar_producto_en_formulario, "Secundario.TButton", "search.png"),
            ("Actualizar", self.actualizar_producto, "Accion.TButton", "edit.png"),
            ("Eliminar", self.eliminar_producto, "Eliminar.TButton", "delete.png"),
            ("Limpiar", self.limpiar_formulario_producto, "Secundario.TButton", "clean.png"),
        )

        for texto, comando, estilo, icono in botones:
            self.crear_boton(acciones, texto, comando, estilo, icono).pack(fill="x", pady=(0, 7))

        listado = self.crear_listado(cuerpo, "Productos registrados", usar_grid=True)
        self.tabla_productos = self.crear_tabla(
            listado,
            ("codigo", "nombre", "categoria", "precio", "stock"),
            ("Código", "Nombre", "Categoría", "Precio", "Stock"),
        )
        self.refrescar_productos()

    def obtener_datos_producto(self):
        assert self.producto_codigo_entry is not None
        assert self.producto_nombre_entry is not None
        assert self.producto_categoria_entry is not None
        assert self.producto_precio_entry is not None
        assert self.producto_stock_entry is not None

        return (
            self.producto_codigo_entry.get(),
            self.producto_nombre_entry.get(),
            self.producto_categoria_entry.get(),
            self.producto_precio_entry.get(),
            self.producto_stock_entry.get(),
        )

    def registrar_producto(self):
        try:
            self.restaurante_servicio.registrar_producto(*self.obtener_datos_producto())
            self.limpiar_formulario_producto()
            self.refrescar_productos()
            messagebox.showinfo("Productos", "Producto registrado correctamente.")
        except ValueError as error:
            messagebox.showerror("Productos", str(error))

    def cargar_producto_en_formulario(self):
        assert self.producto_codigo_entry is not None
        assert self.producto_nombre_entry is not None
        assert self.producto_categoria_entry is not None
        assert self.producto_precio_entry is not None
        assert self.producto_stock_entry is not None

        producto = self.restaurante_servicio.buscar_producto_por_codigo(self.producto_codigo_entry.get())
        if producto is None:
            messagebox.showerror("Productos", "No existe un producto con ese código.")
            return

        codigo_buscado = self.producto_codigo_entry.get()
        self.limpiar_formulario_producto()
        self.producto_codigo_entry.insert(0, codigo_buscado.strip())
        self.producto_nombre_entry.insert(0, producto.nombre)
        self.producto_categoria_entry.insert(0, producto.categoria)
        self.producto_precio_entry.insert(0, str(producto.precio))
        self.producto_stock_entry.insert(0, str(producto.stock))

    def actualizar_producto(self):
        try:
            codigo, nombre, categoria, precio, stock = self.obtener_datos_producto()
            self.restaurante_servicio.actualizar_producto(codigo, nombre, categoria, precio, stock)
            self.refrescar_productos()
            messagebox.showinfo("Productos", "Producto actualizado correctamente.")
        except ValueError as error:
            messagebox.showerror("Productos", str(error))

    def eliminar_producto(self):
        assert self.producto_codigo_entry is not None

        try:
            self.restaurante_servicio.eliminar_producto(self.producto_codigo_entry.get())
            self.limpiar_formulario_producto()
            self.refrescar_productos()
            messagebox.showinfo("Productos", "Producto eliminado correctamente.")
        except ValueError as error:
            messagebox.showerror("Productos", str(error))

    def limpiar_formulario_producto(self):
        entradas = (
            self.producto_codigo_entry, self.producto_nombre_entry,
            self.producto_categoria_entry, self.producto_precio_entry,
            self.producto_stock_entry,
        )
        for entrada in entradas:
            assert entrada is not None
            entrada.delete(0, tk.END)

    def refrescar_productos(self):
        assert self.tabla_productos is not None

        self.limpiar_tabla(self.tabla_productos)
        for producto in self.restaurante_servicio.listar_productos():
            self.tabla_productos.insert(
                "", tk.END,
                values=(
                    producto.codigo, producto.nombre, producto.categoria,
                    f"{producto.precio:.2f}", producto.stock,
                ),
            )
        self.actualizar_barra_estado()

    # -------------------------------------------------------------------------
    # Utilidades de interfaz compartidas por las vistas.
    # -------------------------------------------------------------------------
    def crear_titulo_seccion(self, texto):
        assert self.contenido is not None
        tk.Label(
            self.contenido, text=texto, bg=self.color_fondo, fg=self.color_encabezado,
            font=("Arial", 20, "bold"),
        ).pack(anchor="w", pady=(0, 16))

    def crear_campo(self, contenedor, etiqueta, fila):
        tk.Label(
            contenedor, text=etiqueta, bg=self.color_panel, fg=self.color_texto,
            font=("Arial", 10, "bold"),
        ).grid(row=fila, column=0, sticky="w", pady=(0, 8), padx=(0, 10))

        entrada = tk.Entry(contenedor, width=26, font=("Arial", 10))
        entrada.grid(row=fila, column=1, sticky="ew", pady=(0, 8))
        return entrada

    def crear_listado(self, contenedor, titulo, usar_grid=False):
        listado = tk.LabelFrame(
            contenedor, text=titulo, bg=self.color_panel, fg=self.color_encabezado,
            font=("Arial", 10, "bold"), padx=12, pady=12,
        )

        if usar_grid:
            listado.grid(row=0, column=1, sticky="nsew")
        else:
            listado.pack(fill="both", expand=True)

        return listado

    def crear_tabla(self, contenedor, columnas, encabezados):
        frame_tabla = tk.Frame(contenedor, bg=self.color_panel)
        frame_tabla.pack(fill="both", expand=True)

        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=12)
        barra = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)

        for columna, encabezado in zip(columnas, encabezados):
            tabla.heading(columna, text=encabezado)
            tabla.column(columna, width=120, anchor="w")

        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return tabla

    def limpiar_tabla(self, tabla):
        for item in tabla.get_children():
            tabla.delete(item)

    def cerrar_sesion(self):
        self.al_cerrar_sesion()