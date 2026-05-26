import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        if user.username not in settings.ALLOWED_USERS:
            await self.close()
            return

        self.room_name = "private_chat"

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data["message"]
        sender = self.scope["user"]

        # ✅ Save message safely
        await self.save_message(sender, message_text)

        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",
                "message": message_text,
                "sender": sender.username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # 🔐 DB access MUST be here
    @database_sync_to_async
    def save_message(self, sender, message_text):
        from django.contrib.auth.models import User
        from .models import Message

        users = list(User.objects.filter(username__in=settings.ALLOWED_USERS))
        receiver = users[0] if users[1] == sender else users[1]

        Message.objects.create(
            sender=sender,
            receiver=receiver,
            text=message_text
        )
