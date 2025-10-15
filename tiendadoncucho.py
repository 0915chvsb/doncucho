import tkinter as tk
import sqlite3
import os
import sys
from tkinter import messagebox

# -----------------------------------------------------------
# Función para obtener un directorio permanente para guardar la BD.
def get_data_directory():
    if sys.platform == "win32":
        # En Windows se usa APPDATA (Roaming)
        appdata = os.environ.get("APPDATA")
        if appdata:
            data_dir = os.path.join(appdata, "InventarioApp")
        else:
            data_dir = os.path.expanduser("~")
    else:
        # En otros sistemas se usa una carpeta oculta en el home
        data_dir = os.path.join(os.path.expanduser("~"), ".inventario_app")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

base_dir = get_data_directory()
db_path = os.path.join(base_dir, "inventario.db")
print(f"Base de datos: {db_path}")
# SQLite creará la BD si no existe al conectarse.
# -----------------------------------------------------------

class InventarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Inventario")
        self.root.state('zoomed')
        
        # Conexión y creación de la tabla si no existe.
        try:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    precio REAL NOT NULL
                )
            ''')
            self.conn.commit()
            print(f"Base de datos guardada en: {db_path}")
        except Exception as e:
            messagebox.showerror("Error en Base de Datos", f"No se pudo conectar a SQLite.\n{e}")
        
        self.carrito = {}
        
        # Frame de botones principales
        frame_botones = tk.Frame(root)
        frame_botones.pack(fill="x", padx=10, pady=10)
        
        btn_agregar = tk.Button(frame_botones, text="Agregar Producto", 
                                command=self.agregar_producto, font=("Arial", 20))
        btn_agregar.pack(side="left", padx=5)
        
        btn_ver_productos = tk.Button(frame_botones, text="Ver Inventario", 
                                      command=self.mostrar_inventario, font=("Arial", 20), bg="lightblue")
        btn_ver_productos.pack(side="left", padx=5)
        
        btn_buscar_producto = tk.Button(frame_botones, text="Buscar Producto", 
                                        command=self.abrir_buscar_producto, font=("Arial", 20))
        btn_buscar_producto.pack(side="right", padx=5)
        
        frame_limpiar = tk.Frame(root)
        frame_limpiar.pack(fill="x", padx=10, pady=(0,10))
        
        btn_limpiar = tk.Button(frame_limpiar, text="Limpiar Carrito", 
                                command=self.limpiar_carrito, font=("Arial", 20))
        btn_limpiar.pack(side="left", padx=5)
        
        tk.Label(root, text="Escanear/Ingresar Código de Barras:", font=("Arial", 20)).pack()
        self.codigo_entry = tk.Entry(root, font=("Arial", 20))
        self.codigo_entry.pack()
        self.codigo_entry.focus()
        self.codigo_entry.bind("<Return>", self.buscar_producto)
        
        # Frame para la lista del carrito
        frame_lista = tk.Frame(root)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=(10,15))
        self.canvas_carrito = tk.Canvas(frame_lista, bg="white", bd=2, relief="sunken")
        self.canvas_carrito.pack(side="left", fill="both", expand=True)
        scrollbar_carrito = tk.Scrollbar(frame_lista, orient="vertical", command=self.canvas_carrito.yview)
        scrollbar_carrito.pack(side="right", fill="y")
        self.canvas_carrito.configure(yscrollcommand=scrollbar_carrito.set)
        self.frame_carrito = tk.Frame(self.canvas_carrito, bg="white")
        self.canvas_carrito.create_window((0,0), window=self.frame_carrito, anchor="nw")
        self.frame_carrito.bind("<Configure>", lambda event: self.canvas_carrito.configure(scrollregion=self.canvas_carrito.bbox("all")))
        self.label_total = tk.Label(root, text="", font=("Arial", 25), fg="green")
        self.label_total.pack(pady=5)
    
    # ----------------------------
    # Métodos de la aplicación
    # ----------------------------
    
    def buscar_producto(self, event):
        codigo = self.codigo_entry.get()
        try:
            self.cursor.execute("SELECT nombre, precio FROM productos WHERE codigo = ?", (codigo,))
            producto = self.cursor.fetchone()
            if producto:
                nombre, precio = producto
                if codigo in self.carrito:
                    self.carrito[codigo]["cantidad"] += 1
                    self.carrito[codigo]["total"] = self.carrito[codigo]["cantidad"] * self.carrito[codigo]["precio"]
                else:
                    self.carrito[codigo] = {"nombre": nombre, "precio": precio, "cantidad": 1, "total": precio}
                self.actualizar_lista_carrito()
            else:
                messagebox.showerror("Producto inexistente", "El código ingresado no está registrado.")
        except Exception as e:
            messagebox.showerror("Error en búsqueda", f"No se pudo buscar el producto.\n{e}")
        self.codigo_entry.delete(0, tk.END)
    
    def actualizar_lista_carrito(self):
        for widget in self.frame_carrito.winfo_children():
            widget.destroy()
        header_frame = tk.Frame(self.frame_carrito, bg="white")
        header_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(header_frame, text="Producto", font=("Arial", 20), bg="white", width=25, anchor="w").pack(side="left", padx=10)
        tk.Label(header_frame, text="Cantidad", font=("Arial", 20), bg="white", width=15, anchor="w").pack(side="left", padx=10)
        tk.Label(header_frame, text="Precio Total", font=("Arial", 20), bg="white", width=15, anchor="w").pack(side="left", padx=10)
        # Se recorre el diccionario de carrito
        for codigo, producto in self.carrito.items():
            row_frame = tk.Frame(self.frame_carrito, bg="white")
            row_frame.pack(fill="x", padx=5, pady=2)
            tk.Label(row_frame, text=producto['nombre'], font=("Arial", 20), bg="white", width=25, anchor="w").pack(side="left", padx=10)
            tk.Label(row_frame, text=str(producto['cantidad']), font=("Arial", 20), bg="white", width=15, anchor="w").pack(side="left", padx=10)
            tk.Label(row_frame, text=f"S/{producto['total']:.2f}", font=("Arial", 20), bg="white", width=15, anchor="w").pack(side="left", padx=10)
            # Se agrega un botón "X" para quitar el producto del carrito.
            tk.Button(row_frame, text="X", font=("Arial", 20), fg="red",
                      command=lambda c=codigo: self.quitar_producto(c)).pack(side="left", padx=10)
        total_amount = sum(prod['total'] for prod in self.carrito.values())
        self.label_total.config(text=f"Monto Total: S/{total_amount:.2f}")
    
    def quitar_producto(self, codigo):
        """Elimina el producto con el código dado del carrito y actualiza la lista."""
        if codigo in self.carrito:
            del self.carrito[codigo]
            self.actualizar_lista_carrito()
    
    def limpiar_carrito(self):
        self.carrito = {}
        self.actualizar_lista_carrito()
        messagebox.showinfo("Carrito", "Todos los productos han sido eliminados.")
    
    def mostrar_inventario(self):
        ventana_inventario = tk.Toplevel(self.root)
        ventana_inventario.title("Inventario de Productos")
        ventana_inventario.state('zoomed')
        
        tk.Label(ventana_inventario, text="Lista de Productos", font=("Arial", 20)).pack(pady=10)
        lista_inventario = tk.Listbox(ventana_inventario, font=("Arial", 16))
        lista_inventario.pack(fill="both", expand=True, padx=20, pady=10)
        try:
            self.cursor.execute("SELECT codigo, nombre, precio FROM productos")
            productos = self.cursor.fetchall()
            for producto in productos:
                codigo, nombre, precio = producto
                lista_inventario.insert(tk.END, f"{codigo} - {nombre} - Precio: S/{precio:.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el inventario.\n{e}")
        
        frame_opciones = tk.Frame(ventana_inventario)
        frame_opciones.pack(pady=10)
        btn_editar = tk.Button(frame_opciones, text="Editar Producto", font=("Arial", 20),
                                command=self.abrir_editar_producto)
        btn_editar.pack(side="left", padx=10)
        btn_eliminar = tk.Button(frame_opciones, text="Eliminar Producto", font=("Arial", 20),
                                  command=self.abrir_eliminar_producto)
        btn_eliminar.pack(side="left", padx=10)
    
    def abrir_buscar_producto(self):
        ventana_buscar = tk.Toplevel(self.root)
        ventana_buscar.title("Buscar Producto")
        ventana_buscar.geometry("600x400")
        
        tk.Label(ventana_buscar, text="Ingrese palabras clave:", font=("Arial", 20)).pack(pady=10)
        entry_buscar = tk.Entry(ventana_buscar, font=("Arial", 20))
        entry_buscar.pack(pady=10, fill="x", padx=20)
        entry_buscar.focus()  # Foco automático en el Entry
        entry_buscar.bind("<Return>", lambda event: self.realizar_busqueda_producto(entry_buscar.get(), ventana_buscar))
        
        tk.Button(ventana_buscar, text="Buscar", font=("Arial", 20),
                  command=lambda: self.realizar_busqueda_producto(entry_buscar.get(), ventana_buscar)).pack(pady=10)
        lista_resultados = tk.Listbox(ventana_buscar, font=("Arial", 20))
        lista_resultados.pack(fill="both", expand=True, padx=20, pady=10)
        ventana_buscar.lista_resultados = lista_resultados
    
    def realizar_busqueda_producto(self, palabras, ventana):
        try:
            self.cursor.execute("SELECT codigo, nombre, precio FROM productos WHERE nombre LIKE ?", ('%' + palabras + '%',))
            resultados = self.cursor.fetchall()
            ventana.lista_resultados.delete(0, tk.END)
            if resultados:
                for r in resultados:
                    codigo, nombre, precio = r
                    ventana.lista_resultados.insert(tk.END, f"{codigo} - {nombre} - Precio: S/{precio:.2f}")
            else:
                ventana.lista_resultados.insert(tk.END, "No se encontraron resultados.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar la búsqueda.\n{e}")
    
    def abrir_editar_producto(self):
        ventana_editar = tk.Toplevel(self.root)
        ventana_editar.title("Editar Producto")
        ventana_editar.geometry("500x300")
        tk.Label(ventana_editar, text="Ingrese Código de Barras:", font=("Arial", 20)).pack(pady=10)
        codigo_entry = tk.Entry(ventana_editar, font=("Arial", 20))
        codigo_entry.pack()
        codigo_entry.focus_set()  # Foco automático
        tk.Button(ventana_editar, text="Buscar", font=("Arial", 20),
                  command=lambda: self.buscar_editar_producto(codigo_entry.get(), ventana_editar)).pack(pady=10)
        codigo_entry.bind("<Return>", lambda event: self.buscar_editar_producto(codigo_entry.get(), ventana_editar))
    
    def buscar_editar_producto(self, codigo, ventana_editar):
        try:
            self.cursor.execute("SELECT nombre, precio FROM productos WHERE codigo = ?", (codigo,))
            producto = self.cursor.fetchone()
            if producto:
                nombre, precio = producto
                for widget in ventana_editar.winfo_children():
                    widget.destroy()
                tk.Label(ventana_editar, text=f"Editar Producto {codigo}", font=("Arial", 20)).pack(pady=10)
                
                tk.Label(ventana_editar, text="Nombre:", font=("Arial", 20)).pack()
                nombre_entry = tk.Entry(ventana_editar, font=("Arial", 20))
                nombre_entry.pack()
                nombre_entry.insert(0, nombre)
                nombre_entry.focus_set()  # Asigna foco automáticamente al Entry de Nombre
                nombre_entry.bind("<Return>", lambda event: precio_entry.focus_set())
                
                tk.Label(ventana_editar, text="Precio:", font=("Arial", 20)).pack()
                precio_entry = tk.Entry(ventana_editar, font=("Arial", 20))
                precio_entry.pack()
                precio_entry.insert(0, str(precio))
                precio_entry.bind("<Return>", lambda event: self.guardar_cambios_producto(codigo, nombre_entry.get(), precio_entry.get(), ventana_editar))
                
                tk.Button(ventana_editar, text="Guardar Cambios", font=("Arial", 20),
                          command=lambda: self.guardar_cambios_producto(codigo, nombre_entry.get(), precio_entry.get(), ventana_editar)
                          ).pack(pady=10)
            else:
                messagebox.showerror("Error", "Producto no encontrado.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar el producto.\n{e}")
    
    def guardar_cambios_producto(self, codigo, nuevo_nombre, nuevo_precio, ventana_editar):
        if nuevo_nombre and nuevo_precio.replace(".", "").isdigit():
            try:
                self.cursor.execute("UPDATE productos SET nombre = ?, precio = ? WHERE codigo = ?", 
                                      (nuevo_nombre, float(nuevo_precio), codigo))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
                ventana_editar.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el producto.\n{e}")
        else:
            messagebox.showerror("Error", "Datos inválidos, revise el nombre y el precio.")
    
    def abrir_eliminar_producto(self):
        ventana_eliminar = tk.Toplevel(self.root)
        ventana_eliminar.title("Eliminar Producto")
        ventana_eliminar.geometry("500x300")
        tk.Label(ventana_eliminar, text="Ingrese Código de Barras:", font=("Arial", 20)).pack(pady=10)
        codigo_entry = tk.Entry(ventana_eliminar, font=("Arial", 20))
        codigo_entry.pack()
        codigo_entry.focus_set()  # Foco automático
        tk.Button(ventana_eliminar, text="Buscar", font=("Arial", 20),
                  command=lambda: self.buscar_eliminar_producto(codigo_entry.get(), ventana_eliminar)
                  ).pack(pady=10)
        codigo_entry.bind("<Return>", lambda event: self.buscar_eliminar_producto(codigo_entry.get(), ventana_eliminar))
    
    def buscar_eliminar_producto(self, codigo, ventana_eliminar):
        try:
            self.cursor.execute("SELECT nombre, precio FROM productos WHERE codigo = ?", (codigo,))
            producto = self.cursor.fetchone()
            if producto:
                nombre, precio = producto
                for widget in ventana_eliminar.winfo_children():
                    widget.destroy()
                tk.Label(ventana_eliminar, text=f"Eliminar Producto {codigo}", font=("Arial", 20)).pack(pady=10)
                tk.Label(ventana_eliminar, text=f"Nombre: {nombre}", font=("Arial", 20)).pack(pady=5)
                tk.Label(ventana_eliminar, text=f"Precio: S/{precio:.2f}", font=("Arial", 20)).pack(pady=5)
                # Se pasa el nombre para usarlo en la confirmación.
                btn_eliminar = tk.Button(ventana_eliminar, text="Eliminar Producto", font=("Arial", 20),
                              command=lambda: self.eliminar_producto(nombre, codigo, ventana_eliminar))
                btn_eliminar.pack(pady=10)
                btn_eliminar.focus_set()  # Foco en el botón para que al presionar Enter se active
                btn_eliminar.bind("<Return>", lambda event: self.eliminar_producto(nombre, codigo, ventana_eliminar))
            else:
                messagebox.showerror("Error", "Producto no encontrado.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar el producto.\n{e}")
    
    def eliminar_producto(self, nombre, codigo, ventana_eliminar):
        respuesta = messagebox.askyesno("Confirmación", f"¿Está seguro que desea eliminar el producto '{nombre}'?")
        if respuesta:
            try:
                self.cursor.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
                ventana_eliminar.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el producto.\n{e}")
    
    def agregar_producto(self):
        ventana_agregar = tk.Toplevel(self.root)
        ventana_agregar.title("Agregar Producto")
        ventana_agregar.geometry("500x350")
        
        tk.Label(ventana_agregar, text="Código de Barras:", font=("Arial", 18)).pack(pady=10)
        codigo_entry = tk.Entry(ventana_agregar, font=("Arial", 18), relief="solid", bd=1)
        codigo_entry.pack(pady=5)
        codigo_entry.focus_set()
        
        tk.Label(ventana_agregar, text="Nombre del Producto:", font=("Arial", 18)).pack(pady=10)
        nombre_entry = tk.Entry(ventana_agregar, font=("Arial", 18), relief="solid", bd=1)
        nombre_entry.pack(pady=5)
        
        tk.Label(ventana_agregar, text="Precio:", font=("Arial", 18)).pack(pady=10)
        precio_entry = tk.Entry(ventana_agregar, font=("Arial", 18), relief="solid", bd=1)
        precio_entry.pack(pady=5)
        
        # Navegación secuencial con Enter:
        codigo_entry.bind("<Return>", lambda event: nombre_entry.focus_set())
        nombre_entry.bind("<Return>", lambda event: precio_entry.focus_set())
        precio_entry.bind("<Return>", lambda event: self.guardar_producto(codigo_entry.get(), nombre_entry.get(), precio_entry.get(), ventana_agregar))
        
        tk.Button(ventana_agregar, text="Guardar", font=("Arial", 18),
                  command=lambda: self.guardar_producto(codigo_entry.get(), nombre_entry.get(), precio_entry.get(), ventana_agregar)
                  ).pack(pady=20)
    
    def guardar_producto(self, codigo, nombre, precio, ventana_agregar):
        if codigo and nombre and precio.replace(".", "").isdigit():
            try:
                self.cursor.execute("SELECT codigo FROM productos WHERE codigo = ?", (codigo,))
                existente = self.cursor.fetchone()
                if existente:
                    messagebox.showerror("Error", "Ya existe un producto con este código de barras.")
                else:
                    self.cursor.execute("INSERT INTO productos (codigo, nombre, precio) VALUES (?, ?, ?)",
                                        (codigo, nombre, float(precio)))
                    self.conn.commit()
                    messagebox.showinfo("Éxito", "Producto agregado correctamente.")
                    ventana_agregar.destroy()
            except Exception as e:
                messagebox.showerror("Error en guardado", f"No se pudo agregar el producto.\n{e}")
        else:
            messagebox.showerror("Error", "Datos inválidos, verifica que el precio sea un número.")

# -----------------------------------------------------------
# Crear la ventana principal y ejecutar la aplicación.
root = tk.Tk()
app = InventarioApp(root)
root.mainloop()
