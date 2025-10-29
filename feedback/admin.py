from django.contrib import admin
from .models import Feedback, FeedbackModalDismissal


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at', 'updated_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'feedback_text')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(FeedbackModalDismissal)
class FeedbackModalDismissalAdmin(admin.ModelAdmin):
    list_display = ('user', 'dismissed_at', 'journal_count_at_dismissal')
    list_filter = ('dismissed_at',)
    search_fields = ('user__username',)
    readonly_fields = ('dismissed_at',)
    ordering = ('-dismissed_at',)
