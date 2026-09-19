from django.shortcuts import render


def shipping_policy(request):
    return render(request, "legal/shipping.html")
