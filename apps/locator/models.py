from django.db import models
from django.conf import settings

class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    zip_code = models.CharField(max_length=10)
    machine_type = models.CharField(max_length=50)
    results_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.zip_code} - {self.machine_type}"

class LocationData(models.Model):
    search_history = models.ForeignKey(SearchHistory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    business_hours = models.CharField(max_length=200, blank=True)
    foot_traffic = models.CharField(max_length=20, default='Low')  # Low, Moderate, High
    
    def __str__(self):
        return f"{self.name} - {self.category}"