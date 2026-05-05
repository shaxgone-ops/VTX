MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        "daily_ping": "Daily update is live. Open the app and boost your profit.",
        "open_app": "Open App",
        "profile": "Profile",
    },
    "ru": {
        "daily_ping": "Ежедневное обновление готово. Откройте приложение и усилите доход.",
        "open_app": "Открыть приложение",
        "profile": "Профиль",
    },
    "uz": {
        "daily_ping": "Kunlik yangilanish tayyor. Ilovani ochib daromadni oshiring.",
        "open_app": "Ilovani ochish",
        "profile": "Profil",
    },
}


def normalize_locale(code: str | None) -> str:
    if not code:
        return "en"
    base = code.lower().split("-")[0].split("_")[0]
    if base in MESSAGES:
        return base
    return "en"


def tr(locale: str | None, key: str, fallback: str = "") -> str:
    normalized = normalize_locale(locale)
    return MESSAGES.get(normalized, {}).get(key, fallback or key)
