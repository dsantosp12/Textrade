from flask.ext.bcrypt import check_password_hash, generate_password_hash

from .models import User
from app import db
from config import SECRET_KEY

# Alchemy Tools
import sqlalchemy as sql

# Help generate token
from itsdangerous import URLSafeTimedSerializer, TimedSerializer


class UserController:

    SALT = "*lo!ki>,C}s%}651{343{"
    DEFAULT_DAYS = 86400 * 3 # Day in seconds times the number of days to activate account

    def __init__(self, first_name=None, last_name=None,
                 username=None, password=None, university_email=None,
                 role="customer", user=None):
        self.user = user  # This is the user object
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = UserController.__get_hash(password)
        self.university_email = university_email
        self.role = role

    @staticmethod
    def create_user(**kwargs):
        """"Create user controls."""
        db.session.add(
            User(
                first_name=kwargs['first_name'],
                last_name=kwargs['last_name'],
                username=kwargs['username'],
                password=kwargs['password'],
                # TODO: when expansion to different schools
                university_email=kwargs['university_email'],
                role="costumer"
            )
        )
        db.session.commit()

    def create(self):
        """Create user if initialized with constructor."""
        db.session.add(
            User(self.first_name, self.last_name, self.username,
                 self.password, self.university_email, self.role)
        )
        db.session.commit()

    def change_password(self, old_password, new_password):
        """Change the user passed in constructor."""
        if UserController.check_hash(self.password, new_password):
            db.session.execute(
                sql.update(self.user).where(
                    User.username == self.username
                ).values(
                    password=UserController.__get_hash(new_password)
                )
            )
            db.session.commit()
        else:
            raise ValueError("Old password is invalid.")

    @staticmethod
    def change_user_password(pk_id, old_password, new_password):
        """Edit a user. Old password is required."""
        user = User.query.filter_by(id=pk_id).first()

        if UserController.check_hash(user.password, old_password):
            db.session.execute(
                sql.update(User).where(
                    User.id == pk_id
                ).values(
                    password=UserController.__get_hash(new_password)
                )
            )
            db.session.commit()
        else:
            raise ValueError("Old password is invalid.")

    @staticmethod
    def delete_user(username, password):
        """Delete a user. The password must be provided."""
        user = User.get(User.username == username)
        if UserController.check_hash(
            user.password,  # Hash
            password
        ):
            user.delete_instance()
        else:
            raise PermissionError("You password is wrong.")

    @staticmethod
    def get_user_by_username(username=None):
        user = User.query.filter_by(username=username).first()
        if user is None:
            raise UserController.UserNotFound("%s is not a username." % username)
        else:
            return user

    @staticmethod
    def __get_hash(password):
        return generate_password_hash(password)

    @staticmethod
    def check_hash(p_hash, password):
        return check_password_hash(p_hash, password)

    def __generate_token(self):
        return URLSafeTimedSerializer(
                secret_key=SECRET_KEY,
                salt=UserController.SALT
        ).dumps(
                self.university_email,
        )

    @staticmethod
    def generate_token(email):
        return URLSafeTimedSerializer(
                secret_key=SECRET_KEY,
                salt=UserController.SALT
        ).dumps(
            email
        )

    @staticmethod
    def confirm_token(token, expiration=None):
        serializer = URLSafeTimedSerializer(
                secret_key=SECRET_KEY,
                salt=UserController.SALT
        )
        if expiration:
            email = serializer.loads(
                token,
                max_age=expiration,
                salt=UserController.SALT
            )
        else:
            email = serializer.loads(
                token,
                max_age=UserController.DEFAULT_DAYS,  # Default 3 days to activate account
                salt=UserController.SALT
            )
        return email

    class UserNotFound(Exception):
        pass