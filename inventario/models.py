from django.db import models

class Producto(models.Model):
    """Define la estructura de la tabla 'productos' en la base de datos."""
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código de Barras")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (S/)")
    stock = models.IntegerField(default=0, verbose_name="Stock Disponible")

    def __str__(self):
        """Representación amigable del objeto (ej. para el panel de administración)."""
        return f"{self.nombre} ({self.codigo})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']