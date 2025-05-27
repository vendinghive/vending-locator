from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import GeneratedScript
from apps.subscriptions.models import UserSubscription  # Add this import

@login_required
def toolkit_dashboard(request):
    """Dashboard view for the sales toolkit"""
    try:
        recent_scripts = GeneratedScript.objects.filter(user=request.user)[:5]
    except:
        recent_scripts = []
    
    context = {
        'recent_scripts': recent_scripts
    }
    return render(request, 'toolkit/dashboard.html', context)

# @login_required
# @require_POST
# def generate_script(request):
#     """Generate a sales script (simplified version for now)"""
#     return JsonResponse({
#         'success': False,
#         'error': 'Script generation functionality coming soon!'
#     })


@login_required
@require_POST
def generate_script(request):
    """Generate a sales script"""
    try:
        # Check subscription
        try:
            subscription = UserSubscription.objects.get(user=request.user)
            if not subscription.is_active or subscription.is_expired():
                return JsonResponse({
                    'success': False,
                    'error': 'No active subscription found.'
                })
        except UserSubscription.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No active subscription found.'
            })
        
        # Get parameters
        script_type = request.POST.get('script_type', 'cold_call')
        location_name = request.POST.get('location_name', '').strip()
        location_category = request.POST.get('location_category', '').strip()
        machine_type = request.POST.get('machine_type', '').strip()
        
        if not all([location_name, location_category, machine_type]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters.'
            })
        
        # Generate script
        from .services import ScriptGeneratorService
        service = ScriptGeneratorService()
        
        if script_type == 'cold_call':
            script_content = service.generate_cold_call_script(location_name, location_category, machine_type)
        elif script_type == 'email':
            script_content = service.generate_email_template(location_name, location_category, machine_type)
        elif script_type == 'in_person':
            script_content = service.generate_in_person_script(location_name, location_category, machine_type)
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid script type.'
            })
        
        # Save generated script
        generated_script = GeneratedScript.objects.create(
            user=request.user,
            script_type=script_type,
            location_name=location_name,
            location_category=location_category,
            machine_type=machine_type,
            script_content=script_content
        )
        
        return JsonResponse({
            'success': True,
            'script_content': script_content,
            'script_id': generated_script.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })
    
@login_required
def script_history(request):
    """View script history"""
    try:
        scripts = GeneratedScript.objects.filter(user=request.user)
    except:
        scripts = []
    
    context = {
        'scripts': scripts
    }
    return render(request, 'toolkit/script_history.html', context)