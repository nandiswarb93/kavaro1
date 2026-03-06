from django.contrib import admin

from django.contrib import admin
from .models import (
    Brand, ProductType, Category, SubCategory,
    Season, Size, Product, ProductStock, ProductImage, SizeAndFit,
    CompositionAndCare,
    DeliveryAndReturn
)




@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(SizeAndFit)
class SizeAndFitAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(CompositionAndCare)
class CompositionAndCareAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(DeliveryAndReturn)
class DeliveryAndReturnAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductStockInline(admin.TabularInline):
    model = ProductStock
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "brand", "category", "sub_category",
        "price", "ratings", "size_and_fit",
        "composition_and_care",
        "delivery_and_return", "is_available_for_cod"
    )
    list_filter = ("brand", "category", "season", "is_available_for_cod")
    search_fields = ("name", "brand__name")
    inlines = [ProductImageInline, ProductStockInline]
