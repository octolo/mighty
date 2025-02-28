from django.db import models


def ImmutabledModel(**kwargs):
    def decorator(obj):
        obj.immutable_config = kwargs
        obj.immutable_bypass = False
        obj.add_to_class(
            'immutable',
            models.BooleanField(default=kwargs.get('immutable', False)),
        )
        obj.add_to_class(
            'immutable_delete',
            models.BooleanField(default=kwargs.get('delete', True)),
        )
        obj.add_to_class(
            'immutable_fields',
            models.TextField(
                default=kwargs.get('fields', '*'),
                blank=kwargs.get('blank', True),
                null=kwargs.get('null', True),
            ),
        )

        def add_immutable_fields_editable(self, fields):
            self.immutable_fields = ','.join(fields)

        obj.add_immutable_fields_editable = add_immutable_fields_editable

        @property
        def immutable_fields_editable(self):
            base = ('immutable', 'immutable_delete')
            return base + tuple(
                field
                for field in self.immutable_fields.split(',')
                if hasattr(self, field)
            )

        obj.immutable_fields_editable = immutable_fields_editable

        @property
        def can_be_changed(self):
            if self.immutable and not self.immutable_bypass:
                if self.immutable_fields == '*':
                    return True
                return all(
                    field in self.immutable_fields_editable
                    for field in self.fields_changed
                )
            return True

        obj.can_be_changed = can_be_changed

        @property
        def can_be_deleted(self):
            if hasattr(obj, 'immutable_custom'):
                return self.immutable_custom
            return (
                not self.immutable
                or self.immutable_bypass
                or self.immutable_delete
            )

        obj.can_be_deleted = can_be_deleted

        return obj

    return decorator
