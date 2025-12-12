from django.contrib.admin import SimpleListFilter
from django.db import models


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



#
# class CategoryCountFilter(SimpleListFilter):
#     title = "By Category"
#     parameter_name = "category"
#
#     def lookups(self, request, model_admin):
#         qs = model_admin.get_queryset(request)
#
#         # Category-wise counts
#         data = (
#             qs.values("category__id", "category__name")
#               .order_by("category__name")
#         )
#
#         # Build lookup list
#         results = []
#         counted = {}   # to accumulate counts
#
#         for item in data:
#             cid = item["category__id"]
#             name = item["category__name"]
#             if cid:
#                 counted.setdefault(cid, {"name": name, "count": 0})
#                 counted[cid]["count"] += 1
#
#         # Return (id, "Name (count)") pairs
#         return [
#             (cid, f"{info['name']} ({info['count']})")
#             for cid, info in counted.items()
#         ]
#
#     def choices(self, changelist):
#         """
#         Modify default All label → All (total)
#         Django 3.2 compatible
#         """
#         qs = changelist.queryset
#         total = qs.count()
#
#         for choice in super().choices(changelist):
#             # Detect the default "All"
#             if choice["query_string"].endswith("&category=") or choice["query_string"] == "?":
#                 choice["display"] = f"All ({total})"
#             yield choice
#
#     def queryset(self, request, queryset):
#         value = self.value()
#         if value:
#             return queryset.filter(category_id=value)
#         return queryset
#

from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html


class CategoryCountFilter(SimpleListFilter):
    title = "By Category"
    parameter_name = "category"

    def lookups(self, request, model_admin):
        # Return a dummy lookup to ensure the filter is displayed.
        # The real choices are generated in `choices()`.
        return [("__dummy__", "Loading...")]

    def choices(self, changelist):
        # Get the CURRENT filtered queryset (after is_active, search, etc.)
        qs = changelist.queryset

        # Total count for "All"
        total = qs.count()

        # Build category counts from filtered qs
        category_counts = (
            qs.filter(category__isnull=False)
            .values("category__id", "category__name")
            .annotate(count=models.Count("category__id"))
            .order_by("category__name")
        )

        # Build a dict for quick lookup
        cat_dict = {
            str(item["category__id"]): {
                "name": item["category__name"],
                "count": item["count"]
            }
            for item in category_counts
        }

        # Current selected value (if any)
        current_value = self.value()

        # Yield "All" choice
        yield {
            "selected": current_value is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": format_html("All ({})", total),
        }

        # Yield each category
        for cat_id, info in sorted(cat_dict.items(), key=lambda x: x[1]["name"]):
            yield {
                "selected": current_value == cat_id,
                "query_string": changelist.get_query_string({self.parameter_name: cat_id}),
                "display": format_html("{} ({})", info["name"], info["count"]),
            }

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(category_id=value)
        return queryset


