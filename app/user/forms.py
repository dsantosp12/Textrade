from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)
from app.user.models import User


def username_exits(form, field):
    if User.query.filter_by(username=field.data).first():
        raise ValidationError('User with that username already exists.')


def university_email_exits(form, field):
    if User.query.filter_by(university_email=field.data).first():
        raise ValidationError('This email is already in our system.')


def university_email_does_not_exits(form, field):
    if not User.query.filter_by(university_email=field.data).first():
        raise ValidationError("This email is not in our system.")


def is_not_user_active(form, field):
    # This try was done to prevent UserDoesn't exist
    # Could not find specific exception
    try:
        if User.query.filter_by(username=field.data).first().is_active():
            raise ValidationError("Your account is already active.")
    except not ValidationError:
        pass


# def personal_email_exits(form, field):
#     if User.select().where(User.personal_email == field.data).exists():
#         raise ValidationError('This email is already in our system.')


def is_uml_email(form, field):
    if "@student.uml.edu" not in field.data:
        raise ValidationError('This is not a valid email. You must be a UML student.')


class RegisterForm(Form):
    """Form to register an user."""
    first_name = StringField(
        'First Name',
        id="first_name-reg",
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z]+$',
                message="First name can only contain characters."
            )
        ]
    )
    last_name = StringField(
        'Last Name',
        id="last_name-reg",
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z]+$',
                message="Last name can only contain characters."
            )
        ]
    )
    university_email = StringField(
        'University Email',
        id="university_email-reg",
        validators=[
            DataRequired(),
            Email(),
            is_uml_email,
            university_email_exits
        ]
    )
    username = StringField(
        'Username',
        id="username-reg",
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_-]+$',
                message=("Username should be one word, letters, "
                         "numbers, and '_, -'.")
            ),
            username_exits
        ]
    )
    password = PasswordField(
        'Password',
        id="password-reg",
        validators=[
            DataRequired(),
            Length(min=5),
            EqualTo('password2', message='Password must match')
        ]
    )
    password2 = PasswordField(
        'Confirm Password',
        id="password2-reg",
        validators=[DataRequired()]
    )
    # TODO: when expansion to different schools
    # university_name = StringField(
    #     'University Name',
    #     validators=[
    #         DataRequired(),
    #         Regexp(
    #             r'^[a-zA-Z]+&',
    #             message="University name can only contain characters."
    #         )
    #     ]
    # )

    # personal_email = StringField(
    #     'Personal Email (Optional)',
    #     validators=[
    #         Email(),
    #         personal_email_exits
    #     ]
    # )


class LoginForm(Form):
    """Login user form."""
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class ResendActivationEmailForm(Form):
    """Resend token form when activating user."""
    university_email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            university_email_does_not_exits,
        ]
    )


class ForgotCredentialReset(Form):
    """Form to send reset email with verification."""
    university_email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            university_email_does_not_exits
        ]
    )


class ResetPassword(Form):
    """Form to reset password."""
    password = PasswordField(
        'New Password',
        validators=[
            DataRequired(),
            Length(min=5),
            EqualTo('password2', message="Password must match!")
        ]
    )
    password2 = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
        ]
    )
