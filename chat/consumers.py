import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.contrib.auth.models import User

from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.room_group_name = "chat_room"

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

        user = self.scope["user"]

        if data.get("typing"):

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_message",
                    "sender": user.username,
                }
            )

            return

        message = data["message"]

        await self.save_message(
            user.username,
            message
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": user.username,
            }
        )

    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
        }))

    async def typing_message(self, event):

        await self.send(text_data=json.dumps({
            "typing": True,
            "sender": event["sender"],
        }))

    @database_sync_to_async
    def save_message(self, username, message):

        user = User.objects.get(username=username)

        Message.objects.create(
            sender=user,
            content=message
        )