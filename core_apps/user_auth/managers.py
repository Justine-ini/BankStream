import random
import string
from os import getenv
from typing import Any, Optional

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


def generate_username() -> str:
    """
    Generates a unique username based on the bank name and random alphanumeric characters.

    The username is constructed by taking the first letter of each word in
      the bank name (converted to uppercase),
    followed by a hyphen and a random sequence of uppercase letters and
      digits to reach a total length of 12 characters.

    Returns:
        str: The generated username.
    """
    bank_name = getenv("BANK_NAME").replace(
        ".", " ").replace("-", " ").replace("_", " ").strip()
    words = bank_name.split()
    prefix = "".join(word[0].upper() for word in words if word)
    remaining_length = 12 - len(prefix) - 1
    random_chars = "".join(random.choices(
        string.ascii_uppercase + string.digits, k=remaining_length))
    username = f"{prefix}-{random_chars}"
    return username


def validate_email_address(email: str) -> None:
    """
    Validates the given email address.

    Attempts to validate the provided email address using Django's `validate_email` function.
    Raises a `ValidationError` with a user-friendly message if the email address is invalid.

    Args:
        email (str): The email address to validate.

    Raises:
        ValidationError: If the email address is not valid.
    """
    try:
        validate_email(email)
    except ValidationError as e:
        raise ValidationError(_("Enter a valid email address")) from e


class UserManager(DjangoUserManager):
    """
    Custom user manager for handling user creation and management.
    Methods
    -------
    _create_user(email: str, password: str, **extra_fields: Any)
        Internal method to create and save a user with the given email and password.
        Validates that both email and password are provided, normalizes the email,
        generates a username, and saves the user instance.
    create_user(email: str, password: Optional[str] = None, **extra_fields: Any)
        Creates and saves a regular user with the given email and password.
        Sets 'is_superuser' and 'is_staff' to False by default.
    create_superuser(email: str, password: Optional[str] = None, **extra_fields)
        Creates and saves a superuser with the given email and password.
        Ensures 'is_superuser' and 'is_staff' are set to True, raising a ValueError if not.
    """

    def _create_user(self, email: str, password: str, **extra_fields: Any):
        """
        Creates and saves a new user with the given email and password.
        Args:
            email (str): The user's email address.
            password (str): The user's password.
            **extra_fields (Any): Additional fields to set on the user model.
        Raises:
            ValueError: If the email or password is not provided.
        Returns:
            User: The newly created user instance.
        """
        if not email:
            raise ValueError(_("An email address must be provided."))

        if not password:
            raise ValueError(_("Password must be provided."))

        username = generate_username()
        email = self.normalize_email(email)
        validate_email_address(email)

        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: Optional[str] = None, **extra_fields: Any):
        """
        Creates and returns a new user with the given email and password.

        Args:
            email (str): The user's email address.
            password (Optional[str], optional): The user's password. Defaults to None.
            **extra_fields (Any): Additional fields to set on the user object.

        Returns:
            User: The newly created user instance.

        Notes:
            - Sets 'is_superuser' and 'is_staff' to False by default unless specified in extra_fields.
        """
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: Optional[str] = None, **extra_fields):
        """
        Creates and returns a superuser with the given email and password.
        Ensures that the created user has both 'is_superuser' and 'is_staff' set to True.
        Raises a ValueError if these fields are not set correctly.
        Args:
            email (str): The email address for the superuser.
            password (Optional[str]): The password for the superuser.
            **extra_fields: Additional fields to set on the superuser.
        Returns:
            User: The created superuser instance.
        Raises:
            ValueError: If 'is_staff' or 'is_superuser' are not set to True.
        """
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Superuser must have is_staff=True."))

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self._create_user(email, password, **extra_fields)
