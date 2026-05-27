from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .models import Message


@login_required
def chat_view(request):

    messages = Message.objects.all().order_by("timestamp")

    return render(request, "chat/chat.html", {
        "messages": messages,
        "username": request.user.username
    })


def logout_view(request):

    logout(request)

    return redirect("/")