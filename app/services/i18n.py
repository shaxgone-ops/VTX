"""
VTX Earn Arena — Internationalization (i18n)
=============================================
Supports 15+ languages with auto-detection from
Telegram's language_code field.

Fallback chain: user_locale → en
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Full translation tables — 15 languages
# ---------------------------------------------------------------------------

MESSAGES: dict[str, dict[str, str]] = {
    # ── English (default) ─────────────────────────────────────────────────
    "en": {
        "welcome": "Welcome to <b>VTX Earn Arena</b>!\nTap, upgrade cards and earn tokens!",
        "welcome_balance": "Balance: <b>{balance}</b> {symbol}\nProfit/h: <b>{pph}</b>\nStamina: <b>{stamina}</b>",
        "welcome_invite": "Invite friends: {link}",
        "daily_ping": "Your daily update is ready! Open the app and boost your profit.",
        "open_app": "Open App",
        "profile": "Profile",
        "play": "Play",
        "cards": "Cards",
        "friends": "Friends",
        "earn": "Earn",
        "airdrop": "Airdrop",
        "upgrade": "Upgrade",
        "max_stage": "Max Stage",
        "insufficient_balance": "Insufficient balance",
        "upgrade_success": "Upgrade successful! +{delta} PPH",
        "tap_accepted": "Tap accepted! +{tokens} {symbol}",
        "stamina_empty": "Stamina is empty! Wait for regen.",
        "banned": "Your account has been suspended.",
        "suspicious": "Suspicious activity detected.",
        "daily_reward_claimed": "Daily reward claimed: +{amount} {symbol}",
        "daily_reward_wait": "Play first, then claim your reward.",
        "quest_completed": "Quest completed! +{tokens} tokens, +{pph} PPH",
        "quest_not_done": "Quest not completed yet.",
        "quest_already_claimed": "Already claimed.",
        "referral_reward": "Referral bonus: +{amount} {symbol}",
        "leaderboard_title": "Top Players",
        "vip_activated": "VIP activated for {days} days!",
        "wallet_saved": "Wallet saved for {network}",
        "withdrawal_created": "Withdrawal request created: {amount} {symbol}",
        "withdrawal_locked": "Withdrawals temporarily locked.",
        "help_text": "Use /start to begin.\nTap to earn tokens.\nUpgrade cards to boost profit/hour.\nInvite friends for bonuses!",
        "language_changed": "Language set to English.",
        "combo_claimed": "Daily Combo claimed! +{amount} tokens!",
        "cipher_solved": "Daily Cipher solved! +{amount} tokens!",
        "access_blocked": "Access blocked. Bot is in private mode.",
        "bot_started": "Bot started! Tap the button below to play.",
    },

    # ── Russian ───────────────────────────────────────────────────────────
    "ru": {
        "welcome": "Добро пожаловать в <b>VTX Earn Arena</b>!\nТапай, улучшай карточки и зарабатывай токены!",
        "welcome_balance": "Баланс: <b>{balance}</b> {symbol}\nДоход/ч: <b>{pph}</b>\nСтамина: <b>{stamina}</b>",
        "welcome_invite": "Пригласи друзей: {link}",
        "daily_ping": "Ежедневное обновление готово! Открой приложение и увеличь доход.",
        "open_app": "Открыть",
        "profile": "Профиль",
        "play": "Играть",
        "cards": "Карточки",
        "friends": "Друзья",
        "earn": "Заработок",
        "airdrop": "Аирдроп",
        "upgrade": "Улучшить",
        "max_stage": "Макс. уровень",
        "insufficient_balance": "Недостаточно средств",
        "upgrade_success": "Улучшение успешно! +{delta} PPH",
        "tap_accepted": "Тап принят! +{tokens} {symbol}",
        "stamina_empty": "Стамина закончилась! Подожди восстановления.",
        "banned": "Ваш аккаунт заблокирован.",
        "suspicious": "Обнаружена подозрительная активность.",
        "daily_reward_claimed": "Награда получена: +{amount} {symbol}",
        "daily_reward_wait": "Сначала поиграй, потом забери награду.",
        "quest_completed": "Квест выполнен! +{tokens} токенов, +{pph} PPH",
        "quest_not_done": "Квест ещё не выполнен.",
        "quest_already_claimed": "Уже получено.",
        "referral_reward": "Бонус за реферала: +{amount} {symbol}",
        "leaderboard_title": "Топ игроков",
        "vip_activated": "VIP активирован на {days} дней!",
        "wallet_saved": "Кошелёк сохранён для {network}",
        "withdrawal_created": "Запрос на вывод создан: {amount} {symbol}",
        "withdrawal_locked": "Вывод временно заблокирован.",
        "help_text": "Напиши /start для начала.\nТапай для заработка.\nУлучшай карточки для дохода/час.\nПриглашай друзей за бонусы!",
        "language_changed": "Язык установлен: Русский.",
        "combo_claimed": "Дейли комбо получен! +{amount} токенов!",
        "cipher_solved": "Дейли шифр решён! +{amount} токенов!",
        "access_blocked": "Доступ закрыт. Бот в приватном режиме.",
        "bot_started": "Бот запущен! Нажми кнопку ниже для игры.",
    },

    # ── Uzbek ─────────────────────────────────────────────────────────────
    "uz": {
        "welcome": "<b>VTX Earn Arena</b> ga xush kelibsiz!\nBosing, kartalarni kuchaytiring va token ishlang!",
        "welcome_balance": "Balans: <b>{balance}</b> {symbol}\nDaromad/s: <b>{pph}</b>\nStamina: <b>{stamina}</b>",
        "welcome_invite": "Do'stlarni taklif qiling: {link}",
        "daily_ping": "Kunlik yangilanish tayyor! Ilovani ochib daromadni oshiring.",
        "open_app": "Ochish",
        "profile": "Profil",
        "play": "O'ynash",
        "cards": "Kartalar",
        "friends": "Do'stlar",
        "earn": "Ishlash",
        "airdrop": "Airdrop",
        "upgrade": "Kuchaytirish",
        "max_stage": "Max daraja",
        "insufficient_balance": "Balans yetarli emas",
        "upgrade_success": "Kuchaytirildi! +{delta} PPH",
        "tap_accepted": "Tap qabul qilindi! +{tokens} {symbol}",
        "stamina_empty": "Stamina tugadi! Tiklanishini kuting.",
        "banned": "Hisobingiz bloklangan.",
        "suspicious": "Shubhali harakat aniqlandi.",
        "daily_reward_claimed": "Kunlik mukofot olindi: +{amount} {symbol}",
        "daily_reward_wait": "Avval o'ynang, keyin mukofot oling.",
        "quest_completed": "Quest bajarildi! +{tokens} token, +{pph} PPH",
        "quest_not_done": "Quest hali bajarilmagan.",
        "quest_already_claimed": "Allaqachon olingan.",
        "referral_reward": "Referal bonus: +{amount} {symbol}",
        "leaderboard_title": "Top o'yinchilar",
        "vip_activated": "VIP {days} kunga aktivlashtirildi!",
        "wallet_saved": "Hamyon saqlandi: {network}",
        "withdrawal_created": "Yechib olish so'rovi yaratildi: {amount} {symbol}",
        "withdrawal_locked": "Yechib olish vaqtincha bloklangan.",
        "help_text": "/start boshlash uchun.\nBosib token ishlang.\nKartalarni kuchaytiring.\nDo'stlarni taklif qiling!",
        "language_changed": "Til o'rnatildi: O'zbekcha.",
        "combo_claimed": "Kunlik Combo olindi! +{amount} token!",
        "cipher_solved": "Kunlik Shifr yechildi! +{amount} token!",
        "access_blocked": "Kirish yopiq. Bot maxfiy rejimda.",
        "bot_started": "Bot ishga tushdi! O'ynash uchun pastdagi tugmani bosing.",
    },

    # ── Turkish ───────────────────────────────────────────────────────────
    "tr": {
        "welcome": "<b>VTX Earn Arena</b>'a hoş geldiniz!\nDokunun, kartları geliştirin ve jeton kazanın!",
        "welcome_balance": "Bakiye: <b>{balance}</b> {symbol}\nKâr/s: <b>{pph}</b>\nStamina: <b>{stamina}</b>",
        "welcome_invite": "Arkadaşları davet et: {link}",
        "daily_ping": "Günlük güncelleme hazır! Uygulamayı aç ve kârını artır.",
        "open_app": "Aç",
        "profile": "Profil",
        "play": "Oyna",
        "cards": "Kartlar",
        "friends": "Arkadaşlar",
        "earn": "Kazan",
        "airdrop": "Airdrop",
        "upgrade": "Yükselt",
        "max_stage": "Max Seviye",
        "insufficient_balance": "Yetersiz bakiye",
        "upgrade_success": "Yükseltme başarılı! +{delta} PPH",
        "tap_accepted": "Dokunma kabul edildi! +{tokens} {symbol}",
        "stamina_empty": "Stamina bitti! Yenilenmesini bekle.",
        "banned": "Hesabınız askıya alındı.",
        "suspicious": "Şüpheli aktivite tespit edildi.",
        "daily_reward_claimed": "Günlük ödül alındı: +{amount} {symbol}",
        "daily_reward_wait": "Önce oyna, sonra ödülünü al.",
        "language_changed": "Dil ayarlandı: Türkçe.",
        "access_blocked": "Erişim engellendi. Bot özel modda.",
        "bot_started": "Bot başladı! Oynamak için aşağıdaki düğmeye bas.",
    },

    # ── German ────────────────────────────────────────────────────────────
    "de": {
        "welcome": "Willkommen bei <b>VTX Earn Arena</b>!\nTippe, verbessere Karten und verdiene Token!",
        "welcome_balance": "Guthaben: <b>{balance}</b> {symbol}\nProfit/h: <b>{pph}</b>\nStamina: <b>{stamina}</b>",
        "welcome_invite": "Freunde einladen: {link}",
        "daily_ping": "Dein tägliches Update ist bereit! Öffne die App.",
        "open_app": "Öffnen",
        "profile": "Profil",
        "play": "Spielen",
        "cards": "Karten",
        "friends": "Freunde",
        "earn": "Verdienen",
        "airdrop": "Airdrop",
        "upgrade": "Verbessern",
        "language_changed": "Sprache: Deutsch.",
        "access_blocked": "Zugang gesperrt. Bot im privaten Modus.",
        "bot_started": "Bot gestartet! Tippe den Button zum Spielen.",
    },

    # ── French ────────────────────────────────────────────────────────────
    "fr": {
        "welcome": "Bienvenue sur <b>VTX Earn Arena</b>!\nTouchez, améliorez les cartes et gagnez des jetons!",
        "welcome_balance": "Solde: <b>{balance}</b> {symbol}\nProfit/h: <b>{pph}</b>\nStamina: <b>{stamina}</b>",
        "welcome_invite": "Inviter des amis: {link}",
        "daily_ping": "Votre mise à jour quotidienne est prête! Ouvrez l'app.",
        "open_app": "Ouvrir",
        "profile": "Profil",
        "play": "Jouer",
        "cards": "Cartes",
        "friends": "Amis",
        "earn": "Gagner",
        "airdrop": "Airdrop",
        "upgrade": "Améliorer",
        "language_changed": "Langue: Français.",
        "access_blocked": "Accès bloqué. Bot en mode privé.",
        "bot_started": "Bot lancé! Appuyez sur le bouton ci-dessous.",
    },

    # ── Spanish ───────────────────────────────────────────────────────────
    "es": {
        "welcome": "¡Bienvenido a <b>VTX Earn Arena</b>!\nToca, mejora cartas y gana tokens!",
        "welcome_balance": "Saldo: <b>{balance}</b> {symbol}\nBeneficio/h: <b>{pph}</b>\nStamina: <b>{stamina}</b>",
        "welcome_invite": "Invitar amigos: {link}",
        "daily_ping": "¡Tu actualización diaria está lista! Abre la app.",
        "open_app": "Abrir",
        "profile": "Perfil",
        "play": "Jugar",
        "cards": "Cartas",
        "friends": "Amigos",
        "earn": "Ganar",
        "airdrop": "Airdrop",
        "upgrade": "Mejorar",
        "language_changed": "Idioma: Español.",
        "access_blocked": "Acceso bloqueado. Bot en modo privado.",
        "bot_started": "¡Bot iniciado! Pulsa el botón de abajo.",
    },

    # ── Portuguese ────────────────────────────────────────────────────────
    "pt": {
        "welcome": "Bem-vindo ao <b>VTX Earn Arena</b>!\nToque, melhore cartas e ganhe tokens!",
        "daily_ping": "Sua atualização diária está pronta! Abra o app.",
        "open_app": "Abrir",
        "profile": "Perfil",
        "play": "Jogar",
        "language_changed": "Idioma: Português.",
        "access_blocked": "Acesso bloqueado. Bot em modo privado.",
        "bot_started": "Bot iniciado! Pressione o botão abaixo.",
    },

    # ── Arabic ────────────────────────────────────────────────────────────
    "ar": {
        "welcome": "مرحبًا بك في <b>VTX Earn Arena</b>!\nانقر، طوّر البطاقات واربح الرموز!",
        "daily_ping": "تحديثك اليومي جاهز! افتح التطبيق.",
        "open_app": "افتح",
        "profile": "الملف الشخصي",
        "play": "العب",
        "language_changed": "اللغة: العربية.",
        "access_blocked": "الوصول محظور. البوت في الوضع الخاص.",
        "bot_started": "البوت يعمل! اضغط الزر أدناه للعب.",
    },

    # ── Hindi ─────────────────────────────────────────────────────────────
    "hi": {
        "welcome": "<b>VTX Earn Arena</b> में स्वागत है!\nटैप करें, कार्ड अपग्रेड करें और टोकन कमाएं!",
        "daily_ping": "आपका दैनिक अपडेट तैयार है! ऐप खोलें।",
        "open_app": "खोलें",
        "profile": "प्रोफ़ाइल",
        "play": "खेलें",
        "language_changed": "भाषा: हिंदी।",
        "access_blocked": "पहुँच अवरुद्ध। बोट प्राइवेट मोड में है।",
        "bot_started": "बोट शुरू हो गया! खेलने के लिए नीचे बटन दबाएं।",
    },

    # ── Chinese (Simplified) ──────────────────────────────────────────────
    "zh": {
        "welcome": "欢迎来到 <b>VTX Earn Arena</b>！\n点击、升级卡牌、赚取代币！",
        "daily_ping": "您的每日更新已就绪！打开应用程序。",
        "open_app": "打开",
        "profile": "个人资料",
        "play": "游戏",
        "language_changed": "语言：中文。",
        "access_blocked": "访问被阻止。机器人处于私密模式。",
        "bot_started": "机器人已启动！点击下方按钮开始游戏。",
    },

    # ── Japanese ──────────────────────────────────────────────────────────
    "ja": {
        "welcome": "<b>VTX Earn Arena</b>へようこそ！\nタップしてカードをアップグレードしてトークンを稼ごう！",
        "daily_ping": "デイリーアップデート準備完了！アプリを開こう。",
        "open_app": "開く",
        "profile": "プロフィール",
        "play": "プレイ",
        "language_changed": "言語：日本語。",
        "access_blocked": "アクセスがブロックされました。",
        "bot_started": "ボット起動！下のボタンをタップ。",
    },

    # ── Korean ────────────────────────────────────────────────────────────
    "ko": {
        "welcome": "<b>VTX Earn Arena</b>에 오신 것을 환영합니다!\n탭하고, 카드를 업그레이드하고, 토큰을 벌어보세요!",
        "daily_ping": "일일 업데이트 준비 완료! 앱을 열어보세요.",
        "open_app": "열기",
        "profile": "프로필",
        "play": "플레이",
        "language_changed": "언어: 한국어.",
        "access_blocked": "접근이 차단되었습니다.",
        "bot_started": "봇이 시작되었습니다! 아래 버튼을 누르세요.",
    },

    # ── Indonesian ────────────────────────────────────────────────────────
    "id": {
        "welcome": "Selamat datang di <b>VTX Earn Arena</b>!\nKetuk, tingkatkan kartu dan dapatkan token!",
        "daily_ping": "Pembaruan harian Anda siap! Buka aplikasi.",
        "open_app": "Buka",
        "profile": "Profil",
        "play": "Main",
        "language_changed": "Bahasa: Indonesia.",
        "access_blocked": "Akses diblokir. Bot dalam mode pribadi.",
        "bot_started": "Bot dimulai! Tekan tombol di bawah.",
    },

    # ── Vietnamese ────────────────────────────────────────────────────────
    "vi": {
        "welcome": "Chào mừng đến <b>VTX Earn Arena</b>!\nNhấn, nâng cấp thẻ và kiếm token!",
        "daily_ping": "Cập nhật hàng ngày đã sẵn sàng! Mở ứng dụng.",
        "open_app": "Mở",
        "profile": "Hồ sơ",
        "play": "Chơi",
        "language_changed": "Ngôn ngữ: Tiếng Việt.",
        "access_blocked": "Truy cập bị chặn. Bot ở chế độ riêng tư.",
        "bot_started": "Bot đã khởi động! Nhấn nút bên dưới.",
    },

    # ── Kazakh ────────────────────────────────────────────────────────────
    "kk": {
        "welcome": "<b>VTX Earn Arena</b> қош келдіңіз!\nБасыңыз, карталарды жақсартыңыз және токен табыңыз!",
        "daily_ping": "Күнделікті жаңарту дайын! Қосымшаны ашыңыз.",
        "open_app": "Ашу",
        "profile": "Профиль",
        "play": "Ойнау",
        "language_changed": "Тіл: Қазақ тілі.",
        "access_blocked": "Кіру бұғатталған.",
        "bot_started": "Бот іске қосылды! Төмендегі батырманы басыңыз.",
    },
}


# ---------------------------------------------------------------------------
# Locale normalization & translation helpers
# ---------------------------------------------------------------------------

SUPPORTED_LOCALES = set(MESSAGES.keys())


def normalize_locale(code: str | None) -> str:
    """
    Convert a Telegram language_code (e.g. 'en-US', 'ru', 'uz-Cyrl')
    into one of our supported locale keys.
    Falls back to 'en' if unsupported.
    """
    if not code:
        return "en"

    # Take the base language code (before hyphen or underscore)
    base = code.lower().split("-")[0].split("_")[0].strip()

    if base in SUPPORTED_LOCALES:
        return base

    # Common aliases
    aliases: dict[str, str] = {
        "uk": "ru",     # Ukrainian → Russian fallback
        "be": "ru",     # Belarusian → Russian
        "tg": "ru",     # Tajik → Russian
        "az": "tr",     # Azerbaijani → Turkish
        "ms": "id",     # Malay → Indonesian
        "fil": "id",    # Filipino → Indonesian
        "th": "vi",     # Thai → Vietnamese (approximate)
    }

    if base in aliases:
        return aliases[base]

    return "en"


def tr(locale: str | None, key: str, fallback: str = "", **kwargs) -> str:
    """
    Translate a message key for the given locale.
    Supports {variable} substitution via kwargs.

    Usage:
        tr("ru", "welcome_balance", balance=1000, symbol="VTX", pph=150, stamina=200)
    """
    normalized = normalize_locale(locale)
    messages = MESSAGES.get(normalized, MESSAGES["en"])

    # Try the specific locale first, then fall back to English
    text = messages.get(key)
    if text is None:
        text = MESSAGES["en"].get(key, fallback or key)

    # Apply variable substitution
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass  # Return unformatted text if substitution fails

    return text
