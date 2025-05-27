from django.db import models
from django.conf import settings

class GeneratedScript(models.Model):
    SCRIPT_TYPES = [
        ('cold_call', 'Cold Call'),
        ('email', 'Email'),
        ('in_person', 'In Person'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    script_type = models.CharField(max_length=20, choices=SCRIPT_TYPES)
    location_name = models.CharField(max_length=255)
    location_category = models.CharField(max_length=100)
    machine_type = models.CharField(max_length=50)
    script_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.script_type} - {self.location_name}"