#!/usr/bin/env python3
"""Run once to create/update tables and seed the admin user."""
from dotenv import load_dotenv
load_dotenv()

import os
from sqlmodel import SQLModel, create_engine, Session, select
from yiwu_app.models.models import User, ProductList, Product
from yiwu_app.utils.auth import hash_password

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///yiwu_dev.db")
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)
print("✅ Tables ready:", list(SQLModel.metadata.tables.keys()))

with Session(engine) as session:
    existing = session.execute(select(User).where(User.email == "admin")).scalar_one_or_none()
    if not existing:
        admin = User(
            email="admin",
            name="Administrator",
            hashed_password=hash_password("martinez@2026"),
            is_admin=True,
        )
        session.add(admin)
        session.commit()
        print("✅ Admin user created  (login: admin / martinez@2026)")
    else:
        existing.is_admin = True
        session.commit()
        print("✅ Admin user already exists")
