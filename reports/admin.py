from django.contrib import admin

from .models import GeneratedReport


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ("report_type", "requested_by", "generated_at")
    list_filter = ("report_type",)
