import httpx
import time
import hashlib
import hmac
import logging
from app.config import config

async def authorize_user_in_laravel(user_data: dict, contact, from_user):
    url = f"{config.backend_url}/api/account/telegram/auth"

    auth_date = int(time.time())
    tg_id = int(from_user.id)
    locale = user_data.get("user_lang", "ru")

    digits = ''.join(filter(str.isdigit, contact.phone_number))
    phone = f"+{digits}"

    fields = {
        "first_name": from_user.first_name or "",
        "last_name": from_user.last_name or "",
        "phone": phone,
        "locale": locale,
        "telegram_user_id": tg_id,
        "auth_date": auth_date
    }

    check_string = "\n".join([f"{k}={v}" for k, v in fields.items()])
    
    backend_token = config.backend_api_secret 
    secret_key = hashlib.sha256(backend_token.encode()).digest()

    generated_hash = hmac.new(
        secret_key, 
        check_string.encode(), 
        hashlib.sha256
    ).hexdigest()

    payload = {
        "first_name": from_user.first_name,
        "last_name": from_user.last_name,
        "phone": phone,
        "locale": locale,
        "telegram_user_id": tg_id,
        "auth_date": auth_date,
        "hash": generated_hash
    }

    async with httpx.AsyncClient() as client:
        try:
            logging.info(f"Check String for Laravel:\n{check_string}")
            response = await client.post(
                url, 
                json=payload, 
                headers={"Accept": "application/json"},
                timeout=10.0
            )
            logging.info(f"Backend Status: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            logging.error(f"API Error: {e}")
            return None # Вместо False возвращаем None