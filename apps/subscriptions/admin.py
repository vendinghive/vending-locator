from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, PaymentHistory

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'searches_per_month', 'script_templates', 'regeneration_allowed']
    list_filter = ['regeneration_allowed']
    search_fields = ['name']

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'start_date', 'end_date', 'is_active', 'searches_used']
    list_filter = ['plan', 'is_active', 'start_date']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['start_date']

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'paypal_payment_id']
    readonly_fields = ['created_at']