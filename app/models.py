from django.db import models
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories"
    )
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("category", "name")

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Season(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Summer, Winter

    def __str__(self):
        return self.name



# Size model


class Size(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=5, blank=True, null=True)

    ORDER = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]

    class Meta:
        ordering = []  # remove default ordering

    def order_index(self):
        try:
            return self.ORDER.index(self.code)
        except ValueError:
            return 999  # unknown size goes last

    def __str__(self):
        return self.code or self.name

class SizeAndFit(models.Model):
    name = models.CharField(max_length=100)   # Regular Fit, Slim Fit, Oversized
    description = models.TextField(blank=True)

    def __str__(self):
        return self.description


class CompositionAndCare(models.Model):
    name = models.CharField(max_length=100)   # 100% Cotton, Hand Wash, etc
    description = models.TextField(blank=True)

    def __str__(self):
        return self.description


class DeliveryAndReturn(models.Model):
    name = models.CharField(max_length=100)   # Free Delivery, 7 Days Return
    description = models.TextField(blank=True)

    def __str__(self):
        return self.description


class Product(models.Model):
    name = models.CharField(max_length=200)

    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    product_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True)

    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True)

    image_url = models.URLField(max_length=500, blank=True, null=True)

    color = models.CharField(max_length=50,null=True)
    fabric = models.CharField(max_length=100,null=True)  # Cotton, Polyester, etc.

    price = models.DecimalField(max_digits=10, decimal_places=2)

    ratings = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0
    )  # Example: 4.5

    size_and_fit = models.ForeignKey(
        SizeAndFit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    composition_and_care = models.ForeignKey(
        CompositionAndCare,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    delivery_and_return = models.ForeignKey(
        DeliveryAndReturn,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )


    is_available_for_cod = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Stock per product & size
class ProductStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size')  # one stock entry per size per product

    def __str__(self):
        return f"{self.product.name} - {self.size.name} ({self.stock})"



# ✅ New: Multiple images model
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500, blank=True, null=True)  # Changed from ImageField to URLField
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_feature = models.BooleanField(default=False)  # Optionally mark one image as main

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"


