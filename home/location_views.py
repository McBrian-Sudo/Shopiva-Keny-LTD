from django.http import JsonResponse

from .models import ShopivaBranch, ShopivaOutlet


def shopiva_locations(request):
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "GET required."}, status=405)

    county = request.GET.get("county", "").strip()
    town = request.GET.get("town", "").strip()

    branches = ShopivaBranch.objects.filter(is_active=True)
    outlets = ShopivaOutlet.objects.filter(is_active=True).select_related("branch")

    if county:
        branches = branches.filter(county__iexact=county)
        outlets = outlets.filter(county__iexact=county)
    if town:
        branches = branches.filter(town__icontains=town)
        outlets = outlets.filter(town__icontains=town)

    return JsonResponse({
        "ok": True,
        "branches": [
            {
                "id": item.id,
                "name": item.name,
                "code": item.code,
                "county": item.county,
                "town": item.town,
                "address": item.address,
                "phone": item.phone,
                "email": item.email,
                "latitude": str(item.latitude) if item.latitude is not None else None,
                "longitude": str(item.longitude) if item.longitude is not None else None,
                "opening_time": item.opening_time.isoformat() if item.opening_time else None,
                "closing_time": item.closing_time.isoformat() if item.closing_time else None,
                "services": item.services,
                "is_headquarters": item.is_headquarters,
            }
            for item in branches.order_by("county", "town", "name")
        ],
        "outlets": [
            {
                "id": item.id,
                "name": item.name,
                "code": item.code,
                "branch_id": item.branch_id,
                "branch_name": item.branch.name if item.branch else None,
                "county": item.county,
                "town": item.town,
                "address": item.address,
                "phone": item.phone,
                "email": item.email,
                "latitude": str(item.latitude) if item.latitude is not None else None,
                "longitude": str(item.longitude) if item.longitude is not None else None,
                "opening_time": item.opening_time.isoformat() if item.opening_time else None,
                "closing_time": item.closing_time.isoformat() if item.closing_time else None,
                "services": item.services,
                "pickup_available": item.pickup_available,
            }
            for item in outlets.order_by("county", "town", "name")
        ],
    })
