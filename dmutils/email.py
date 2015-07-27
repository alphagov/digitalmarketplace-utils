from flask import current_app
from mandrill import Mandrill, Error
from itsdangerous import URLSafeTimedSerializer


class MandrillException(Exception):
    pass


def send_email(
        user_id,
        email_address,
        email_body,
        api_key,
        subject,
        from_email,
        from_name,
        tags):
    try:
        mandrill_client = Mandrill(api_key)

        message = {
            'html': email_body,
            'subject': subject,
            'from_email': from_email,
            'from_name': from_name,
            'to': [{
                'email': email_address,
                'name': 'Recipient Name',
                'type': 'to'
            }],
            'important': False,
            'track_opens': None,
            'track_clicks': None,
            'auto_text': True,
            'tags': tags,
            'headers': {'Reply-To': from_email},  # noqa
            'recipient_metadata': [{
                'rcpt': email_address,
                'values': {
                    'user_id': user_id
                }
            }]
        }

        result = mandrill_client.messages.send(
            message=message,
            async=False,
            ip_pool='Main Pool'
        )
    except Error as e:
        # Mandrill errors are thrown as exceptions
        current_app.logger.error("A mandrill error occurred: %s", e)
        raise MandrillException(e.message)

    current_app.logger.info("Sent password email: %s", result)


def generate_token(data, secret_key, salt):
    ts = URLSafeTimedSerializer(secret_key)
    return ts.dumps(data, salt=salt)


def decode_token(token, secret_key, salt):
    ts = URLSafeTimedSerializer(secret_key)
    decoded, timestamp = ts.loads(
        token,
        salt=salt,
        max_age=86400,
        return_timestamp=True
    )
    return decoded, timestamp
