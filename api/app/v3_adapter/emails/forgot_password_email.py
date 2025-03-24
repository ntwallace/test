from datetime import datetime
from app.v3_adapter.emails.emails import TEMPLATES, send_email


def forgot_password_email(receiver: str, forgot_password_link: str) -> None:
    send_email(
        to_email=receiver,
        content=(
            TEMPLATES.forgot_password_email_template()
            .replace("{{PASSWORD_RESET_LINK}}", forgot_password_link)
            .replace("{{YEAR}}", str(datetime.now().year))
        ),
        subject="PowerX Reset Password",
    )
