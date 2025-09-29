import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .emails import send_account_locked_email
from .managers import UserManager


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser with additional fields and
      methods for enhanced authentication and account management.
    Fields:
        id (UUIDField): Primary key, unique identifier for the user.
        username (CharField): Unique username, max length 12.
        security_question (CharField): Security question for account recovery, choices
          defined in SecurityQuestions.
        security_answer (CharField): Answer to the security question.
        email (EmailField): Unique email address, used for login.
        first_name (CharField): User's first name.
        middle_name (CharField): User's middle name (optional).
        last_name (CharField): User's last name.
        id_no (PositiveIntegerField): Unique identification number.
        account_status (CharField): Status of the account, choices defined in AccountStatus.
        role (CharField): User role, choices defined in RoleChoices.
        failed_login_attempts (PositiveSmallIntegerField): Number of consecutive
          failed login attempts.
        last_failed_login (DateTimeField): Timestamp of the last failed login attempt.
        otp (CharField): One-time password for authentication.
        otp_expiry_time (DateTimeField): Expiry time for the OTP.
    Choices:
        SecurityQuestions: Enum for security questions.
        AccountStatus: Enum for account status (ACTIVE, LOCKED).
        RoleChoices: Enum for user roles (CUSTOMER, ACCOUNT_EXECUTIVE, TELLER, BRANCH_MANAGER).
    Methods:
        set_otp(otp: str): Sets OTP and expiry time.
        verify_otp(otp: str) -> bool: Verifies OTP and resets if valid.
        handle_failed_login_attempts(): Increments failed login attempts, locks
          account if threshold exceeded.
        reset_failed_login_attempts(): Resets failed login attempts and unlocks account.
        unlock_account(): Unlocks account if currently locked.
        has_role(role_name: str) -> bool: Checks if user has a specific role.
        __str__() -> str: Returns string representation of the user.
    Properties:
        is_locked_out (bool): Indicates if the user is currently locked out.
        full_name (str): Returns the user's full name in title case.
    Meta:
        verbose_name: "User"
        verbose_name_plural: "Users"
        ordering: By date joined (descending).
    """
    class SecurityQuestions(models.TextChoices):
        """
        An enumeration of common security questions used for user authentication.

        Choices:
            MAIDEN_NAME: "What is your mother's maiden name?"
            FAVORITE_COLOR: "What is your favorite color?"
            BIRTH_CITY: "What is the city you were born?"
            CHILDHOOD_FRIEND: "What is the name of your childhood best friend?"
        """
        MAIDEN_NAME = (
            "maiden_name",
            _("What is your mother's maiden name?")
        )
        FAVORITE_COLOR = (
            "favorite_color",
            _("What is your favorite color?")
        )
        BIRTH_CITY = (
            "birth_city",
            _("What is the city you were born?")
        )
        CHILDHOOD_FRIEND = (
            "childhood_friend",
            _("What is the name of your childhood best friend?")
        )

    class AccountStatus(models.TextChoices):
        """
        An enumeration representing the possible statuses for a user account.

        Attributes:
            ACTIVE: Indicates that the account is active and accessible.
            LOCKED: Indicates that the account is locked and access is restricted.
        """
        ACTIVE = "active", _("Active")
        LOCKED = "locked", _("Locked")

    class RoleChoices(models.TextChoices):
        """
        An enumeration of user roles within the banking system.

        Attributes:
            CUSTOMER: Represents a customer of the bank.
            ACCOUNT_EXECUTIVE: Represents an account executive responsible
              for managing client accounts.
            TELLER: Represents a bank teller who handles transactions and customer service.
            BRANCH_MANAGER: Represents the manager of a bank branch.
        """
        CUSTOMER = "customer", _("Customer")
        ACCOUNT_EXECUTIVE = "account_executive", _("Account Executive")
        TELLER = "teller", _("Teller")
        BRANCH_MANAGER = "branch_manager", _("Branch Manager")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(_("Username"), max_length=12, unique=True)
    security_question = models.CharField(
        _("Security Question"), max_length=30, choices=SecurityQuestions.choices)
    security_answer = models.CharField(_("Security Answer"), max_length=30)
    email = models.EmailField(_("Email"), unique=True, db_index=True)
    first_name = models.CharField(_("First Name"), max_length=30)
    middle_name = models.CharField(
        _("Middle Name"), max_length=30, blank=True, null=True)
    last_name = models.CharField(_("Last Name"), max_length=30)
    id_no = models.PositiveIntegerField(_("ID Number"), unique=True)
    account_status = models.CharField(
        _("Account Status"), max_length=10,
        choices=AccountStatus.choices, default=AccountStatus.ACTIVE)
    role = models.CharField(_("Role"), max_length=20,
                            choices=RoleChoices.choices, default=RoleChoices.CUSTOMER)
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    otp = models.CharField(_("OTP"), max_length=6, blank=True)
    otp_expiry_time = models.DateTimeField(
        _("OTP Expity Time"), null=True, blank=True)

    objects = UserManager()
    USERNAME_FIELD = "email"         # login with email
    REQUIRED_FIELDS = [
        "first_name", "last_name", "id_no", "security_question", "security_answer"]

    def set_otp(self, otp: str) -> None:
        """
        Sets the OTP (One-Time Password) for the user and updates its expiry time.

        Args:
            otp (str): The OTP value to be set.

        Side Effects:
            - Updates the `otp` and `otp_expiry_time` fields of the user instance.
            - Saves the changes to the database.
        """
        self.otp = otp
        self.otp_expiry_time = timezone.now() + settings.OTP_EXPIRATION
        self.save()

    def verify_otp(self, otp: str) -> bool:
        """
        Verifies the provided OTP against the stored OTP and checks if it is still valid.

        If the OTP matches and has not expired, clears the OTP and its expiry time,
          saves the changes, and returns True. Otherwise, returns False.

        Args:
            otp (str): The OTP code to verify.

        Returns:
            bool: True if the OTP is correct and valid, False otherwise.
        """
        if self.otp == otp and self.otp_expiry_time > timezone.now():
            self.otp = ""
            self.otp_expiry_time = None
            self.save()
            return True
        return False

    def handle_failed_login_attempts(self) -> None:
        """
        Handles a failed login attempt by incrementing the failed login counter
          and updating the timestamp.
        If the number of failed attempts reaches the configured threshold, locks
          the user's account and sends a notification email.

        Side Effects:
            - Updates `failed_login_attempts` and `last_failed_login` fields.
            - May update `account_status` to locked.
            - Persists changes to the database.
            - Sends an account locked email if threshold is reached.
        """
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        if self.failed_login_attempts >= settings.LOGIN_ATTEMPTS:
            self.account_status = self.AccountStatus.LOCKED
            self.save()
            send_account_locked_email(self)
        self.save()

    def reset_failed_login_attempts(self) -> None:
        """
        Resets the user's failed login attempts and related account status.

        Sets the failed_login_attempts counter to zero, clears the last_failed_login timestamp,
        and updates the account_status to ACTIVE. Saves the changes to the database.
        """
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.account_status = self.AccountStatus.ACTIVE
        self.save()

    def unlock_account(self) -> None:
        """
        Unlocks the user account if it is currently locked.

        This method sets the account status to ACTIVE, resets the failed login attempts counter,
        clears the last failed login timestamp, and saves the changes to the database.
        """
        if self.account_status == self.AccountStatus.LOCKED:
            self.account_status = self.AccountStatus.ACTIVE
            self.failed_login_attempts = 0
            self.last_failed_login = None
            self.save()

    @property
    def is_locked_out(self) -> bool:
        """
        Determines whether the user's account is currently locked out.

        Returns:
            bool: True if the account is locked, False otherwise. If the lockout duration has passed,
            the account is automatically unlocked and returns False.

        Logic:
            - Checks if the account status is LOCKED.
            - If locked, verifies if the lockout duration has expired since the last failed login.
            - Unlocks the account if the duration has passed.
            - Returns True if still locked, otherwise False.
        """
        if self.account_status == self.AccountStatus.LOCKED:
            if self.last_failed_login and (timezone.now() - self.last_failed_login) > settings.LOCKOUT_DURATION:
                self.unlock_account()
                return False
            return True
        return False

    @property
    def full_name(self):
        """
        Returns the user's full name by concatenating the first and last names,
        formatting the result in title case and removing any leading or trailing whitespace.

        Returns:
            str: The formatted full name of the user.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.title().strip()

    class Meta:
        """
        Meta options for the User model:
        - verbose_name: Human-readable singular name for the model ("User").
        - verbose_name_plural: Human-readable plural name for the model ("Users").
        - ordering: Default ordering for querysets, sorted by 'date_joined' in descending order.
        """
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]

    def has_role(self, role_name: str) -> bool:
        """
        Checks if the user has a specific role.

        Args:
            role_name (str): The name of the role to check against the user's role.

        Returns:
            bool: True if the user has the specified role, False otherwise.
        """
        return hasattr(self, "role") and self.role == role_name

    def __str__(self) -> str:
        return f"{self.full_name} - {self.get_role_display()}"
