from django.db import models
from django.conf import settings
from datetime import datetime, timedelta

class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('pro', 'Pro'),
        ('elite', 'Elite'),
    ]
    
    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    searches_per_month = models.IntegerField()
    leads_per_search = models.CharField(max_length=10)  # e.g., "10-15"
    script_templates = models.IntegerField()
    regeneration_allowed = models.BooleanField(default=False)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.get_name_display()} - ${self.price}/month"

class UserSubscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    searches_used = models.IntegerField(default=0)
    paypal_subscription_id = models.CharField(max_length=100, blank=True)
    
    #def save(self, *args, **kwargs):
    def save(self, *args, **kwargs):
        if not self.end_date:
            from django.utils import timezone
            self.end_date = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)
            # if not self.end_date:
        #     self.end_date = self.start_date + timedelta(days=30)
        # super().save(*args, **kwargs)
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.end_date
        
    def can_search(self):
        return self.is_active and not self.is_expired() and self.searches_used < self.plan.searches_per_month
    
    def use_search(self):
        if self.can_search():
            self.searches_used += 1
            self.save()
            return True
        return False
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

class PaymentHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paypal_payment_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount} - {self.status}"