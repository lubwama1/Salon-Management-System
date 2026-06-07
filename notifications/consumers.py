

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
            return
        self.group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        await self.close()

    async def notification_message(self, event):
        print("Notification received:", event)
        await self.send(text_data=json.dumps({
            'notification_id': event['notification_id'],
            'sender': event['sender'],
            'sender_role': event['sender_role'],
            'message': event['message'],
            'link': event['link'],
            'notification_type': event['notification_type'],
            'unread_count': event['unread_count'],
            'timestamp': event['timestamp'],
        }))

