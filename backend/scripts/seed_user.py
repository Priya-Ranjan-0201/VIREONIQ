import asyncio
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from db.session import async_session_maker
from db.models import User, Role
from core.security import get_password_hash

async def seed_user() -> None:
    """
    Seed the database with initial roles (User, Admin, Recruiter) and a
    test user (test@example.com / password).  Existing records are skipped
    so the function is safely idempotent.
    """
    print("Seeding roles and test user...")
    async with async_session_maker() as session:
        # 1. Create Roles
        roles_to_create = ["User", "Admin", "Recruiter"]
        role_map = {}
        for role_name in roles_to_create:
            stmt = select(Role).where(Role.name == role_name)
            role = (await session.execute(stmt)).scalar_one_or_none()
            if not role:
                new_role = Role(name=role_name, description=f"{role_name} role")
                session.add(new_role)
                await session.flush()
                role_map[role_name] = new_role.id
            else:
                role_map[role_name] = role.id

        # 2. Create Users
        users_to_seed = [
            ("test@example.com", "password", "User"),
            ("demo@vireoniq.com", "Demo@1234", "User"),
            ("admin@vireoniq.com", "Admin@9876", "Admin"),
        ]
        
        for email, password, role_name in users_to_seed:
            stmt = select(User).where(User.email == email)
            existing_user = (await session.execute(stmt)).scalar_one_or_none()
            if not existing_user:
                user = User(
                    email=email,
                    password_hash=get_password_hash(password),
                    role_id=role_map.get(role_name, role_map["User"]),
                    is_active=True,
                    is_email_verified=True
                )
                session.add(user)
                print(f"User {email} created with password: {password}")
            else:
                print(f"User {email} already exists.")
            
        await session.commit()
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_user())
