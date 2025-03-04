from drf_yasg.inspectors import SwaggerAutoSchema


class CustomSwaggerAutoSchema(SwaggerAutoSchema):
    def get_query_parameters(self):
        params = [
            param
            for param in super().get_query_parameters()
            if param not in ["created_at", "updated_at"]
        ]
        return params
