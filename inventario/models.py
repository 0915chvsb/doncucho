from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre del Proveedor")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Email de Contacto")
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Categoría")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código de Barras")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de Venta (S/)")
    stock_minimo = models.IntegerField(default=5, verbose_name="Stock Mínimo de Alerta")
    
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoría")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proveedor")

    def __str__(self):
        return self.nombre

    @property
    def stock_total(self):
        stock = self.lotes.filter(fecha_vencimiento__gt=timezone.now(), stock_lote__gt=0).aggregate(Sum('stock_lote'))['stock_lote__sum']
        return stock or 0

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

class Lote(models.Model):
    producto = models.ForeignKey(Producto, related_name='lotes', on_delete=models.CASCADE, verbose_name="Producto")
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Precio de Compra (S/)")
    stock_lote = models.IntegerField(default=0, verbose_name="Stock de este Lote")
    fecha_ingreso = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Ingreso")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento")

    def __str__(self):
        return f"Lote de {self.producto.nombre} - Vence: {self.fecha_vencimiento}"

    class Meta:
        ordering = ['fecha_vencimiento']

class Venta(models.Model):
    cajero = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Cajero")
    fecha_venta = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total (S/)")

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha_venta.strftime('%d/%m/%Y %H:%M')}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE, verbose_name="Venta")
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, verbose_name="Producto")
    lote_origen = models.ForeignKey(Lote, on_delete=models.SET_NULL, null=True, verbose_name="Lote de Origen")
    cantidad = models.IntegerField(verbose_name="Cantidad Vendida")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio en Venta")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")

    def __str__(self):
        return f"{self.producto.nombre} (x{self.cantidad}) en Venta #{self.venta.id}"