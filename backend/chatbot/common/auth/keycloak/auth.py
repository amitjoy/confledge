from fastapi import Security, HTTPException, status, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID
from kink import di
from pydantic import BaseModel, Field

from config.app import Settings


class User(BaseModel):
    """
    Pydantic model representing user information.
    """
    id: str = Field(description="The ID of the user")
    username: str = Field(description="The username of the user")
    email: str = Field(description="The email of the user")
    first_name: str = Field(description="The first name of the user")
    last_name: str = Field(description="The last name of the user")
    realm_roles: list = Field(description="The realm roles of the user")
    client_roles: list = Field(description="The client roles of the user")


settings = di[Settings]
token_url = f"{settings.server.auth.server_url}/realms/{settings.server.auth.realm}/protocol/openid-connect/token"

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.server.auth.server_url,
    tokenUrl=token_url
)

_idp = KeycloakOpenID(
    server_url=settings.server.auth.server_url,
    client_id=settings.server.auth.client_id,
    client_secret_key=settings.server.auth.client_secret,
    realm_name=settings.server.auth.realm,
    verify=True
)


async def get_idp_public_key() -> str:
    """
    Retrieves the public key from the identity provider.

    :return: The public key as a string.
    """
    return (
        "-----BEGIN PUBLIC KEY-----\n"
        f"{_idp.public_key()}"
        "\n-----END PUBLIC KEY-----"
    )


async def decode_token(token: str, verify_aud: bool = True) -> dict:
    """
    Decodes the provided token using the identity provider.

    :param token: The token to decode.
    :param verify_aud: Whether to verify the audience claim.
    :return: The decoded token payload as a dictionary.
    :raises HTTPException: If the token cannot be decoded.
    """
    try:
        return _idp.decode_token(
            token=token,
            key=await get_idp_public_key(),
            options={
                "verify_signature": True,
                "verify_aud": verify_aud,
                "exp": True
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_auth(token: str = Security(oauth2_scheme)) -> dict:
    """
    Retrieves and verifies the authentication token.

    :param token: The OAuth2 token.
    :return: The decoded token payload as a dictionary.
    """
    return await decode_token(token, verify_aud=True)


async def get_payload(token: str = Security(oauth2_scheme)) -> dict:
    """
    Retrieves and decodes the token payload without verifying the audience claim.

    :param token: The OAuth2 token.
    :return: The decoded token payload as a dictionary.
    """
    return await decode_token(token, verify_aud=False)


async def get_user_info(payload: dict = Depends(get_payload)) -> User:
    """
    Extracts user information from the token payload.

    :param payload: The token payload.
    :return: The User model instance.
    :raises HTTPException: If user information cannot be extracted.
    """
    try:
        return User(
            id=payload.get("sub"),
            username=payload.get("preferred_username"),
            email=payload.get("email"),
            first_name=payload.get("given_name"),
            last_name=payload.get("family_name"),
            realm_roles=payload.get("realm_access", {}).get("roles", []),
            client_roles=payload.get("resource_access", {}).get("client_id", {}).get("roles", [])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
