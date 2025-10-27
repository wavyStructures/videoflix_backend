from django.contrib import admin
from .models import Video

# admin.site.register(Video)
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')

