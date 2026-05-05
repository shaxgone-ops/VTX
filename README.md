VTX Earn Arena

Bu loyiha Telegram tap earn platformasi uchun kengaytirilgan backend bo'lib, anti bot himoya, VIP access, referral economy, quest progression, oylik airdrop snapshot va admin moderation funksiyalarini bitta tizimga birlashtiradi.

Arxitektura

- `FastAPI` webhook endpoint
- `aiogram` update processing
- `PostgreSQL` persistent data
- `SQLAlchemy async` ORM
- env based secrets management
- Dockerized deployment with Render

Asosiy imkoniyatlar

- whitelist only access va VIP account control
- invite deep link, referral reward, audit yozuv
- high frequency anti tap validation va suspicious scoring
- stamina economy, combo, level progression, PPH scaling
- quest board, quest claim, token + PPH rewards
- leaderboard, daily active reward, boost flow
- simulated market sell va fee engine
- withdrawal request queue va admin review
- monthly airdrop epoch, score snapshot, distribution
- admin commandlar orqali ops boshqaruvi

Admin commandlar

- `/admin_vip <telegram_id> <days>`
- `/admin_withdrawals`
- `/admin_review <request_id> approve|reject <note>`
- `/admin_airdrop <month_key> <pool_tokens>`

User commandlar

- `/start`
- `/setwallet <wallet>`
- `/fingerprint <device_fingerprint>`

UI callbacklar

- tap x1 x5 x10 x25 x50
- profile
- daily reward
- quest board
- quest claim
- boost pph
- market sell
- withdraw
- leaderboard

Ishga tushirish

1. `.env.example` ni `.env` ga nusxalang
2. Quyidagilarni to'ldiring:
   - `BOT_TOKEN`
   - `POSTGRES_DSN`
   - `WEBHOOK_BASE_URL`
   - `WEBHOOK_SECRET`
   - `TOKEN_LOGO_URL`
   - `COVER_IMAGE_URL`
   - `VIP_IMAGE_URL`
   - `MARKET_IMAGE_URL`
   - `QUEST_IMAGE_URL`
3. `pip install -r requirements.txt`
4. `uvicorn app.main:app --host 0.0.0.0 --port 10000`

Render deploy ikki bo'lim

1. Backend Web Service

- Type: Web Service
- Runtime: Docker
- Root: loyiha ildizi
- Start: Dockerfile dagi uvicorn
- URL misol: `https://vtx-backend.onrender.com`

2. Frontend Static Site

- Type: Static Site
- Root: `frontend`
- Build command: `npm install && npm run build`
- Publish directory: `dist`
- URL misol: `https://vtx-frontend.onrender.com`

Render ENV qayerga yoziladi

Backend Web Service ENV:

- `APP_NAME`
- `ENVIRONMENT`
- `BOT_TOKEN` Telegram BotFather dan olinadi
- `WEBHOOK_BASE_URL` backend URL
- `WEBHOOK_PATH` `/telegram/webhook`
- `WEBHOOK_SECRET` o'zingiz generatsiya qilasiz
- `POSTGRES_DSN` Render PostgreSQL internal URL
- `ADMIN_IDS` Telegram user id lar
- `VIP_IDS` Telegram user id lar
- `WHITELIST_ONLY`
- `TOKEN_SYMBOL`
- `TOKEN_NAME`
- `TOKEN_LOGO_URL`
- `COVER_IMAGE_URL`
- `VIP_IMAGE_URL`
- `MARKET_IMAGE_URL`
- `QUEST_IMAGE_URL`
- `FRONTEND_PUBLIC_URL` static site URL
- `BACKEND_PUBLIC_URL` web service URL
- `BROADCAST_INTERVAL_HOURS` odatda `24`
- `INITIAL_STAMINA`
- `STAMINA_REGEN_PER_MIN`
- `MAX_TAP_PER_SECOND`
- `BASE_PROFIT_PER_HOUR`
- `VIP_PROFIT_MULTIPLIER`
- `REFERRAL_REWARD`
- `DAILY_ACTIVE_REWARD`
- `MARKET_BUY_FEE_BPS`
- `MARKET_SELL_FEE_BPS`
- `EXCHANGE_API_BASE`
- `EXCHANGE_API_KEY`
- `EXCHANGE_API_SECRET`
- `ENABLED_EXCHANGES`

Frontend Static Site ENV:

- `VITE_API_BASE_URL` backend URL

Telegram bot bilan static webapp ulash

- Bot ichidagi `Open Web App` tugmasi `FRONTEND_PUBLIC_URL` ni ochadi
- Static webapp backend API ga `VITE_API_BASE_URL` orqali ulanadi
- `/api/cards/{telegram_id}` va `/api/cards/upgrade` card economy endpointlari ishlaydi

Card economy qoidalari

- Har card `15` stage
- Upgrade narxi har stage `300%` oshadi
- Rarity bo'yicha yakuniy profit intervali `40k` dan `100k` gacha
- Har upgrade balansdan yechiladi va `profit_per_hour` oshiriladi

Wallet va withdraw

- user bir nechta network wallet saqlay oladi
- command: `/wallet NETWORK ADDRESS`
- network misollar: `TON`, `TRON`, `BSC`, `ETH`, `SOL`, `POLYGON`
- withdraw request network va asset bilan saqlanadi

Airdrop nazorati

- instant auto airdrop yo'q
- faqat admin command orqali run bo'ladi:
- `/admin_airdrop <month_key> <pool_tokens>`
- airdrop token gameplay tokendan alohida bo'lishi mumkin: `AIRDROP_TOKEN_SYMBOL`
- reward diapazoni env orqali boshqariladi: `AIRDROP_REWARD_MIN`, `AIRDROP_REWARD_MAX`
- default diapazon: `100000` dan `300000` gacha

24 soatlik xabar

- bot barcha ro'yxatdan o'tgan userlarga har `BROADCAST_INTERVAL_HOURS` da xabar yuboradi
- xabar ichida webapp ochish tugmasi bor

Avtomatik til

- user `Telegram language_code` dan til aniqlanadi
- hozir `en`, `ru`, `uz` qo'llab-quvvatlanadi

Exchange API olish va vaqt

1. Binance
- Account ochish
- API Management dan key yaratish
- IP whitelist va trading permission yoqish
- taxminiy vaqt: 30 daqiqa dan 1 kun

2. Bybit
- API Keys sahifasi orqali key secret olish
- Spot trading permission yoqish
- taxminiy vaqt: 30 daqiqa dan 1 kun

3. OKX
- API create
- Trade permission va passphrase
- taxminiy vaqt: 1 kun atrofida

4. KuCoin
- API create
- Trade permission va passphrase
- taxminiy vaqt: 1 kun atrofida

To'liq production daraja uchun qo'shimcha

- har bir birja private signed endpointlari
- retry queue
- idempotency key
- withdrawal hot wallet monitoring
- chain transaction confirmation worker
- security audit va rate limiting

Umumiy muddat

- MVP multi exchange + wallet withdraw: 7-14 kun
- production daraja to'liq monitoring bilan: 3-6 hafta

Admin API va Worker

- admin endpointlar:
  - `GET /admin/health`
  - `GET /admin/withdrawals/pending`
  - `POST /admin/withdrawals/queue`
  - `GET /admin/jobs`
- header: `x-admin-token: <ADMIN_API_TOKEN>`
- worker loop approved withdrawal larni queue orqali broadcast qiladi va confirmation status ga o'tkazadi

Private signing

- exchange signing util fayli: `app/services/exchange_private.py`
- qo'llab-quvvatlanadi:
  - Binance
  - Bybit
  - OKX
  - KuCoin
- har biriga alohida key secret passphrase env lar qo'shilgan

Rasm assetlar

Loyihada emoji ishlatilmaydi, interfeys photo va caption asosida yuradi. Quyidagi rasm fayllarini static host yoki CDN ga yuklab, URL larini env ga qo'ying:

- `vtx_token_logo_main.png`
- `vtx_arena_cover.png`
- `vtx_vip_badge.png`
- `vtx_market_banner.png`
- `vtx_quest_board.png`

Security

- barcha API key va tokenlar env orqali olinadi
- `.env` git ignore qilingan
- audit log orqali kritik actionlar loglanadi
- suspicious scoring orqali auto block mexanizmi mavjud
- fingerprint tracking orqali multi device abuse kamaytiriladi

Exchange va real token

Haqiqiy exchange order yuborish, smart contract mint, listing va legal compliance alohida bosqichlar bilan amalga oshiriladi. Hozirgi holatda market moduli real public price oladi va ichki order lifecycle ni yuritadi. Private signed order pipeline qo'shish uchun exchange private API endpointlari bo'yicha imzolash va retry queue yozilishi kerak.
