from rest_framework.serializers import ModelSerializer
from mighty.models import Missive

class MissiveSerializer(ModelSerializer):
    class Meta:
        model = Missive
        fields = (
            "uid",
            "status",
            "name",
            "sender",
            "reply",
            "reply_name",
            "target",
            "html",
            "txt",
        )
