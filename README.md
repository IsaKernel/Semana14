# restaurante_app — Semana 14: Componentes y contenedores

**Estudiante:** Cueva Ochoa Sabrina Isabel 
**Asignatura:** Programación Orientada a Objetos
**Actividad:** Semana 14 — Componentes y contenedores

Continuación del proyecto `restaurante_app` a partir de la base gráfica de la Semana 13. Esta semana la interfaz evoluciona de dos pantallas simples (login + panel con solo lectura) a una aplicación organizada con **navegación lateral**, **formularios**, **tablas** y **operaciones completas sobre productos** (registrar, consultar por código, actualizar, eliminar), todo mediante componentes y contenedores de Tkinter/ttk. Los usuarios se mantienen como información de solo consulta.

## Estructura del proyecto

```
restaurante_app/
├── datos/
│   ├── productos.json
│   └── usuarios.json
├── modelos/
│   ├── __init__.py
│   ├── producto.py
│   └── usuario.py
├── servicios/
│   ├── __init__.py
│   ├── archivo_servicio.py
│   └── restaurante.py
├── ui/
│   ├── __init__.py
│   ├── login_view.py
│   └── main_view.py
├── assets/
│   ├── icons/          (add.png, search.png, edit.png, delete.png, clean.png,
│   │                     home.png, users.png, productos.png, logout.png)
│   └── logo/            (logo.png, icono.png)
├── main.py
└── README.md
```

`assets/` es opcional: si las imágenes no están presentes, `login_view.py` y `main_view.py` simplemente omiten el logo/los iconos y muestran los botones con texto, sin romper la aplicación.

## Responsabilidad de cada archivo

- **`modelos/producto.py` y `modelos/usuario.py`** — solo representan la entidad y validan sus propios campos mediante `@property`, reutilizando un `@staticmethod validar_texto()` compartido para los campos de texto obligatorios (igual patrón que el proyecto docente). No tienen `__str__` ni conocen JSON: la conversión a diccionario para persistir vive en el servicio, no en el modelo.
- **`servicios/archivo_servicio.py`** — genérico: solo `leer_json(nombre_archivo)` y `escribir_json(nombre_archivo, datos)`. No cambió esta semana.
- **`servicios/restaurante.py`** — carga productos y usuarios, y concentra **todas** las reglas de negocio: validaciones, duplicados, conversión segura de texto a número, y persistencia (`guardar_productos()` arma el diccionario de cada producto directamente en el servicio). Las vistas nunca validan ni escriben JSON, solo llaman a estos métodos.
- **`ui/login_view.py`** — acceso simulado, sin cambios funcionales; ahora carga un logo opcional desde `assets/logo/logo.png`.
- **`ui/main_view.py`** — reestructurada por completo: sidebar de navegación (Inicio, Usuarios, Productos, Cerrar sesión) + área de contenido que cambia según la sección activa.
- **`main.py`** — ventana ampliada (920x560), con icono opcional cargado desde `assets/logo/icono.png`.

## Componentes y contenedores utilizados

| Elemento | Uso en la interfaz |
|---|---|
| `tk.Frame` | Sidebar de navegación, área de contenido, barra de estado, cada tarjeta de resumen |
| `tk.LabelFrame` | Agrupa visualmente el formulario ("Datos del producto") y cada tabla ("Productos registrados", "Consulta de usuarios") |
| `ttk.Treeview` | Tabla de productos (código, nombre, categoría, precio, stock) y tabla de usuarios (identificación, nombre, usuario) |
| `ttk.Scrollbar` | Acompaña cada `Treeview`, vinculada con `yscrollcommand`/`command=tabla.yview` |
| `tk.Entry` | Campos del formulario de productos (código, nombre, categoría, precio, stock) |
| `ttk.Button` con `command=` | Registrar, Cargar por código, Actualizar, Eliminar, Limpiar, navegación del sidebar, cerrar sesión |
| `grid()` | Organiza el formulario internamente (etiqueta + campo por fila) y la distribución formulario/tabla dentro de la sección de Productos |
| `pack()` | Organiza el sidebar, el área de contenido y los elementos que se apilan verticalmente (botones del menú, tarjetas de resumen) |

Se usó `grid()` donde se necesitaba alinear pares etiqueta-campo o dos columnas (formulario a la izquierda, tabla a la derecha), y `pack()` donde bastaba apilar elementos en una dirección — ninguno de los dos gestor se usó "por costumbre", sino según lo que la sección necesitaba organizar.

## Gestión de productos: operaciones implementadas

Todas viven en `Restaurante`, no en los botones de `main_view.py`:

```python
def registrar_producto(self, codigo, nombre, categoria, precio, stock):
    precio_valido = self._convertir_precio(precio)
    stock_valido = self._convertir_stock(stock)
    nuevo_producto = Producto(codigo, nombre, categoria, precio_valido, stock_valido)

    if self.buscar_producto_por_codigo(nuevo_producto.codigo) is not None:
        raise ValueError("Ya existe un producto con ese código.")

    self.productos.append(nuevo_producto)
    self.guardar_productos()
    return nuevo_producto
```

- **Registrar**: convierte precio/stock a número y crea el `Producto` primero (así se validan todos los campos mediante sus `@property`), y solo después revisa si el código ya existe.
- **Cargar/consultar por código**: `buscar_producto_por_codigo()` llena el formulario con los datos actuales para poder editarlos.
- **Actualizar**: construye un `Producto` temporal con los nuevos valores (reutilizando las mismas validaciones) y solo si es válido copia los campos al objeto real, sin perder su lugar en la lista.
- **Eliminar**: busca por código y lo remueve de la lista.
- Las cuatro operaciones llaman a `guardar_productos()` al final, que arma el diccionario de cada producto y reescribe `productos.json` completo mediante `archivo_servicio.escribir_json()`.
- Si algo falla (código duplicado, código inexistente, precio o stock no numéricos, campo vacío), se lanza `ValueError` con un mensaje claro; `main_view.py` lo captura y lo muestra con `messagebox.showerror()`, sin que la vista decida por sí misma si el dato es válido.

## Flujo de la aplicación

```
Inicio de la aplicación
        ↓
main.py prepara Tkinter y crea ArchivoServicio + Restaurante
        ↓
LoginView
        ↓
Restaurante.validar_acceso()
        ↓
MainView (sidebar + contenido)
        ↓
Inicio (resumen) | Usuarios (consulta) | Productos (formulario + tabla)
        ↓
Registrar | Cargar por código | Actualizar | Eliminar
        ↓
Restaurante procesa la operación y valida
        ↓
guardar_productos() → productos.json
        ↓
Se refresca la tabla de productos
        ↓
Cerrar sesión → LoginView
```

## Ejecución

Desde la carpeta `restaurante_app/`:

```bash
python main.py
```

## Credenciales de prueba

| Usuario | Contraseña |
|---------|-----------|
| sebas   | hope1     |
| isa     | hope2     |

> El acceso es una simulación pedagógica; no representa un mecanismo de autenticación seguro.

## Pruebas realizadas

- **Inicio sin errores** y acceso con `sebas`/`hope1` funcionando igual que la semana anterior.
- **Consulta de usuarios**: la tabla muestra identificación, nombre y usuario de cada registro de `usuarios.json`.
- **Registrar producto**: se agregó un producto nuevo y apareció inmediatamente en la tabla y en `productos.json`.
- **Código duplicado**: se intentó registrar un código ya existente y la operación fue rechazada con un mensaje claro, sin modificar la lista.
- **Cargar por código**: se consultó un producto existente y el formulario se llenó con sus datos actuales.
- **Actualizar**: se modificaron nombre, categoría, precio y stock de un producto, y los cambios se reflejaron en la tabla y en el archivo.
- **Precio/stock inválidos**: se intentó actualizar con texto no numérico en precio y stock; la operación fue rechazada sin tocar el producto original.
- **Eliminar**: se eliminó un producto y dejó de aparecer en la tabla y en `productos.json`.
- **Persistencia real**: se cerró el proceso y se volvió a ejecutar; los cambios en productos se mantuvieron.
- **Separación de responsabilidades**: se verificó que `main_view.py` nunca abre `productos.json`/`usuarios.json` directamente ni contiene reglas de validación — todo pasa por `Restaurante`.

## Reflexión

Pasar de un panel que solo mostraba información a uno que además la modifica cambió la forma de pensar la interfaz, ya no es suficiente  con recorrer una lista y pintar etiquetas, sino que cada sección necesitaba su propio contenedor con una responsabilidad clara — un `LabelFrame` para agrupar el formulario, otro para la tabla, y un `Frame` de sidebar que se mantiene fijo mientras el contenido central cambia. Organizar el formulario de productos con `grid()` en vez de apilarlo con `pack()` fue una decisión concreta a alinear etiqueta y campo en la misma fila solo es cómodo con una cuadrícula, mientras que la lista de botones de acción sí se beneficiaba de simplemente apilarse con `pack()`. La otra lección fue dónde no debía vivir la lógica, ya que cada botón dispara un método corto en la vista (`registrar_producto`, `actualizar_producto`) que solo recoge lo que el usuario escribió y llama al servicio; toda decisión sobre si un dato es válido —código duplicado, precio no numérico, producto inexistente— sigue viviendo en `Restaurante`, exactamente donde vivía antes de que existiera ningún botón.