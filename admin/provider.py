import bcrypt
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed

from utils.env_data import Config as conf


class UsernameAndPasswordProvider(AuthProvider):

    async def login(
        self, username: str, password: str, remember_me: bool, request: Request
    ) -> Response | None:
        if len(username) < 3:
            raise FormValidationError(
                {"username": "Ensure username has at least 3 characters"}
            )

        if username == conf.web.ADMIN_USERNAME and bcrypt.checkpw(
            password.encode(), conf.web.ADMIN_PASSWORD.encode()
        ):
            request.session.update({"username": username})
            return None

        raise LoginFailed("Invalid username or password")

    async def authenticate(self, request: Request) -> AdminUser | None:
        username = request.session.get("username")
        if username == conf.web.ADMIN_USERNAME:
            return AdminUser(username=username)
        return None

    async def logout(self, request: Request) -> Response | None:
        request.session.clear()
        return None
