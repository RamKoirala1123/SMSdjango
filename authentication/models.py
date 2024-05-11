from django.db import models


from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver

# Create your models here.
from authentication.storage import OverwriteStorage, ProfileImagePath
import os


class CustomUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        if not username and not email:
            raise ValueError('The given username and email must be set')
        return super(CustomUserManager, self)._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    MALE = 'ml'
    FEMALE = 'fl'
    STAFF = 'sf'
    TEACHER = 'tr'
    STUDENT = 'st'

    GENDER_CHOICES = ((MALE, 'male'), (FEMALE, 'female'))
    USERTYPE_CHOICES = ((TEACHER, 'teacher'),
                        (STUDENT, 'student'), (STAFF, 'staff'))

    username = models.CharField(
        _('username'),
        null=False,
        blank=False,
        max_length=30,
        unique=True,
        help_text=_(
            'Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[
            username_validator
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    first_name = models.CharField(
        _('first name'), max_length=30, blank=True)
    last_name = models.CharField(
        _('last name'), max_length=30, blank=True)
    email = models.EmailField(
        _('email address'), unique=True, blank=False, null=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    dob = models.DateField(_('date of birth'), blank=True)
    _gender = models.CharField(
        _('gender'), max_length=2, choices=GENDER_CHOICES, blank=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    email_from_work = models.EmailField(
        max_length=255, unique=True, null=True, blank=True)
    _usertype = models.CharField(
        _('type of user'), max_length=2, choices=USERTYPE_CHOICES, blank=True, null=False)
    image = models.ImageField(_('Profile Image'), storage=OverwriteStorage(
    ), upload_to=ProfileImagePath, blank=True, null=True)
    objects = CustomUserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'dob', '_gender']

    @property
    def gender(self):
        if self._gender:
            for i in self.GENDER_CHOICES:
                if self._gender in i:
                    return i[1]

    @property
    def usertype(self):
        if self._usertype:
            for i in self.USERTYPE_CHOICES:
                if self._usertype in i:
                    return i[1]

    @gender.setter
    def gender(self, value):
        value = str(value).lower()
        for i in self.GENDER_CHOICES:
            if value in i:
                self._gender = i[0]
                return

    @usertype.setter
    def usertype(self, value):
        value = str(value).lower()
        for i in self.USERTYPE_CHOICES:
            if value in i:
                self._usertype = i[0]
                return

    def save(self, *args, **kwargs):
        if not self.email_from_work:
            self.email_from_work = self.get_email()
        super(User, self).save(*args, **kwargs)

    def get_email(self):
        return self.email

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def __str__(self):
        return self.username

    def delete(self, *args, **kwargs):
        self.image
        super(User, self).delete(*args, **kwargs)


@receiver(models.signals.post_delete, sender=User)
def post_delete_file_path(sender, instance, **kwargs):
    if instance.image:
        dirname, filename = instance.image.path.split('/')
        if os.path.exists(dirname):
            os.remove(dirname)

class Notice(models.Model):
    date=models.DateField(auto_now=True)
    by=models.CharField(max_length=20,null=True,default='Admin')
    message=models.CharField(max_length=500)