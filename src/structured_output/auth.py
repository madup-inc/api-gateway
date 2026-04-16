"""Cognito 인증 토큰 발급"""
import os
from functools import lru_cache

import boto3
from dotenv import load_dotenv

load_dotenv()

# pytest-xdist 워커는 컨트롤러에서 발급한 토큰을 이 환경변수로 받는다
_CACHED_TOKEN_ENV = "COGNITO_CACHED_TOKEN"


@lru_cache(maxsize=1)
def get_cognito_token() -> str:
    # 이미 발급된 토큰이 환경변수에 있으면 재사용 (워커 프로세스용)
    if cached := os.environ.get(_CACHED_TOKEN_ENV):
        return cached

    user_pool_id = os.environ["COGNITO_USER_POOL_ID"]
    client_id = os.environ["COGNITO_CLIENT_ID"]
    username = os.environ["COGNITO_ID"]
    password = os.environ["COGNITO_PW"]
    region = user_pool_id.split("_")[0]

    cognito = boto3.client("cognito-idp", region_name=region)
    resp = cognito.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
        ClientId=client_id,
    )
    return resp["AuthenticationResult"]["IdToken"]
