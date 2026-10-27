import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SiteSettings, ContactMessage


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    return render(request, "sitepages/home.html")


def about(request):
    return render(request, "sitepages/about.html")


def services(request):
    return render(request, "sitepages/services.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        message = request.POST.get("message", "").strip()
        if not name or not message:
            messages.error(request, "Please enter your name and message.")
            return redirect("sitepages:contact")
        ContactMessage.objects.create(
            name=name[:120],
            email=request.POST.get("email", "").strip()[:254],
            phone=request.POST.get("phone", "").strip()[:30],
            subject=request.POST.get("subject", "").strip()[:200],
            message=message,
        )
        messages.success(request, "JazakAllah! Your message has been received. Our office will get back to you shortly.")
        return redirect("sitepages:contact")
    return render(request, "sitepages/contact.html")
