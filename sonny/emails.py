import requests
from utils import get_config_module


class EmailSender(object):
    def __init__(self):
        _, config = get_config_module()
        self.mailgun_settings = config.MAILGUN_SETTINGS
        self.sonny_config = config

    def send_emails(self, to=None, subject=None, attachments=None):
        to = to or []
        attachments = attachments or []

        # do some checks and conversions
        assert isinstance(to, list)
        assert len(to) >= 1
        assert subject is not None
        assert isinstance(attachments, list) or isinstance(attachments, tuple)
        subject = str(subject)

        # configure attachments
        attachments = [("attachment", open(a)) for a in attachments]

        # fire emails
        for recipient in to:
            return requests.post(
                "{base_url}/messages".format(base_url=self.mailgun_settings.get('base_url')),
                auth=("api", self.mailgun_settings.get('api_key')),
                data={"from": self.mailgun_settings.get('from'),
                      "to": [recipient['email']],
                      "subject": subject,
                      "text": "Dear {name},\n\nPlease find attached a Be Trade Happy report.\n\n".format(
                          name=recipient['name'])},
                files=attachments
            )
