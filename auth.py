import httpx
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel

from settings import settings


class TokenData(BaseModel):
    discord_id: int
    username: str
    avatar_url: Optional[str] = None
    is_staff: bool = False


class DiscordUser(BaseModel):
    id: int
    username: str
    avatar: Optional[str]
    discriminator: str


class DiscordOAuthToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str


async def get_discord_user(access_token: str) -> DiscordUser:
    """Fetch user info from Discord API using access token."""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get(
            f"{settings.DISCORD_API_URL}/users/@me",
            headers=headers
        )
        response.raise_for_status()
        return DiscordUser(**response.json())


async def get_discord_user_guilds(access_token: str) -> list:
    """Fetch guilds the user is a member of."""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get(
            f"{settings.DISCORD_API_URL}/users/@me/guilds",
            headers=headers
        )
        response.raise_for_status()
        return response.json()


async def get_discord_member(guild_id: int, user_id: int, bot_token: str) -> dict:
    """Fetch member info from Discord API using bot token."""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bot {bot_token}"}
        response = await client.get(
            f"{settings.DISCORD_API_URL}/guilds/{guild_id}/members/{user_id}",
            headers=headers
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()


def check_staff_role(roles: list, staff_role_id: int) -> bool:
    """Check if user has staff role."""
    return str(staff_role_id) in roles


async def verify_staff_access(access_token: str, bot_token: str) -> tuple[DiscordUser, bool]:
    """Verify user is in server and has staff role."""
    user = await get_discord_user(access_token)
    
    # Check if user is in the server
    member = await get_discord_member(
        settings.DISCORD_SERVER_ID,
        user.id,
        bot_token
    )
    
    is_staff = False
    if member:
        is_staff = check_staff_role(member.get("roles", []), settings.DISCORD_STAFF_ROLE_ID)
    
    return user, is_staff


def create_access_token(data: TokenData, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token."""
    to_encode = data.dict()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        discord_id: int = payload.get("discord_id")
        username: str = payload.get("username")
        is_staff: bool = payload.get("is_staff", False)
        
        if discord_id is None or username is None:
            return None
        
        return TokenData(
            discord_id=discord_id,
            username=username,
            is_staff=is_staff,
            avatar_url=payload.get("avatar_url")
        )
    except JWTError:
        return None
