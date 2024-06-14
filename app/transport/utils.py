from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


def send_change_signal(type, id, part_of_app):
    print("Test send message")
    channel_layer = get_channel_layer()
    print(f"Channel layer: {channel_layer}")
    async_to_sync(channel_layer.group_send)(
        "transport",
        {
            "type": "change_signal",
            "text": json.dumps({
                "type": type,
                "id": id,
                "part_of_app": part_of_app
            }),
        }
    )