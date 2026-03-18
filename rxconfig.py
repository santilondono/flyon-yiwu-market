import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

config = rx.Config(
    app_name="yiwu_app",
    db_url=os.getenv("DATABASE_URL", "sqlite:///yiwu_dev.db"),
    tailwind=None,
    plugins=[rx.plugins.SitemapPlugin()],
)
