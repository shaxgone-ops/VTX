import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass

from app.config import get_settings

settings = get_settings()


@dataclass
class SignedRequest:
    headers: dict[str, str]
    body: str
    timestamp: str


def sign_binance(payload: dict) -> SignedRequest:
    timestamp = str(int(time.time() * 1000))
    query = "&".join([f"{k}={v}" for k, v in payload.items()]) + f"&timestamp={timestamp}"
    signature = hmac.new(settings.binance_api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest()
    headers = {"X-MBX-APIKEY": settings.binance_api_key}
    return SignedRequest(headers=headers, body=f"{query}&signature={signature}", timestamp=timestamp)


def sign_bybit(payload: dict) -> SignedRequest:
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    body = json.dumps(payload, separators=(",", ":"))
    plain = f"{timestamp}{settings.bybit_api_key}{recv_window}{body}"
    signature = hmac.new(settings.bybit_api_secret.encode("utf-8"), plain.encode("utf-8"), hashlib.sha256).hexdigest()
    headers = {
        "X-BAPI-API-KEY": settings.bybit_api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json",
    }
    return SignedRequest(headers=headers, body=body, timestamp=timestamp)


def sign_okx(method: str, path: str, body: str = "") -> SignedRequest:
    timestamp = str(time.time())
    prehash = f"{timestamp}{method.upper()}{path}{body}"
    digest = hmac.new(settings.okx_api_secret.encode("utf-8"), prehash.encode("utf-8"), hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode("utf-8")
    headers = {
        "OK-ACCESS-KEY": settings.okx_api_key,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": settings.okx_api_passphrase,
        "Content-Type": "application/json",
    }
    return SignedRequest(headers=headers, body=body, timestamp=timestamp)


def sign_kucoin(endpoint: str, body: str = "") -> SignedRequest:
    timestamp = str(int(time.time() * 1000))
    prehash = f"{timestamp}POST{endpoint}{body}"
    signature = base64.b64encode(hmac.new(settings.kucoin_api_secret.encode("utf-8"), prehash.encode("utf-8"), hashlib.sha256).digest()).decode("utf-8")
    passphrase = base64.b64encode(
        hmac.new(settings.kucoin_api_secret.encode("utf-8"), settings.kucoin_api_passphrase.encode("utf-8"), hashlib.sha256).digest()
    ).decode("utf-8")
    headers = {
        "KC-API-KEY": settings.kucoin_api_key,
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": timestamp,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json",
    }
    return SignedRequest(headers=headers, body=body, timestamp=timestamp)
