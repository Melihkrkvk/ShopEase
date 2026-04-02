from dataclasses import dataclass


@dataclass
class User:
    """
    Domain object representing a registered user.

    Pure data container with no database or framework coupling.
    Created by UserRepository after mapping from UserDAO row dicts.

    Attributes:
        email (str): The user's unique email address.
        password (str): The bcrypt-hashed password.
        name (str): The user's display name.
        id (int | None): Assigned by the database after persistence.
        is_admin (bool): Whether the user has admin privileges.
    """

    email: str
    password: str
    name: str
    id: int | None = None
    is_admin: bool = False
