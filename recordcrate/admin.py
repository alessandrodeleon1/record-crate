from django.contrib import admin

from .models import Item, Order_Item, Orders, Owns, Release, AuthUser


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "label", "year", "genre")
    search_fields = ("title", "artist", "label")
    list_filter = ("genre", "year")


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("item_id", "release_id", "physical_format")
    list_filter = ("physical_format",)
    search_fields = ("release_id__title", "release_id__artist")


@admin.register(Owns)
class OwnsAdmin(admin.ModelAdmin):
    list_display = ("user_id", "item_id")


class OrderItemInline(admin.TabularInline):
    model = Order_Item
    extra = 1


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "shipping_status",
        "placed_by_user_id",
        "received_by_user_id",
    )
    list_filter = ("shipping_status",)
    inlines = [OrderItemInline]

