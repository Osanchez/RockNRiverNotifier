import http.client, urllib
import json

class PushoverAPI():

    def __init__(self, token: str, user_key: str):
        self.http_client = http.client.HTTPSConnection("api.pushover.net:443")
        self.token = token
        self.user_key = user_key

    def send_notification(self, message: str, title: str=None) -> bool:
        """
        Send a notification to the Pushover API.

        :param message: The message to send.
        :param title: The title of the notification (optional).
        :return: True if successful, False otherwise.
        """
        payload = {
            "token": self.token,
            "user": self.user_key,
            "message": message,
        }
        if title:
            payload["title"] = title

        try:
            self.http_client.request(
                "POST",
                "/1/messages.json",
                urllib.parse.urlencode(payload),
                { "Content-type": "application/x-www-form-urlencoded" }
            )

            response = self.http_client.getresponse()
            data = response.read()

            if response.status == 200:
                result = json.loads(data.decode())
                return result.get("status") == 1
            else:
                print(f"Request failed with status {response.status}: {data.decode()}")
                return False

        except Exception as e:
            print(f"Exception during Pushover notification: {e}")
            return False