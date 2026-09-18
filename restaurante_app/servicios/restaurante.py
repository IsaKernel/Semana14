# servicios/restaurante.py
# Carga productos y usuarios desde ArchivoServicio y los convierte en
# objetos. Concentra las reglas de negocio y las validaciones: las
# vistas (ui/) nunca leen ni escriben productos.json directamente,
# solo piden operaciones a esta clase.
#
# Esta semana se incorpora la gestion completa de productos (registrar,
# consultar por codigo, actualizar, eliminar) manteniendo la consulta
# de usuarios y el acceso simulado ya existentes.

from modelos.producto import Producto
from modelos.usuario import Usuario


class Restaurante:
    def __init__(self, archivo_servicio):
        self.archivo_servicio = archivo_servicio
        self.productos = []
        self.usuarios = []
        self.cargar_datos()

    def cargar_datos(self):
        # Carga los datos persistidos y los convierte en objetos.
        productos_json = self.archivo_servicio.leer_json("productos.json")
        usuarios_json = self.archivo_servicio.leer_json("usuarios.json")

        self.productos = [
            Producto(
                datos.get("codigo", ""),
                datos.get("nombre", ""),
                datos.get("categoria", ""),
                datos.get("precio", 0),
                datos.get("stock", 0),
            )
            for datos in productos_json
        ]

        self.usuarios = [
            Usuario(
                datos.get("identificacion", ""),
                datos.get("nombre", ""),
                datos.get("correo", ""),
                datos.get("celular", ""),
                datos.get("usuario", ""),
                datos.get("contrasena", ""),
            )
            for datos in usuarios_json
        ]

    # ---------------- Usuarios (solo consulta) ----------------
    def cantidad_usuarios(self):
        return len(self.usuarios)

    def listar_usuarios(self):
        # Entrega los usuarios cargados para mostrarlos en la interfaz.
        return self.usuarios

    def validar_acceso(self, usuario, contrasena):
        """
        Simulación pedagógica de autenticación: compara usuario y
        contraseña contra los usuarios cargados. No representa un
        mecanismo de seguridad real (sin hash, sin sal, sin sesiones).
        """
        for usuario_registrado in self.usuarios:
            if (
                usuario_registrado.usuario == usuario
                and usuario_registrado.contrasena == contrasena
            ):
                return usuario_registrado
        return None

    # ---------------- Productos: persistencia ----------------
    def guardar_productos(self):
        datos = [producto.convertir_a_diccionario() for producto in self.productos]
        self.archivo_servicio.escribir_json("productos.json", datos)

    # ---------------- Productos: consulta ----------------
    def contar_productos(self):
        return len(self.productos)

    def listar_productos(self):
        # Entrega los productos cargados para mostrarlos en la interfaz.
        return self.productos

    def buscar_producto_por_codigo(self, codigo):
        codigo = (codigo or "").strip()
        for producto in self.productos:
            if producto.codigo == codigo:
                return producto
        return None

    # ---------------- Productos: conversion segura de numeros ----------------
    @staticmethod
    def _convertir_precio(valor):
        try:
            return float(valor)
        except (TypeError, ValueError):
            raise ValueError("El precio debe ser un número (ej: 4.50).")

    @staticmethod
    def _convertir_stock(valor):
        try:
            return int(valor)
        except (TypeError, ValueError):
            raise ValueError("El stock debe ser un número entero (ej: 10).")

    # ---------------- Productos: registro, actualizacion y eliminacion ----------------
    def registrar_producto(self, codigo, nombre, categoria, precio, stock):
        codigo_limpio = (codigo or "").strip()

        if self.buscar_producto_por_codigo(codigo_limpio) is not None:
            raise ValueError("Ya existe un producto con ese código.")

        precio_valido = self._convertir_precio(precio)
        stock_valido = self._convertir_stock(stock)

        nuevo_producto = Producto(codigo_limpio, nombre, categoria, precio_valido, stock_valido)

        self.productos.append(nuevo_producto)
        self.guardar_productos()
        return nuevo_producto

    def actualizar_producto(self, codigo, nombre, categoria, precio, stock):
        producto_actual = self.buscar_producto_por_codigo(codigo)

        if producto_actual is None:
            raise ValueError("No existe un producto con ese código.")

        precio_valido = self._convertir_precio(precio)
        stock_valido = self._convertir_stock(stock)

        # Se valida primero con un objeto temporal (reutiliza los mismos
        # setters de Producto) y solo si todo es valido se aplican los
        # cambios al objeto que ya esta en la lista/indice.
        datos_validados = Producto(producto_actual.codigo, nombre, categoria, precio_valido, stock_valido)

        producto_actual.nombre = datos_validados.nombre
        producto_actual.categoria = datos_validados.categoria
        producto_actual.precio = datos_validados.precio
        producto_actual.stock = datos_validados.stock

        self.guardar_productos()
        return producto_actual

    def eliminar_producto(self, codigo):
        producto_actual = self.buscar_producto_por_codigo(codigo)

        if producto_actual is None:
            raise ValueError("No existe un producto con ese código.")

        self.productos.remove(producto_actual)
        self.guardar_productos()
        return producto_actual