
# Author: Mani Amoozadeh
# Email: mani.amoozadeh2@gmail.com
# Description: Posting messages to Discord

# Discord Webhook URL looks like:
# https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN
#
# I am not sure why Discord calls this API webhook.
# A webhook, by definition, is a pre-configured HTTP endpoint that receives or handles data without authentication overhead.
# In other words, you register your URL in the server, and the server will notify you when an event occurs.
# Discord flips the traditional model. So it's kind of a "reverse webhook".

import os
import getpass
import logging

from rest_client import REST_API_Client

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


class Discord_Webhook(REST_API_Client):

    def __init__(self,
                 host=None,
                 port=None,
                 api_ver=None,
                 base=None,
                 user=getpass.getuser()):

        super().__init__(host, port, api_ver, base, user)

        self.webhook_id = os.getenv('WEBHOOK_ID', None)
        self.webhook_token = os.getenv('WEBHOOK_TOKEN', None)


    def send_discord_message(self, content, embed=None):

        url = f"{self.baseurl}/{self.webhook_id}/{self.webhook_token}"

        payload = {
            "content": content
        }

        if embed:
            payload["embeds"] = [embed]

        status, output = self.request("POST", url, json=payload)
        if not status:
            return False, output

        return True, output


if __name__ == "__main__":

    discord = Discord_Webhook(host="discord.com", base="api/webhooks")

    embed = {
        "title": "sample title",
        "description": "sample overview",
        "color": 3447003,
        "fields": [
            {
              "name": "Rating",
              "value": "⭐ sample rating",
              "inline": True
            }
        ],
        "image": {
            "url": "https://image.tmdb.org/t/p/w500/xyz.jpg"
        }
    }

    status, output = discord.send_discord_message(content="testing", embed=embed)

    bla = 0
