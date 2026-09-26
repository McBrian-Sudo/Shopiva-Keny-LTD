def delivery_signup(request):
    """Create a delivery-partner application; staff approval is required before deliveries are accessible."""
    if request.user.is_authenticated:
        if _agent(request):
            return redirect("delivery_portal")
        if request.user.is_staff or request.user.is_superuser:
            return redirect("/admin/")

    if request.method == "POST":
        form = DeliveryRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
            except IntegrityError:
                form.add_error("username", "This account could not be created because the username or email already exists.")
            else:
                return render(request, "delivery/signup_success.html", {"username": user.username, "email": user.email})
    else:
        form = DeliveryRegistrationForm()

    return render(request, "delivery/signup.html", {"form": form})


def delivery_login(request):
    if request.user.is_authenticated:
        if _agent(request):
            return redirect("delivery_portal")
        if request.user.is_staff or request.user.is_superuser:
            return redirect("/admin/")
        logout(request)

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        try:
            agent = user.delivery_agent_profile
        except DeliveryAgent.DoesNotExist:
            form.add_error(None, "This account is not registered as a Shopiva delivery partner.")
        else:
            if not agent.is_active:
                form.add_error(None, "Your staff application is registered and awaiting administrator verification.")
            else:
                login(request, agent.user)
                agent.status = "on_delivery" if agent.orders.filter(status="out_for_delivery").exists() else "available"
                agent.save(update_fields=["status"])
                return redirect("delivery_portal")

    return render(request, "delivery/login.html", {"form": form})
