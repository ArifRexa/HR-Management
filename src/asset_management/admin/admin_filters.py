from django.contrib.admin import SimpleListFilter


class ActiveStatusFilter(SimpleListFilter):
    title = "is active"
    parameter_name = "is_active"

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        active = qs.filter(is_active=True).count()
        inactive = qs.filter(is_active=False).count()

        # Only "Yes" and "No" — we will override "All" separately
        return [
            ("1", f"Yes ({active})"),
            ("0", f"No ({inactive})"),
        ]

    def choices(self, changelist):
        """
        Override the default 'All' label.
        Works in Django 3.2 (no changelist.request).
        """
        # Get queryset from changelist safely in Django 3.2
        qs = changelist.queryset
        total = qs.count()

        # DEFAULT choices are returned by parent
        for choice in super().choices(changelist):
            # Identify the default "All" option
            if choice["query_string"].endswith("&is_active=") or choice["query_string"] == "?":
                choice["display"] = f"All ({total})"
            yield choice

    def queryset(self, request, queryset):
        value = self.value()
        if value == "1":
            return queryset.filter(is_active=True)
        if value == "0":
            return queryset.filter(is_active=False)
        return queryset
