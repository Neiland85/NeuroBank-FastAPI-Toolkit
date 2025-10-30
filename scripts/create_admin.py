import asyncio
import getpass

from app.database import get_db, init_db
from app.services.role_service import initialize_default_roles
from app.services.user_service import create_user
from app.schemas import UserCreate


async def create_admin_user():
    await init_db()

    async for db in get_db():
        await initialize_default_roles(db)

        print("Create Admin User")
        username = input("Username: ")
        email = input("Email: ")
        full_name = input("Full Name: ")
        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Confirm Password: ")

        if password != password_confirm:
            print("Passwords don't match!")
            return

        user_data = UserCreate(
            username=username,
            email=email,
            full_name=full_name,
            password=password,
        )

        user = await create_user(db, user_data, roles=["admin"])
        print(f"Admin user created: {user.username}")
        break


if __name__ == "__main__":
    asyncio.run(create_admin_user())


