import reflex as rx
from sqlalchemy import select
from yiwu_app.models.models import User
from yiwu_app.models.auth_state import AuthState
from yiwu_app.utils.auth import hash_password, verify_password


class AdminState(AuthState):
    # ── User list ──────────────────────────────────────────
    users: list[dict] = []

    # ── Create user form ───────────────────────────────────
    show_create_modal: bool = False
    new_name: str = ""
    new_email: str = ""
    new_password: str = ""
    create_error: str = ""
    is_saving: bool = False

    # ── Change password form ───────────────────────────────
    show_pw_modal: bool = False
    pw_current: str = ""
    pw_new: str = ""
    pw_confirm: str = ""
    pw_error: str = ""
    pw_success: str = ""

    def on_load(self):
        self._load_user_from_token()
        if not self.is_authenticated or not self.is_admin:
            return rx.redirect("/login")
        self._load_users()

    def _load_users(self):
        with rx.session() as session:
            rows = session.execute(
                select(User).where(User.is_admin == False).order_by(User.name)
            ).scalars().all()
            self.users = [
                {"id": u.id, "name": u.name, "email": u.email,
                 "created_at": u.created_at.strftime("%d/%m/%Y") if u.created_at else ""}
                for u in rows
            ]

    # ── Create user ────────────────────────────────────────
    def open_create_modal(self):
        self.new_name = ""
        self.new_email = ""
        self.new_password = ""
        self.create_error = ""
        self.show_create_modal = True

    def close_create_modal(self):
        self.show_create_modal = False

    def set_new_name(self, v): self.new_name = v; self.create_error = ""
    def set_new_email(self, v): self.new_email = v; self.create_error = ""
    def set_new_password(self, v): self.new_password = v; self.create_error = ""

    def create_user(self):
        if not self.new_name.strip() or not self.new_email.strip() or not self.new_password.strip():
            self.create_error = "All fields are required."
            return
        if len(self.new_password) < 6:
            self.create_error = "Password must be at least 6 characters."
            return
        self.is_saving = True
        yield

        with rx.session() as session:
            existing = session.execute(
                select(User).where(User.email == self.new_email.lower().strip())
            ).scalar_one_or_none()
            if existing:
                self.create_error = "That username already exists."
                self.is_saving = False
                return

            user = User(
                email=self.new_email.lower().strip(),
                name=self.new_name.strip(),
                hashed_password=hash_password(self.new_password),
                is_admin=False,
            )
            session.add(user)
            session.commit()

        self.is_saving = False
        self.show_create_modal = False
        self._load_users()

    def delete_user(self, user_id: int):
        with rx.session() as session:
            user = session.get(User, user_id)
            if user and not user.is_admin:
                session.delete(user)
                session.commit()
        self._load_users()

    # ── Change admin password ──────────────────────────────
    def open_pw_modal(self):
        self.pw_current = ""
        self.pw_new = ""
        self.pw_confirm = ""
        self.pw_error = ""
        self.pw_success = ""
        self.show_pw_modal = True

    def close_pw_modal(self):
        self.show_pw_modal = False

    def set_pw_current(self, v): self.pw_current = v; self.pw_error = ""
    def set_pw_new(self, v): self.pw_new = v; self.pw_error = ""
    def set_pw_confirm(self, v): self.pw_confirm = v; self.pw_error = ""

    def change_password(self):
        if not self.pw_current or not self.pw_new or not self.pw_confirm:
            self.pw_error = "All fields are required."
            return
        if self.pw_new != self.pw_confirm:
            self.pw_error = "New passwords do not match."
            return
        if len(self.pw_new) < 6:
            self.pw_error = "Password must be at least 6 characters."
            return

        with rx.session() as session:
            user = session.get(User, self.user_id)
            if not user or not verify_password(self.pw_current, user.hashed_password):
                self.pw_error = "Current password is incorrect."
                return
            user.hashed_password = hash_password(self.pw_new)
            session.commit()

        self.pw_success = "Password updated successfully."
        self.pw_current = ""
        self.pw_new = ""
        self.pw_confirm = ""
