# encoding=utf-8
import requests


class MailSender(object):

    def __init__(self):
        self.url = "https://sendcloud.sohu.com/apiv2/mail/send"
        self.api_user = 'Qimiaoxue_test_A6WkKb'
        self.api_key = 'vtRVjoJ6VvwFWGhU'
        self.from_name = "job_hub_server"

    def get_post_data(self, from_addr, to_addr, subject, html):
        return {
            "apiUser": self.api_user,
            "apiKey": self.api_key,
            "from": from_addr,
            "to": to_addr,
            "subject": subject,
            "html": html,
            "fromName": self.from_name,
            "respEmailId": "true",
        }

    def send(self, from_addr, to_addr, subject, html):
        resp = requests.post(
            self.url,
            data=self.get_post_data(
                from_addr,
                to_addr,
                subject,
                html
            )
        )
        print resp.content


if __name__ == '__main__':
    mail_sender = MailSender()
    from_addr = 'test@sendcloud.org'
    to_addr = '15011272359@163.com'
    subject = "test-1"
    html = """
    <h1>hello, world</h1>
    <p>one</p>
    """
    mail_sender.send(from_addr, to_addr, subject, html)
