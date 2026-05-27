import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.contrib.auth.models import User
from django.conf import settings

from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_group_name = "private_chat"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):

        data = json.loads(text_data)

        message = data["message"]

        sender = self.user

        users = list(
            User.objects.filter(
                username__in=settings.ALLOWED_USERS
            )
        )

        receiver = users[0] if users[1] == sender else users[1]

        await self.save_message(
            sender,
            receiver,
            message
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender.username,
            }
        )

    async def chat_message(self, event):

        await self.send(
            text_data=json.dumps({
                "message": event["message"],
                "sender": event["sender"],
            })
        )

    @database_sync_to_async
    def save_message(self, sender, receiver, message):

        Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=message
        )