from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class UserCreationForm(DjangoUserCreationForm):
    """
    A custom user creation form extending Django's UserCreationForm.
    This form is used to create new User instances with additional fields and validation logic:
        - Ensures unique email and id_no for each user.
        - Requires security question and answer for regular users (non-superusers).
        - Supports saving the user instance.
    Fields:
        - email: User's email address (must be unique).
        - id_no: User's identification number (must be unique).
        - first_name: User's first name.
        - middle_name: User's middle name.
        - last_name: User's last name.
        - security_question: Security question for account recovery (required for regular users).
        - security_answer: Answer to the security question (required for regular users).
        - is_staff: Boolean indicating staff status.
        - is_superuser: Boolean indicating superuser status.
    Methods:
        - clean_email: Validates uniqueness of email.
        - clean_id_no: Validates uniqueness of id_no.
        - clean: Validates presence of security question and answer for regular users.
        - save: Saves the user instance to the database.
    """
    class Meta:
        model = User
        fields = [
            "email",
            "id_no",
            "first_name",
            "middle_name",
            "last_name",
            "security_question",
            "security_answer",
            "is_staff",
            "is_superuser"
        ]

    def clean_email(self):
        """
        Validates the email field to ensure uniqueness.

        Checks if a user with the provided email already exists in the database.
        Raises a ValidationError if the email is already taken.

        Returns:
            str: The validated email address.

        Raises:
            ValidationError: If a user with the given email already exists.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with that email already exist"))
        return email

    def clean_id_no(self):
        """
        Validates the 'id_no' field to ensure uniqueness.

        Checks if a user with the provided 'id_no' already exists in the database.
        Raises a ValidationError if a duplicate is found.
        Returns the validated 'id_no' if it is unique.
        """
        id_no = self.cleaned_data.get("id_no")
        if User.objects.filter(id_no=id_no).exists():
            raise ValidationError(_("A user with that id_no already exist"))
        return id_no

    def clean(self):
        cleaned_data = super().clean()
        is_superuser = cleaned_data.get("is_superuser")
        security_question = cleaned_data.get("security_question")
        security_answer = cleaned_data.get("security_answer")

        if not is_superuser:
            if not security_question:
                self.add_error("security_question", _(
                    "Security question is required for regular users"))
            if not security_answer:
                self.add_error("security_answer", _(
                    "Security answer is required for regular users"))
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class UserChangeForm(DjangoUserChangeForm):
    """
    A form for updating user information, extending Django's UserChangeForm.
    This form allows modification of user fields such as email, ID number, names, security question/answer, and user status flags.
    It enforces uniqueness for email and ID number, and requires security question and answer for non-superuser accounts.
    Attributes:
        Meta:
            models (User): The user model to use for the form.
            fields (list): List of fields to include in the form.
    Methods:
        clean_email():
            Validates that the email is unique among all users except the current instance.
        clean_id_no():
            Validates that the ID number is unique among all users except the current instance.
        clean():
            Ensures that security question and answer are provided for regular users (non-superusers).
    """
    class Meta:
        models = User
        fields = [
            "email",
            "id_no",
            "first_name",
            "middle_name",
            "last_name",
            "security_question",
            "security_answer",
            "is_active",
            "is_staff",
            "is_superuser"
        ]

    def clean_email(self):
        """
        Validates the email field to ensure uniqueness among users.

        Checks if any other user (excluding the current instance) already has the provided email.
        Raises a ValidationError if a duplicate email is found.

        Returns:
            str: The validated email address.

        Raises:
            ValidationError: If a user with the given email already exists.
        """
        email = self.cleaned_data.get("email")
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email

    def clean_id_no(self):
        """
        Validates the uniqueness of the 'id_no' field for the user.

        Checks if another user (excluding the current instance) already exists with the same ID number.
        Raises a ValidationError if a duplicate is found.

        Returns:
            str: The validated ID number.

        Raises:
            ValidationError: If a user with the given ID number already exists.
        """
        id_no = self.cleaned_data.get("id_no")
        if User.objects.exclude(pk=self.instance.pk).filter(id_no=id_no).exists():
            raise ValidationError(
                _("A user with that ID number already exists."))
        return id_no

    def clean(self):
        cleaned_data = super().clean()
        is_superuser = cleaned_data.get("is_superuser")
        security_question = cleaned_data.get("security_question")
        security_answer = cleaned_data.get("security_answer")

        if not is_superuser:
            if not security_question:
                self.add_error("security_question", _(
                    "Security question is required for regular users"))
            if not security_answer:
                self.add_error("security_answer", _(
                    "Security answer is required for regular users"))
        return cleaned_data
