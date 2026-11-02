from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
       Custom manager for our User model.

       Responsible for creating:
       - Regular Users
       - Super Users

       It also ensures that:
       - Emails are normalized
       - Passwords are hashed

    """

    def create_user(self, password=None, **extra_fields):
        email = extra_fields.pop('email', None)
        # email_verified = extra_fields.get('email_verified', None)

        if not email:

            raise ValueError('An email address is required.')

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)

        user.save(using=self.db)

        return user



    def create_superuser(self, password=None, **extra_fields):

        """
            Create and save a Super User with the given email and password.
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(
            password=password,
            **extra_fields
        )