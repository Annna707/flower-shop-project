from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'first_name', 'last_name', 'delivery_method',
        'payment_method', 'created', 'status', 'paid',
    ]
    list_filter = ['status', 'paid', 'delivery_method', 'payment_method', 'created']
    list_editable = ['status']
    inlines = [OrderItemInline]