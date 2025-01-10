from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from kink import di
from peewee import Model, AutoField, CharField, DateTimeField
from peewee_extra_fields import SimplePasswordField
from playhouse.db_url import connect

from config.app import Settings

security = HTTPBasic()


class UserModel(Model):
    """
    Peewee model representing a user.
    """
    id = AutoField()
    username = CharField(null=False, unique=True)
    password = SimplePasswordField(null=False, salt=di[Settings].db.app_db.user_pass_salt)
    created_at = DateTimeField(null=False, default=datetime.now)

    class Meta:
        table_name = di[Settings].db.app_db.user_table_name
        database = connect(di[Settings].db.app_db.connection_string)


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Verifies user credentials using HTTP Basic Authentication.

    :param credentials: HTTPBasicCredentials provided by FastAPI's security dependency.
    :return: The username if authentication is successful.
    :raises HTTPException: If the username or password is incorrect.
    """
    try:
        user = UserModel.get((UserModel.username == credentials.username) &
                             (UserModel.password == credentials.password))
    except UserModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"}
        )
    return credentials.username
