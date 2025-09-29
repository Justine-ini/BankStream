from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from .forms import UserChangeForm, UserCreationForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for the User model in Django admin.
    This class customizes the display, filtering, and editing of user accounts in
      the admin interface.
    Attributes:
        form (UserChangeForm): Form used for changing existing users.
        add_form (UserCreationForm): Form used for creating new users.
        model (User): The user model managed by this admin.
        list_display (list): Fields displayed in the user list view.
        list_filter (list): Fields available for filtering the user list.
        fieldsets (tuple): Grouped fields for organizing the user edit form.
        search_fields (list): Fields searchable in the admin interface.
        ordering (list): Default ordering of users in the list view.
    """
    form = UserChangeForm
    add_form = UserCreationForm
    model = User
    list_display = [
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "role"
    ]
    list_filter = ["email", "is_staff", "is_active", "role"]
    fieldsets = (
        (
            _("Login Credentials"),
            {
                "fields": (
                    "username",
                    "email",
                    "password",
                )
            },
        ),
        (
            _("Personal Information"),
            {"fields": ("first_name", "middle_name",
                        "last_name", "id_no", "role")},
        ),
        (
            _("Account Status"),
            {
                "fields": (
                    "account_status",
                    "failed_login_attempts",
                    "last_failed_login",)
            },
        ),
        (
            _("Security"),
            {
                "fields": ("security_question", "security_answer",)
            },
        ),
        (
            _("Permissions and Groups"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",)
            },
        ),
        (
            _("Important dates"),
            {
                "fields": ("last_login", "date_joined",)
            },
        ),

    )
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["email"]
