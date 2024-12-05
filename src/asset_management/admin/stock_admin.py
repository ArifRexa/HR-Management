from django.contrib import admin


from asset_management.models import Unit, Product, Stock


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ("title", "unit__title")
    list_display = ("title", "current_stock")

    @admin.display()
    def current_stock(self, obj):
        return f"{obj.current_stock} {obj.unit}"

    def has_module_permission(self, request):
        return False


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    search_fields = ("note", "product__title", "employee__full_name")
    list_display = ("date", "employee", "product", "get_quantity", "note", "type")
    list_filter = ("type", "product")
    date_hierarchy = "date"

    # change_list_template = 'admin/stock/list.html'
    #
    # def changelist_view(self, request, extra_context=None):
    #     qs = self.get_queryset(request).filter(**simple_request_filter(request))
    #     my_context = {
    #         'in': qs.filter(type__exact='in').aggregate(score=Coalesce(Sum('quantity'), 0.0))['score'],
    #         'out': qs.filter(type__exact='out').aggregate(score=Coalesce(Sum('quantity'), 0.0))['score']
    #     }
    #     return super(StockAdmin, self).changelist_view(request, extra_context=my_context)

    @admin.display(description="Quantity")
    def get_quantity(self, obj):
        return f"{obj.quantity} {obj.product.unit}"

    def has_module_permission(self, request):
        return False
