#!/usr/bin/env python3
import json
import random

motd_messages = [
    "Attention! Scheduled maintenance on this device.",
    "Warning! Unscheduled maintenance may occur on this device.",
    "Notice: Routine check on this device today.",
    "Reminder: This device will be updated soon."
]

random_message = random.choice(motd_messages)
print(json.dumps({"motd_message": random_message}))
