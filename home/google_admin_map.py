from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render


@staff_member_required(login_url="admin_login")
def google_admin_delivery_map(request):
    return render(request, "admin/delivery_command_center.html")
