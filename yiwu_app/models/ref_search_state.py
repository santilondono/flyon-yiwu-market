import dataclasses

import reflex as rx

from yiwu_app.models.auth_state import AuthState
from yiwu_app.utils import refs_db


@dataclasses.dataclass
class RefStore:
    store_number: str = ""
    contact: str = ""
    price: str = ""
    times: str = ""
    last_date: str = ""
    is_latest: bool = False
    matches: bool = False


@dataclasses.dataclass
class RefResult:
    ref: str = ""
    name: str = ""
    composition: str = ""
    image_url: str = ""
    stores: list[RefStore] = dataclasses.field(default_factory=list)


def _fmt_price(s: dict, ref_unit: str) -> str:
    price = s.get("last_price_rmb")
    if price is None or price == "":
        return ""
    try:
        text = f"{float(price):.2f}"
    except (TypeError, ValueError):
        text = str(price)
    currency = s.get("currency") or "RMB"
    unit = s.get("unit") or ref_unit or ""
    text = f"{text} {currency}"
    return f"{text} / {unit}" if unit else text


def _fmt_times(times) -> str:
    try:
        n = int(times or 0)
    except (TypeError, ValueError):
        return ""
    if n <= 0:
        return ""
    return "comprada 1 vez" if n == 1 else f"comprada {n} veces"


def _to_result(r: dict) -> RefResult:
    ref_unit = r.get("unit") or ""
    stores = [
        RefStore(
            store_number=str(s.get("store_number") or ""),
            contact=str(s.get("store_contact") or ""),
            price=_fmt_price(s, ref_unit),
            times=_fmt_times(s.get("times")),
            last_date=refs_db.format_date(s.get("last_date")),
            is_latest=(i == 0),
            matches=bool(s.get("matches")),
        )
        for i, s in enumerate(r.get("stores", []))
    ]
    return RefResult(
        ref=str(r.get("ref") or ""),
        name=str(r.get("name") or ""),
        composition=str(r.get("composition") or ""),
        image_url=r.get("image_url") or "",
        stores=stores,
    )


class RefSearchState(AuthState):
    query: str = ""
    store_filter: str = ""
    results: list[RefResult] = []
    is_loading: bool = False
    available: bool = True
    exported_at: str = ""
    lightbox_url: str = ""
    show_lightbox: bool = False

    @rx.var
    def has_search(self) -> bool:
        return len(self.query.strip()) >= 2 or len(self.store_filter.strip()) >= 1

    def on_load(self):
        self._load_user_from_token()
        if not self.is_authenticated:
            return rx.redirect("/login")
        self.available = refs_db.is_available()
        self.exported_at = refs_db.get_exported_at()
        if self.has_search:
            return RefSearchState.run_search

    def set_query(self, v: str):
        self.query = v
        return RefSearchState.run_search

    def set_store_filter(self, v: str):
        self.store_filter = v
        return RefSearchState.run_search

    def clear_query(self):
        self.query = ""
        return RefSearchState.run_search

    def clear_store_filter(self):
        self.store_filter = ""
        return RefSearchState.run_search

    def run_search(self):
        if not self.has_search:
            self.results = []
            self.is_loading = False
            return
        self.is_loading = True
        yield
        data = refs_db.search(self.query, self.store_filter)
        self.available = data["available"]
        self.results = [_to_result(r) for r in data["results"]]
        self.is_loading = False

    def open_lightbox(self, url: str):
        if url:
            self.lightbox_url = url
            self.show_lightbox = True

    def close_lightbox(self):
        self.show_lightbox = False
        self.lightbox_url = ""
