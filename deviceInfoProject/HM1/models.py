from django.db import models
from django.utils import timezone

class Alert(models.Model):
    SOURCE_CHOICES = (
        ('HM1', 'HM1'),
        ('HM2', 'HM2'),
    )

    alert_type = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=3, choices=SOURCE_CHOICES)  # Add source field

    def __str__(self):
        return f"{self.alert_type} - {self.message}"
    
    def resolve(self):
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.save()
