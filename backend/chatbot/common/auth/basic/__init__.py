from common.auth.basic.auth import UserModel

UserModel._meta.database.create_tables([UserModel])
