from rest_framework import serializers
from .models import DailyEntry

class DailyEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyEntry
        fields = [
            "id", "date", "time", "operator",
            "oxygen_purity", "pressure", "flow_rate", "pdp",
            "critical_flag", "alert_status", "notes",
            "technician_ack"   # ✅ add this field
        ]
