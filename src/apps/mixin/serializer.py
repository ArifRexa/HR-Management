from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True
        ignore_exclude_fields = []

    def get_field_names(self, declared_fields, info):
        fields = list(super().get_field_names(declared_fields, info))
        always_exclude_fields = [
            "created_at",
            "updated_at",
        ]
        if hasattr(self.Meta, "ignore_exclude_fields"):
            always_exclude_fields = list(
                set(always_exclude_fields)
                - set(
                    self.Meta.ignore_exclude_fields,
                )
            )

        return [field for field in fields if field not in always_exclude_fields]
    
    
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
