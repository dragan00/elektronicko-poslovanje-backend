import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import requests

class YourConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'transport'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the consumer from the channel group when disconnected
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        
        # Call the API when a message is received
        await self.call_api(message)

        # Optionally send a response back to the WebSocket client
        await self.send(text_data=json.dumps({
            'message': 'API called successfully'
        }))

    @sync_to_async
    def call_api(self, message):
        print("Test call api")
        
    async def change_signal(self, event):
        print("Test send message")
        message = event['text']
        await self.send(text_data=message)
