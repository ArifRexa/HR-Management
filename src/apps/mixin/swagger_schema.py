from drf_yasg.inspectors import SwaggerAutoSchema
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from sqlalchemy import all_


def swagger_tag_generator(tags=["default"]):
    def swagger_decorator(viewset_cls, name="default"):
        standard_actions = ["list", "retrieve", "create", "update", "partial_update", "destroy"]
        custom_actions = [action.__name__ for action in viewset_cls.get_extra_actions()]
        all_actions = standard_actions + custom_actions
        for action in all_actions:
            viewset_cls = method_decorator(
                swagger_auto_schema(tags=tags),
                name=action
            )(viewset_cls)
        return viewset_cls

class CustomSwaggerAutoSchema(SwaggerAutoSchema):
    def get_query_parameters(self):
        params = [
            param
            for param in super().get_query_parameters()
            if param not in ["created_at", "updated_at"]
        ]
        return params
