import logging

from collections.abc import Mapping
from os import environ
from typing import Final, Optional

from sendgrid import SendGridAPIClient  # type: ignore

from app.v3_adapter.emails import TEMPLATES_FOLDER


_logger: Final = logging.getLogger(__name__)

_EMAIL_SENDER_EMAIL: Final[str] = "hello@powerx.co"
_EMAIL_SENDER_NAME: Final[str] = "PowerX"

_EMAIL_FROM: Final[Mapping[str, str]] = {
    "email": _EMAIL_SENDER_EMAIL,
    "name": _EMAIL_SENDER_NAME,
}

_sendgrid_client: SendGridAPIClient = SendGridAPIClient(api_key=environ["SENDGRID_API_KEY"])


def _read_template(name: str) -> str:
    with open(TEMPLATES_FOLDER / name, encoding="utf-8") as f:
        return f.read()


def _verify_template_exists(template_name: str) -> None:
    if not (TEMPLATES_FOLDER / template_name).exists():
        raise ValueError(f"{template_name} template was not found in {TEMPLATES_FOLDER}")


class Templates:
    def __init__(self) -> None:
        self._one_time_password_email_template: Optional[str] = None
        self._forgot_password_email_template: Optional[str] = None

    _one_time_password_template_name: Final = "otp_email.html"
    _verify_template_exists(_one_time_password_template_name)

    def one_time_password_email_template(self) -> str:
        if self._one_time_password_email_template is not None:
            return self._one_time_password_email_template

        template = _read_template(self._one_time_password_template_name)
        self._one_time_password_email_template = template

        return template

    _forgot_password_template_name: Final = "forgot_password_email.html"
    _verify_template_exists(_forgot_password_template_name)

    def forgot_password_email_template(self) -> str:
        if self._forgot_password_email_template is not None:
            return self._forgot_password_email_template

        template = _read_template(self._forgot_password_template_name)
        self._forgot_password_email_template = template

        return template


TEMPLATES: Final[Templates] = Templates()


def send_email(to_email: str, content: str, subject: str) -> None:
    try:
        _sendgrid_client.client.mail.send.post(
            request_body={
                "from": _EMAIL_FROM,
                "content": [{"type": "text/html", "value": content}],
                "personalizations": [
                    {
                        "to": [{"email": to_email}],
                        "subject": subject,
                    },
                ],
            },
        )

    except Exception:
        _logger.exception("Failed to send an email")
