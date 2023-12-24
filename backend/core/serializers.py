from rest_framework import serializers


class BaseBankSerializer(serializers.ModelSerializer):

    class Meta:
        model = None
        exclude = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by', 'deleted_by')

    def create(self, validated_data):
        if self.Meta.model is None:
            raise NotImplementedError(_('BaseBankSerializer must be subclassed with a model'))
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if self.Meta.model is None:
            raise NotImplementedError(_('BaseBankSerializer must be subclassed with a model'))
        return super().update(instance, validated_data)
