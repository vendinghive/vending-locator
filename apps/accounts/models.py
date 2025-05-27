from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def lock_account(self):
        self.is_locked = True
        self.save()
    
    def unlock_account(self):
        self.is_locked = False
        self.failed_login_attempts = 0
        self.save()
    
    def increment_failed_attempts(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 3:
            self.lock_account()
        self.save()
    
    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.save()