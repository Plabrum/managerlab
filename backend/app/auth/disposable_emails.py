"""Disposable/temporary email domain blocking."""

import logging

from litestar.exceptions import ValidationException

logger = logging.getLogger(__name__)

# Curated list of common disposable/temporary email domains
# Source: Common temporary email services that enable spam
DISPOSABLE_DOMAINS = {
    # Popular temporary email services
    "guerrillamail.com",
    "guerrillamail.net",
    "guerrillamail.org",
    "guerrillamailblock.com",
    "mailinator.com",
    "temp-mail.org",
    "temp-mail.io",
    "tempmail.com",
    "10minutemail.com",
    "10minutemail.net",
    "throwaway.email",
    "maildrop.cc",
    "mailnesia.com",
    "trashmail.com",
    "getnada.com",
    "mohmal.com",
    "yopmail.com",
    "yopmail.fr",
    "yopmail.net",
    "cool.fr.nf",
    "jetable.fr.nf",
    "nospam.ze.tc",
    "nomail.xl.cx",
    "mega.zik.dj",
    "speed.1s.fr",
    "courriel.fr.nf",
    "moncourrier.fr.nf",
    "monemail.fr.nf",
    "monmail.fr.nf",
    "fakermail.com",
    "fakeinbox.com",
    "emailondeck.com",
    "sharklasers.com",
    "grr.la",
    "spam4.me",
    "dispostable.com",
    "mintemail.com",
    "mytemp.email",
    "mytrashmail.com",
    "tmpeml.info",
    "emailfake.com",
    "getairmail.com",
    "anonbox.net",
    "anonymbox.com",
    "byom.de",
    "spamgourmet.com",
    "mailcatch.com",
    "mailmetrash.com",
    "mail-temp.com",
    "tempinbox.com",
    "tempmail.net",
    "throwam.com",
    "spambox.us",
    "incognitomail.org",
    "incognitomail.com",
    "incognitomail.net",
    "33mail.com",
    "email-fake.com",
    "filzmail.com",
    "imails.info",
    "inbox.si",
    "mailforspam.com",
    "mailmoat.com",
    "mailzi.ru",
    "pjjkp.com",
    "put2.net",
    "receiveee.com",
    "spamex.com",
    "spamfree24.com",
    "spamfree24.de",
    "spamfree24.org",
    "spamfree24.net",
    "teleworm.com",
    "teleworm.us",
    "zippymail.info",
}


def is_disposable_email(email: str) -> bool:
    """
    Check if an email address uses a disposable/temporary domain.

    Args:
        email: Email address to check

    Returns:
        True if the email domain is in the disposable list
    """
    try:
        domain = email.split("@")[-1].lower()
        return domain in DISPOSABLE_DOMAINS
    except (IndexError, AttributeError):
        return False


def validate_email_not_disposable(email: str) -> None:
    """
    Validate that an email is not from a disposable domain.

    Args:
        email: Email address to validate

    Raises:
        ValidationException: If the email is from a disposable domain
    """
    if is_disposable_email(email):
        domain = email.split("@")[-1]
        logger.warning(f"Blocked disposable email domain: {domain}")
        raise ValidationException(
            detail="Temporary or disposable email addresses are not allowed. Please use a permanent email address."
        )
