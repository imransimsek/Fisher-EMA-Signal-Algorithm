# 🤖 Fisher + EMA Band Telegram Bot

Açık kaynaklı, OKX public API’si ile kline verilerini çeken, Pine Script’ten uyarlanan Fisher Transform + EMA Band indikatörünü hesaplayan ve Telegram üzerinden sinyal bildirimleri gönderen bir Python projesi.

---

## 📖 İçindekiler

- [Türkçe](#-türkçe)  
  - [Özellikler](#özellikler)  
  - [Gereksinimler](#gereksinimler)  
  - [Kurulum](#kurulum)  
  - [Yapılandırma](#yapılandırma)  
  - [Çalıştırma](#çalıştırma)  
  - [Docker ile Çalıştırma](#docker-ile-çalıştırma)  
  - [GitHub Secrets](#github-secrets)  
  - [Katkıda Bulunma](#katkıda-bulunma)  
  - [Lisans](#lisans)  

- [English](#-english)  
  - [Features](#features)  
  - [Requirements](#requirements)  
  - [Installation](#installation)  
  - [Configuration](#configuration)  
  - [Usage](#usage)  
  - [Running with Docker](#running-with-docker)  
  - [GitHub Secrets](#github-secrets-1)  
  - [Contributing](#contributing)  
  - [License](#license)  

---

## 🇹🇷 Türkçe

### Özellikler
- OKX public API ile OHLCV (kline) verilerini çekme  
- Pine Script Fisher Transform + EMA Band indikatör hesaplama  
- `AŞIRI_ALIM` / `AŞIRI_SATIM` sinyallerinin tespiti  
- Telegram aracılığıyla anlık bildirim gönderme  
- APScheduler ile zamanlı taramalar (dakikalık, 5m, 15m, 30m, 1h)

### Gereksinimler
- Python 3.8+  
- Docker (opsiyonel)  
- Bir Telegram Bot Token ve Chat ID  
- (İsteğe bağlı) OKX API Key/Secret (public endpoint’ler için gerek yok)

### Kurulum
1. Depoyu klonlayın:  
   ```bash
   git clone https://github.com/KullaniciAdi/fteb-botV2.git
   cd fteb-botV2
   ```
2. Bir sanal ortam oluşturun ve etkinleştirin:  
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. Gerekli paketleri yükleyin:  
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

### Yapılandırma
1. Proje kökünde bir `.env` dosyası oluşturun veya örnek üzerinden kopyalayın:  
   ```bash
   cp .env.example .env
   ```
2. `.env` dosyasını kendi değerlerinizle doldurun:  
   ```ini
   OKX_API_KEY=
   OKX_API_SECRET=
   OKX_API_PASSPHRASE=
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   TELEGRAM_CHAT_ID=987654321
   SYMBOLS=BTC-USDT,ETH-USDT,SOL-USDT,AVAX-USDT
   INTERVALS=5m,15m,30m,1H
   FISHER_LENGTH=10
   EMA_LENGTH=5
   RANGE_OFFSET=1.0
   DEBUG=False
   ```

### Çalıştırma
- Ortam değişkenlerini yükleyip doğrudan çalıştırın:
  ```bash
  source .env && python main.py
  ```
- Test mesajı atmak isterseniz:
  ```bash
  python environment.py
  ```

### Docker ile Çalıştırma
1. Docker imajını oluşturun:
   ```bash
   docker build -t fisher-bot .
   ```
2. Konteyneri başlatın:
   ```bash
   docker run -d \
     --name fisher-bot \
     --env-file .env \
     -v $(pwd)/fisher_bot.log:/app/fisher_bot.log \
     fisher-bot
   ```
3. Logları izleyin:
   ```bash
   docker logs -f fisher-bot
   ```

### GitHub Secrets
- CI/CD veya GitHub Actions kullandığınızda `.env` dosyasındaki değerleri  
  GitHub → Settings → Secrets & variables → Actions altına ekleyin.

### Katkıda Bulunma
1. Fork’layın  
2. Yeni bir branch açın (`git checkout -b feature/yenifonksiyon`)  
3. Değişikliklerinizi commit edin (`git commit -m "Açıklayıcı mesaj"`)  
4. Push edin (`git push origin feature/yenifonksiyon`)  
5. Pull request açın

### Lisans
MIT © [Sizin İsminiz]

---

## 🇬🇧 English

### Features
- Fetches OHLCV (kline) data from OKX public API  
- Calculates Pine Script–style Fisher Transform + EMA Band indicators  
- Detects `OVERBOUGHT` / `OVERSOLD` signals  
- Sends real-time notifications via Telegram  
- Scheduled scans with APScheduler (every minute, 5m, 15m, 30m, 1h)

### Requirements
- Python 3.8+  
- Docker (optional)  
- A Telegram Bot Token & Chat ID  
- (Optional) OKX API Key/Secret (not required for public endpoints)

### Installation
1. Clone this repo:  
   ```bash
   git clone https://github.com/YourUserName/fteb-botV2.git
   cd fteb-botV2
   ```
2. Create & activate a virtual environment:  
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. Install dependencies:  
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

### Configuration
1. Copy the example env file:  
   ```bash
   cp .env.example .env
   ```
2. Fill in your values in `.env`:  
   ```ini
   OKX_API_KEY=
   OKX_API_SECRET=
   OKX_API_PASSPHRASE=
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   TELEGRAM_CHAT_ID=987654321
   SYMBOLS=BTC-USDT,ETH-USDT,SOL-USDT,AVAX-USDT
   INTERVALS=5m,15m,30m,1H
   FISHER_LENGTH=10
   EMA_LENGTH=5
   RANGE_OFFSET=1.0
   DEBUG=False
   ```

### Usage
- Run the bot:
  ```bash
  source .env && python main.py
  ```
- Test environment & Telegram connection:
  ```bash
  python environment.py
  ```

### Running with Docker
1. Build the Docker image:
   ```bash
   docker build -t fisher-bot .
   ```
2. Run the container:
   ```bash
   docker run -d \
     --name fisher-bot \
     --env-file .env \
     -v $(pwd)/fisher_bot.log:/app/fisher_bot.log \
     fisher-bot
   ```
3. View logs:
   ```bash
   docker logs -f fisher-bot
   ```

### GitHub Secrets
For CI/CD or GitHub Actions, add your `.env` variables under **Settings → Secrets & variables → Actions**.

### Contributing
1. Fork the repository  
2. Create a new branch (`git checkout -b feature/new-feature`)  
3. Commit your changes (`git commit -m "Add new feature"`)  
4. Push to the branch (`git push origin feature/new-feature`)  
5. Open a Pull Request

### License
MIT © [Your Name]
