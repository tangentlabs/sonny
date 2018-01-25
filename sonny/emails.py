import requests
from utils import get_config_module


class EmailSender(object):
    def __init__(self):
        _, config = get_config_module()
        self.mailgun_settings = config.MAILGUN_SETTINGS
        self.sonny_config = config

    def send_emails(self, to=None, subject=None, get_text=None, attachments=None):
        to = to or []
        attachments = attachments or []

        # do some checks and conversions
        assert isinstance(to, list)
        assert len(to) >= 1
        assert subject is not None
        assert callable(get_text)
        assert isinstance(attachments, list) or isinstance(attachments, tuple)
        subject = str(subject)

        for recipient in to:
            # configure attachments
            open_attachments = [open(a, 'rb') for a in attachments]

            # fire emails
            response = requests.post(
                "{base_url}/messages".format(base_url=self.mailgun_settings.get('base_url')),
                auth=("api", self.mailgun_settings.get('api_key')),
                data={"from": self.mailgun_settings.get('from'),
                      "to": recipient['email'],
                      "subject": subject,
                      "text": get_text(recipient=recipient)},
                files=[("attachment", a) for a in open_attachments],
                verify=False
            )

            if response.status_code >= 400:
                print 'Error with sending e-mail: [{}]'.format(response.status_code), response.text

            # close files
            for a in open_attachments:
                a.close()
