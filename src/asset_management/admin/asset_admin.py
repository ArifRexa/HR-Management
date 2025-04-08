from urllib.parse import urlparse

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.template.loader import get_template
from django.utils import timezone
from django.utils.html import format_html

from asset_management.models import (  # AssetCategory,
    Addition,
    Asset,
    AssetHead,
    AssetItem,
    Brand,
    EmployeeAsset,
    EmployeeAssignedAsset,
    Vendor,
)
from asset_management.models.asset import (
    AssetRequest,
    AssetRequestNote,
    AssetRequestStatus,
    AssetVariant,
    PriorityChoices,
)

# @admin.register(AssetCategory)
# class AssetCategoryAdmin(admin.ModelAdmin):
#     def has_module_permission(self, request):
#         return False


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    search_fields = ("name",)

    def has_module_permission(self, request):
        return False


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    search_fields = ("name",)

    def has_module_permission(self, request):
        return False


@admin.register(AssetHead)
class AssetHeadAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)

    def has_module_permission(self, request):
        return False


@admin.register(AssetItem)
class AssetItemAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)

    def has_module_permission(self, request):
        return False


class AdditionInline(admin.TabularInline):
    model = Addition
    extra = 1


@admin.register(AssetVariant)
class AssetVariantAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    def has_module_permission(self, request):
        return False


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "get_item_title",
        "code",
        # "category",
        "description",
        "is_active",
        "is_available",
        "colored_status",
    )
    autocomplete_fields = ("vendor", "brand", "variant")
    search_fields = (
        # "title",
        "code",
        "description",
        "status",
    )
    fields = (
        "head",
        "item",
        "vendor",
        "brand",
        "variant",
        "code",
        "date",
        "rate",
        "description",
        "is_available",
        "is_active",
        "status",
    )
    inlines = [AdditionInline]
    # exclude = ("head",)
    list_filter = (
        "status",
        "head",
        "vendor",
        "brand",
        "variant",
        "is_active",
        "is_available",
    )
    change_form_template = "admin/asset/asset_change_form.html"

    @admin.display(description="Title")
    def get_item_title(self, obj):
        return obj.item.title if obj.item else "-"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}

        if object_id:
            extra_context["assign_history"] = EmployeeAssignedAsset.objects.filter(
                asset_id=object_id
            ).order_by("-id")

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def get_search_results(self, request, queryset, search_term):
        qs, use_distinct = super().get_search_results(request, queryset, search_term)
        data = request.GET.dict()

        app_label = data.get("app_label")
        model_name = data.get("model_name")
        referer = request.META.get("HTTP_REFERER", "")

        if (
            request.user.is_authenticated
            and app_label == "asset_management"
            and model_name == "employeeassignedasset"
        ):
            if "asset_management/employeeasset" in referer:
                url_parts = urlparse(referer).path.split("/")
                if len(url_parts) >= 3:
                    employee_id = url_parts[-3]
                    assined_assets = list(
                        EmployeeAssignedAsset.objects.filter(
                            employee_id=employee_id
                        ).values_list("asset_id", flat=True)
                    )
                    qs = Asset.objects.filter(
                        Q(title__icontains=search_term)
                        | Q(code__icontains=search_term)
                        | Q(is_available=True)
                        | Q(id__in=assined_assets),
                    )
        return qs, use_distinct

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))

        # If user doesn't have permission to change status, make it read-only
        if not request.user.has_perm("asset_management.can_change_asset_status"):
            readonly_fields.append("status")

        return readonly_fields

    def save_model(self, request, obj, form, change):
        # Check if status field was changed
        if change and "status" in form.changed_data:
            # Verify permission before allowing status change
            if not request.user.has_perm("asset_management.can_change_asset_status"):
                raise PermissionDenied(
                    "You don't have permission to change asset status."
                )

        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        # Basic change permission
        has_perm = super().has_change_permission(request, obj)

        if not has_perm:
            return False

        # If trying to change status, check for specific permission
        if obj and "status" in request.POST:
            return request.user.has_perm("asset_management.can_change_asset_status")

        return True

    actions = ["make_pending", "make_approved"]

    def has_can_change_asset_status_permission(self, request):
        """
        Permission method for status change actions
        """
        return request.user.has_perm("asset_management.can_change_asset_status")

    @admin.action(
        description="Mark selected assets as Pending",
        permissions=["can_change_asset_status"],  # Requires this permission
    )
    def make_pending(self, request, queryset):
        if not request.user.has_perm("asset_management.can_change_asset_status"):
            self.message_user(
                request, "You don't have permission to change asset status."
            )
            return

        try:
            updated = queryset.update(status="pending")
            self.message_user(
                request, f"Successfully marked {updated} assets as Pending."
            )
        except Exception as e:
            self.message_user(request, f"Error changing status: {str(e)}")

    @admin.action(
        description="Mark selected assets as Approved",
        permissions=["can_change_asset_status"],  # Requires this permission
    )
    def make_approved(self, request, queryset):
        if not request.user.has_perm("asset_management.can_change_asset_status"):
            self.message_user(
                request, "You don't have permission to change asset status."
            )
            return

        try:
            updated = queryset.update(status="approved")
            self.message_user(
                request, f"Successfully marked {updated} assets as Approved."
            )
        except Exception as e:
            self.message_user(request, f"Error changing status: {str(e)}")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not self.has_can_change_asset_status_permission(request):
            if "make_pending" in actions:
                del actions["make_pending"]
            if "make_approved" in actions:
                del actions["make_approved"]
        return actions

    # @admin.display(description='Status')
    def colored_status(self, obj):
        colors = {"pending": "#FF0000", "approved": "#28a745"}  # Orange  # Green
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, "black"),
            obj.get_status_display(),
        )


# @admin.register(EmployeeAssignedAsset)
# class EmployeeAssignedAssetAdmin(admin.ModelAdmin):
#     list_display = ('employee', 'asset', 'get_asset_category', )
#     autocomplete_fields = ('asset', )
#     list_filter = (
#         'asset__category',
#         ('employee', admin.RelatedOnlyFieldListFilter),
#     )
#     search_fields = (
#         'employee__full_name',
#         'asset__title',
#         'asset__category__title',
#         'asset__code',
#     )

#     @admin.display(description="Category")
#     def get_asset_category(self, obj):
#         return obj.asset.category.title


class EmployeeAssignedAssetAdmin(admin.StackedInline):
    model = EmployeeAssignedAsset
    extra = 0
    autocomplete_fields = ("asset",)
    exclude = ("end_date",)

    def get_formset(self, request, obj=None, **kwargs):
        # Pass the parent instance (obj) to the formset
        self.parent_instance = obj
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "asset":
            # Use self.parent_instance to access the parent object
            if self.parent_instance:
                # Get the employee related to the parent instance
                employee = self.parent_instance
                # Find the last assigned asset for this employee
                last_assigned_asset = (
                    EmployeeAssignedAsset.objects.filter(employee=employee)
                    .order_by("-id")
                    .first()
                )
                # Determine if the last assigned asset is the current asset
                if last_assigned_asset:
                    last_asset_id = last_assigned_asset.asset_id
                else:
                    last_asset_id = None

                # Filter to include available assets or the last assigned asset
                kwargs["queryset"] = Asset.objects.filter(
                    Q(is_available=True) | Q(id=last_asset_id)
                )
            else:
                # If no parent instance, show only available assets
                kwargs["queryset"] = Asset.objects.filter(is_available=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# class EmployeeAssetCategoryFilter(admin.SimpleListFilter):
#     title = "Asset Category"
#     parameter_name = "employeeassignedasset__asset__category_id"

#     def lookups(self, request, model_admin):
#         objs = AssetCategory.objects.all()
#         lookups = [
#             (
#                 ac.id,
#                 ac.title,
#             )
#             for ac in objs
#         ]
#         return tuple(lookups)

#     def queryset(self, request, queryset):
#         value = self.value()
#         if value is not None:
#             return queryset.filter(employeeassignedasset__asset__category_id=value)
#         return queryset


@admin.register(EmployeeAsset)
class EmployeeAssetAdmin(admin.ModelAdmin):
    fields = (
        "full_name",
        "email",
    )
    readonly_fields = (
        "full_name",
        "email",
    )

    inlines = (EmployeeAssignedAssetAdmin,)

    list_display = (
        "full_name",
        "get_assets",
    )
    list_filter = (
        "full_name",
        # EmployeeAssetCategoryFilter,
    )

    @admin.display(description="Assigned Assets")
    def get_assets(self, obj):
        # print(dir(obj))
        assigned_assets = obj.assigned_assets.all()
        assets_str = "<br>".join(
            [
                f"{assignedasset.asset} | {assignedasset.asset.code}"
                for assignedasset in assigned_assets
            ]
        )
        return format_html(assets_str)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.filter(active=True)
        return qs


class AssetRequestNoteInline(admin.TabularInline):
    model = AssetRequestNote
    extra = 1


@admin.register(AssetRequest)
class AssetRequestAdmin(admin.ModelAdmin):
    inlines = (AssetRequestNoteInline,)
    list_display = (
        "category",
        "quantity",
        "get_notes",
        "get_priority",
        "requested_by",
        "requested_date",
        "get_status",
    )
    list_filter = ("category", "priority", "status")
    autocomplete_fields = ("category",)
    change_list_template = "admin/asset/asset_request.html"
    actions = [
        "update_status_done",
        "update_status_pending",
        "update_status_in_progress",
    ]

    def save_model(self, request, obj, form, change):
        if change:
            if obj.status == AssetRequestStatus.DONE:
                obj.approved_at = timezone.now()
        return super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        pending_info = self.get_queryset(request).aggregate(
            pending_count=Count("id", filter=Q(status=AssetRequestStatus.PENDING))
        )
        extra_context["has_pending_request"] = pending_info["pending_count"] > 0
        extra_context["pending_count"] = pending_info["pending_count"]
        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):

        return (
            super()
            .get_queryset(request)
            .select_related("category")
            .prefetch_related("asset_request_notes")
        )

    class Media:
        css = {"all": ("css/list.css",)}

    @admin.display(description="Due Days", ordering="created_at")
    def requested_date(self, obj):
        if obj.approved_at:
            due_days = obj.approved_at - obj.created_at.date()
            return due_days.days
        return (timezone.now().date() - obj.created_at.date()).days

    @admin.display(description="Priority", ordering="priority")
    def get_priority(self, obj):
        color = "green"
        if obj.priority == PriorityChoices.High:
            color = "red"
        elif obj.priority == PriorityChoices.MEDIUM:
            color = "blue"
        return format_html(
            f'<b style="color: {color}">{obj.get_priority_display()}</b>'
        )

    @admin.display(description="Status", ordering="status")
    def get_status(self, obj):
        color = "green"
        if obj.status == AssetRequestStatus.PENDING:
            color = "red"
        elif obj.status == AssetRequestStatus.IN_PROGRESS:
            color = "blue"
        return format_html(f'<b style="color: {color}">{obj.get_status_display()}</b>')

    @admin.action(description="Update Status To Done")
    def update_status_done(self, request, queryset):
        queryset.update(status=AssetRequestStatus.DONE)

    @admin.action(description="Update Status To Pending")
    def update_status_pending(self, request, queryset):
        queryset.update(status=AssetRequestStatus.PENDING)

    @admin.action(description="Update Status To In Progress")
    def update_status_in_progress(self, request, queryset):
        queryset.update(status=AssetRequestStatus.IN_PROGRESS)

    @admin.display(
        description="Requested By", ordering="created_by__employee__full_name"
    )
    def requested_by(self, obj):
        return obj.created_by.employee.full_name

    @admin.display(description="Notes")
    def get_notes(self, obj):
        if not obj.asset_request_notes.exists():
            return "-"
        html_template = get_template("admin/asset/col_note.html")

        html_content = html_template.render(
            {
                "note": obj.asset_request_notes.first(),
                "notes": obj.asset_request_notes.all(),
            }
        )

        return format_html(html_content)
