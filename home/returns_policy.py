from django.shortcuts import render


def returns_policy(request):
    return render(request, "legal/returns.html")
