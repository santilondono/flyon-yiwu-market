import reflex as rx
from sqlalchemy import select
from yiwu_app.models.models import User
from yiwu_app.utils.auth import hash_password, verify_password, create_token, decode_token


class AuthState(rx.State):
    token: str = rx.Cookie(name="yiwu_token", max_age=604800)

    user_id: int = 0
    user_name: str = ""
    user_email: str = ""
    is_admin: bool = False
    is_loading: bool = False
    error: str = ""

    form_email: str = ""
    form_password: str = ""
    form_name: str = ""

    @rx.var
    def is_authenticated(self) -> bool:
        return self.user_id > 0

    def _load_user_from_token(self) -> bool:
        if self.token:
            uid = decode_token(self.token)
            if uid:
                with rx.session() as session:
                    user = session.get(User, uid)
                    if user:
                        self.user_id = user.id
                        self.user_name = user.name
                        self.user_email = user.email
                        self.is_admin = user.is_admin
                        return True
        self.user_id = 0
        self.user_name = ""
        self.user_email = ""
        self.is_admin = False
        return False

    def on_load(self):
        self._load_user_from_token()

    def index_redirect(self):
        authenticated = self._load_user_from_token()
        if authenticated:
            if self.is_admin:
                return rx.redirect("/admin")
            return rx.redirect("/lists")
        return rx.redirect("/login")

    def login_guard(self):
        authenticated = self._load_user_from_token()
        if authenticated:
            if self.is_admin:
                return rx.redirect("/admin")
            return rx.redirect("/lists")

    def set_email(self, v: str):
        self.form_email = v
        self.error = ""

    def set_password(self, v: str):
        self.form_password = v
        self.error = ""

    def set_name(self, v: str):
        self.form_name = v
        self.error = ""

    def login(self):
        if not self.form_email or not self.form_password:
            self.error = "Please fill in all fields."
            return
        self.is_loading = True
        self.error = ""
        yield

        with rx.session() as session:
            user = session.execute(
                select(User).where(User.email == self.form_email.lower().strip())
            ).scalar_one_or_none()

            if not user or not verify_password(self.form_password, user.hashed_password):
                self.error = "Incorrect email or password."
                self.is_loading = False
                return

            self.token = create_token(user.id)
            self.user_id = user.id
            self.user_name = user.name
            self.user_email = user.email
            self.is_admin = user.is_admin

        self.is_loading = False
        self.form_password = ""

        if self.is_admin:
            return rx.redirect("/admin")
        return rx.redirect("/lists")

    def logout(self):
        self.token = ""
        self.user_id = 0
        self.user_name = ""
        self.user_email = ""
        self.is_admin = False
        return rx.redirect("/login")
