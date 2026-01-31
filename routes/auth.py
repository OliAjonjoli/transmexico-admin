from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
import httpx
import os
from datetime import timedelta

from settings import settings
from auth import (
    create_access_token,
    verify_token,
    verify_staff_access,
    get_discord_user,
    TokenData,
    DiscordOAuthToken,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login")
async def login():
    """Redirect user to Discord OAuth login."""
    discord_auth_url = (
        f"{settings.DISCORD_API_URL}/oauth2/authorize?"
        f"client_id={settings.DISCORD_CLIENT_ID}&"
        f"redirect_uri={settings.DISCORD_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=identify%20guilds%20guilds.members.read"
    )
    return RedirectResponse(url=discord_auth_url)


@router.get("/discord/callback")
async def discord_callback(code: str = Query(...), state: str = Query(None)):
    """Handle Discord OAuth callback."""
    try:
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                f"{settings.DISCORD_API_URL}/oauth2/token",
                data={
                    "client_id": settings.DISCORD_CLIENT_ID,
                    "client_secret": settings.DISCORD_CLIENT_SECRET,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.DISCORD_REDIRECT_URI,
                },
            )
            token_response.raise_for_status()
            token_data = DiscordOAuthToken(**token_response.json())
        
        # Get bot token from environment for staff check
        bot_token = os.getenv("DISCORD_BOT_TOKEN")
        if not bot_token:
            raise HTTPException(status_code=500, detail="Bot token not configured")
        
        # Verify user is in server and get staff status
        user, is_staff = await verify_staff_access(token_data.access_token, bot_token)
        
        if not is_staff:
            # User doesn't have staff role - deny access
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/auth/unauthorized"
            )
        
        # Create JWT token
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data_obj = TokenData(
            discord_id=user.id,
            username=user.username,
            avatar_url=f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png" if user.avatar else None,
            is_staff=is_staff,
        )
        access_token = create_access_token(token_data_obj, expires_delta)
        
        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
        )
    
    except Exception as e:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/error?message={str(e)}"
        )


@router.get("/me")
async def get_current_user(token: str = Query(...)):
    """Get current authenticated user."""
    token_data = verify_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "discord_id": token_data.discord_id,
        "username": token_data.username,
        "avatar_url": token_data.avatar_url,
        "is_staff": token_data.is_staff,
    }


@router.post("/logout")
async def logout():
    """Logout user."""
    # Tokens are stateless, so just clear client-side
    return {"message": "Logged out successfully"}
