from django.contrib import admin
from .models import DailyEntry

@admin.register(DailyEntry)
class DailyEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'operator', 'oxygen_purity', 'pressure', 'flow_rate', 'pdp', 'alert_status', 'critical_flag')
    list_filter = ('alert_status', 'critical_flag', 'date')
    search_fields = ('operator__username',)
