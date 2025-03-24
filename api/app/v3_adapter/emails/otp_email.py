from datetime import datetime
from app.v3_adapter.emails.emails import TEMPLATES, send_email


def otp_email(receiver: str, one_time_code: str) -> None:
    send_email(
        to_email=receiver,
        content=(
            TEMPLATES.one_time_password_email_template()
            .replace("{{PASSWORD}}", one_time_code)
            .replace("{{YEAR}}", str(datetime.now().year))
        ),
        subject="PowerX Verification Code",
    )
