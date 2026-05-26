from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseForbidden
from .models import Message


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if user.username not in settings.ALLOWED_USERS:
                return HttpResponseForbidden("Access denied")

            login(request, user)

            return redirect("chat")

        return render(request, "chat/login.html", {
            "error": "Invalid username or password"
        })

    return render(request, "chat/login.html")


@login_required
def chat_view(request):

    if request.user.username not in settings.ALLOWED_USERS:
        return HttpResponseForbidden("Access denied")

    messages = Message.objects.order_by("timestamp")

    Message.objects.filter(
        receiver=request.user,
        seen=False
    ).update(seen=True)

    return render(request, "chat/chat.html", {
        "username": request.user.username,
        "messages": messages,
    })


def logout_view(request):

    logout(request)

    return redirect("login")