from slack_sdk import WebClient


class SlackClient:
    def __init__(self, token: str):
        self.token = token
        self.client = WebClient(token=token)

    def send_file_to(self, filepath: str, user_id: str) -> None:
        response = self.client.conversations_open(users=user_id)
        channel_id = response["channel"]["id"]
        self.client.files_upload_v2(
            channel=channel_id, file=filepath, initial_comment="Hello, voici mon justificatif de transport pour le "
                                                               "mois dernier")

    def get_users(self) -> dict:
        response = self.client.users_list()
        return {m["id"]: m["profile"]["real_name"] for m in response["members"] if not m["is_bot"] and not m["deleted"]}
