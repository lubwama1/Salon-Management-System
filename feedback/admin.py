from django.contrib import admin
from .models import Feedback


class FeedBackAdmin(admin.ModelAdmin):
    list_display = ('user__username', 'service__name', 'rating', 'approved')


admin.site.register(Feedback, FeedBackAdmin)
