from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código de Barras")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (S/)")
    stock = models.IntegerField(default=0, verbose_name="Stock Disponible")
    stock_minimo = models.IntegerField(default=5, verbose_name="Stock Mínimo de Alerta")

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

class Venta(models.Model):
    cajero = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Cajero")
    fecha_venta = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total (S/)")

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha_venta.strftime('%d/%m/%Y %H:%M')}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE, verbose_name="Venta")
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, verbose_name="Producto")
    cantidad = models.IntegerField(verbose_name="Cantidad Vendida")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio en Venta")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")

    def __str__(self):
        return f"{self.producto.nombre} (x{self.cantidad}) en Venta #{self.venta.id}"