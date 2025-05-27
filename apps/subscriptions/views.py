# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import SubscriptionPlan, UserSubscription

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import SubscriptionPlan, UserSubscription, PaymentHistory
import paypalrestsdk
from django.conf import settings


def plans_view(request):
    plans = SubscriptionPlan.objects.all().order_by('price')
    return render(request, 'subscriptions/plans.html', {'plans': plans})

# Configure PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox or live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})



# @login_required
# def subscribe_view(request, plan_id):
#     plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
#     if plan.name == 'free':
#         # Handle free plan
#         subscription, created = UserSubscription.objects.get_or_create(
#             user=request.user,
#             defaults={'plan': plan}
#         )
#         if not created:
#             subscription.plan = plan
#             subscription.searches_used = 0
#             subscription.is_active = True
#             subscription.save()
        
#         messages.success(request, 'Successfully subscribed to Free plan!')
#         return redirect('locator:dashboard')
    
#     # For paid plans, redirect to plans for now (PayPal integration can be added later)
#     messages.info(request, 'Paid plans coming soon! Using free plan for now.')
#     return redirect('subscriptions:plans')








# @login_required
# def subscribe_view(request, plan_id):
#     plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
#     # Check if user already has this plan
#     try:
#         current_subscription = UserSubscription.objects.get(user=request.user)
#         if current_subscription.plan.id == plan_id:
#             messages.error(request, f'You are already subscribed to the {plan.get_name_display()} plan!')
#             return redirect('subscriptions:plans')
        
#         # Check if trying to downgrade to free from paid plan
#         if plan.name == 'free' and current_subscription.plan.price > 0:
#             messages.error(request, 'Cannot downgrade to free plan. Please contact support.')
#             return redirect('subscriptions:plans')
            
#     except UserSubscription.DoesNotExist:
#         current_subscription = None
    
#     if plan.name == 'free':
#         # Only allow free plan if no current subscription
#         if current_subscription is None:
#             subscription = UserSubscription.objects.create(
#                 user=request.user,
#                 plan=plan
#             )
#             messages.success(request, 'Successfully subscribed to Free plan!')
#             return redirect('locator:dashboard')
#         else:
#             messages.error(request, 'You already have an active subscription!')
#             return redirect('subscriptions:plans')
    
#     # For paid plans - implement basic PayPal (simplified)
#     if current_subscription:
#         # Update existing subscription
#         current_subscription.plan = plan
#         current_subscription.searches_used = 0  # Reset searches on upgrade
#         current_subscription.is_active = True
#         current_subscription.save()
#         messages.success(request, f'Successfully upgraded to {plan.get_name_display()} plan!')
#     else:
#         # Create new subscription
#         UserSubscription.objects.create(
#             user=request.user,
#             plan=plan
#         )
#         messages.success(request, f'Successfully subscribed to {plan.get_name_display()} plan!')
    
#     return redirect('locator:dashboard')


@login_required
def subscribe_view(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    # Check if user already has this plan
    try:
        current_subscription = UserSubscription.objects.get(user=request.user)
        if current_subscription.plan.id == plan_id:
            messages.error(request, f'You are already subscribed to the {plan.get_name_display()} plan!')
            return redirect('subscriptions:plans')
    except UserSubscription.DoesNotExist:
        current_subscription = None
    
    if plan.name == 'free':
        # Only allow free plan if no current subscription
        if current_subscription is None:
            subscription = UserSubscription.objects.create(
                user=request.user,
                plan=plan
            )
            messages.success(request, 'Successfully subscribed to Free plan!')
            return redirect('locator:dashboard')
        else:
            messages.error(request, 'You already have an active subscription!')
            return redirect('subscriptions:plans')
    
    # For paid plans - PayPal integration
    try:
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": request.build_absolute_uri(f"/subscriptions/payment/success/?plan_id={plan_id}"),
                "cancel_url": request.build_absolute_uri("/subscriptions/payment/cancel/")
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"{plan.get_name_display()} Plan",
                        "sku": plan.name,
                        "price": str(plan.price),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(plan.price),
                    "currency": "USD"
                },
                "description": f"Subscription to {plan.get_name_display()} plan"
            }]
        })
        
        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    request.session['payment_id'] = payment.id
                    return redirect(link.href)
        else:
            messages.error(request, 'Failed to create PayPal payment. Please try again.')
            
    except Exception as e:
        messages.error(request, f'PayPal error: {str(e)}')
    
    return redirect('subscriptions:plans')

@login_required
def payment_cancel(request):
    messages.warning(request, 'Payment was cancelled.')
    return redirect('subscriptions:plans')





@login_required
def payment_success(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    plan_id = request.GET.get('plan_id')
    
    if payment_id and payer_id and plan_id:
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            if payment.execute({"payer_id": payer_id}):
                plan = get_object_or_404(SubscriptionPlan, id=plan_id)
                
                # Create or update subscription
                subscription, created = UserSubscription.objects.get_or_create(
                    user=request.user,
                    defaults={'plan': plan}
                )
                if not created:
                    subscription.plan = plan
                    subscription.searches_used = 0
                    subscription.is_active = True
                    subscription.save()
                
                messages.success(request, f'Successfully subscribed to {plan.get_name_display()} plan!')
                return redirect('locator:dashboard')
        except Exception as e:
            messages.error(request, f'Payment processing error: {str(e)}')
    
    messages.error(request, 'Payment verification failed.')
    return redirect('subscriptions:plans')