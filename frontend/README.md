
Frontend Hero Section qo'shildi

- React + Tailwind asosida full screen video hero
- Video URL static source sifatida ulandi
- Responsive headline va custom SVG CTA tugma qo'shildi

Backend exchange routing qo'shildi

- Binance Bybit OKX KuCoin adapterlar qo'shildi
- Market service fallback va multi exchange routing bilan yangilandi

Ishga tushirish

Backend:
- pip install -r requirements.txt
- uvicorn app.main:app --host 0.0.0.0 --port 10000

Frontend:
- cd frontend
- npm install
- npm run dev

Cheklovlar

- Hamma birjada real order ishlashi uchun har bir birja private API signed endpointlari va alohida KYC/permissions kerak
- Hozirgi kod multi exchange adapter arxitekturasini beradi, real trading credentials bilan to'ldirish kerak
