from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Feedback(models.Model):
    """
    Model to store user feedback and ratings for the app
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    feedback_text = models.TextField(
        blank=True,
        null=True,
        help_text="Optional feedback text"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
    
    def __str__(self):
        return f"{self.user.username} - {self.rating} stars - {self.created_at.strftime('%Y-%m-%d')}"


class FeedbackModalDismissal(models.Model):
    """
    Track when users dismiss the feedback modal to avoid showing it too frequently
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='modal_dismissals')
    dismissed_at = models.DateTimeField(auto_now_add=True)
    journal_count_at_dismissal = models.IntegerField(
        default=0,
        help_text="Number of journals user had when they dismissed the modal"
    )
    
    class Meta:
        ordering = ['-dismissed_at']
        verbose_name = 'Modal Dismissal'
        verbose_name_plural = 'Modal Dismissals'
    
    def __str__(self):
        return f"{self.user.username} dismissed at {self.dismissed_at.strftime('%Y-%m-%d %H:%M')}"
