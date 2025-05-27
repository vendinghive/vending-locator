from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.subscriptions.models import UserSubscription
from .models import SearchHistory, LocationData
from .services import LocationFinderService
import json

@login_required
def dashboard_view(request):
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        context = {
            'subscription': subscription,
            'can_search': subscription.can_search(),
            'searches_remaining': subscription.plan.searches_per_month - subscription.searches_used
        }
    except UserSubscription.DoesNotExist:
        context = {
            'subscription': None,
            'can_search': False,
            'searches_remaining': 0
        }
    
    return render(request, 'locator/dashboard.html', context)


# @login_required
# @require_POST
# def search_locations(request):
#     try:
#         # Check subscription
#         try:
#             subscription = UserSubscription.objects.get(user=request.user)
#             if not subscription.can_search():
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Search limit reached or subscription expired. Please upgrade your plan.'
#                 })
#         except UserSubscription.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'No active subscription found. Please subscribe to a plan.'
#             })
        
#         # Get search parameters
#         zip_code = request.POST.get('zip_code', '').strip()
#         machine_type = request.POST.get('machine_type', '')
        
#         if not zip_code or not machine_type:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Please provide both zip code and machine type.'
#             })
        
#         if not zip_code.isdigit() or len(zip_code) != 5:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Please enter a valid 5-digit zip code.'
#             })
        
#         # Initialize location finder
#         finder = LocationFinderService()
        
#         # Validate zip code
#         if not finder.validate_zip_code(zip_code):
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Zip code not found. Please enter a valid US zip code.'
#             })
        
#         # Get coordinates
#         coords = finder.get_coordinates_from_zip(zip_code)
#         if not coords:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Unable to get coordinates for this zip code.'
#             })
        
#         lat, lon = coords
        
#         # Find nearby places
#         places = finder.find_nearby_places(lat, lon, machine_type)
        
#         if not places:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'No suitable locations found in this area.'
#             })
        
#         # Use search credit
#         subscription.use_search()
        
#         # Save search history
#         search_history = SearchHistory.objects.create(
#             user=request.user,
#             zip_code=zip_code,
#             machine_type=machine_type,
#             results_count=len(places)
#         )
        
#         # Save location data
#         for place in places:
#             LocationData.objects.create(
#                 search_history=search_history,
#                 name=place['name'],
#                 category=place['category'],
#                 address=place['address'],
#                 latitude=place['lat'],
#                 longitude=place['lon'],
#                 phone=place.get('phone', ''),
#                 email=place.get('email', ''),
#                 business_hours=place.get('business_hours', ''),
#                 foot_traffic=place.get('foot_traffic', 'Low')
#             )
        
#         return JsonResponse({
#             'success': True,
#             'places': places,
#             'searches_remaining': subscription.plan.searches_per_month - subscription.searches_used
#         })
        
#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'error': f'An error occurred: {str(e)}'
#         })


@login_required
@require_POST
def search_locations(request):
    try:
        # Check subscription
        try:
            subscription = UserSubscription.objects.get(user=request.user)
            if not subscription.can_search():
                return JsonResponse({
                    'success': False,
                    'error': 'Search limit reached or subscription expired. Please upgrade your plan.'
                })
        except UserSubscription.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No active subscription found. Please subscribe to a plan.'
            })
        
        # Get search parameters
        zip_code = request.POST.get('zip_code', '').strip()
        machine_type = request.POST.get('machine_type', '')
        radius = request.POST.get('radius', '')
        
        if not zip_code or not machine_type or not radius:
            return JsonResponse({
                'success': False,
                'error': 'Please provide zip code, machine type, and radius.'
            })
        
        if not zip_code.isdigit() or len(zip_code) != 5:
            return JsonResponse({
                'success': False,
                'error': 'Please enter a valid 5-digit zip code.'
            })
        
        # Initialize location finder
        finder = LocationFinderService()
        
        # Validate zip code
        if not finder.validate_zip_code(zip_code):
            return JsonResponse({
                'success': False,
                'error': 'Zip code not found. Please enter a valid US zip code.'
            })
        
        # Get coordinates
        coords = finder.get_coordinates_from_zip(zip_code)
        if not coords:
            return JsonResponse({
                'success': False,
                'error': 'Unable to get coordinates for this zip code.'
            })
        
        lat, lon = coords
        
        # Find nearby places
        places = finder.find_nearby_places(lat, lon, machine_type, int(radius))
        
        if not places:
            return JsonResponse({
                'success': False,
                'error': 'No suitable locations found in this area.'
            })
        
        # Use search credit
        subscription.use_search()
        
        # Save search history
        search_history = SearchHistory.objects.create(
            user=request.user,
            zip_code=zip_code,
            machine_type=machine_type,
            results_count=len(places)
        )
        
        # Save location data (remove foot_traffic)
        for place in places:
            LocationData.objects.create(
                search_history=search_history,
                name=place['name'],
                category=place['category'],
                address=place['address'],
                latitude=place['lat'],
                longitude=place['lon'],
                phone=place.get('phone', ''),
                email=place.get('email', ''),
                business_hours=place.get('business_hours', '')
            )
        
        return JsonResponse({
            'success': True,
            'places': places,
            'searches_remaining': subscription.plan.searches_per_month - subscription.searches_used
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })
    
@login_required
def search_history_view(request):
    searches = SearchHistory.objects.filter(user=request.user)[:10]
    return render(request, 'locator/search_history.html', {'searches': searches})