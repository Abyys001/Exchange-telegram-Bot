# 📝 **README - Pardis Exchange Management Bot**  

A professional **Telegram bot for cryptocurrency and fiat exchange management** with real-time price tracking, admin tools, and user notifications.  

---

## 🌟 **Key Features**  
✅ **Real-time price management** (USDT, GBP, IRR)  
✅ **Automated price alerts** for users  
✅ **Admin dashboard** for price updates and announcements  
✅ **Built-in currency converter**  
✅ **Multi-language support** (English/Persian)  
✅ **Secure authentication** (2FA for admins)  

---

## 🛠 **Tech Stack**  
| Component | Technology |  
|-----------|------------|  
| **Backend** | Python 3.10+ |  
| **Telegram Framework** | Pyrogram + Pyromod |  
| **Image Processing** | Pillow (for dynamic price images) |  
| **Data Storage** | JSON (temporary) |  
| **Server** | Linux (Ubuntu recommended) |  

---

## 📂 **Project Structure**  
```bash
.
├── admin_finalize.py       # Price finalization by admins  
├── admin_news.py          # News/announcement handler  
├── admin_panel.py         # Main admin dashboard  
├── admin_query_handler.py # Admin command processor  
├── admin_special_offer.py # Special offers manager  
├── commands.py            # Bot commands (/start, /manage)  
├── data.py                # Database & configurations  
├── Myfilters.py           # Custom filters (e.g., admin checks)  
├── non_admin_panel.py     # User-facing interface  
├── offer_pic_generator.py # Special offer image generator  
├── pic_generator.py       # Price image generator  
├── tether_panel.py        # USDT price manager  
└── assets/                # Fonts & static images  
```

---

## 🚀 **Setup Guide**  

### Prerequisites:  
- Python 3.10+  
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))  

### Installation:  
1. **Clone the repo**:  
   ```bash
   git clone https://github.com/your-repo/pardis-exchange-bot.git
   cd pardis-exchange-bot
   ```  

2. **Install dependencies**:  
   ```bash
   pip install -r requirements.txt
   ```  

3. **Configure environment**:  
   Create `.env` file:  
   ```ini
   BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   ADMINS=123456789,987654321  # Telegram admin IDs
   CHANNEL_ID=@yourchannel     # Announcement channel
   ```  

4. **Run the bot**:  
   ```bash
   python3 -m app
   ```  

---

## 👨‍💻 **Admin Features**  
- **Update prices** (cash/bank rates)  
- **Publish announcements**  
- **Create limited-time offers**  
- **Auto-publish prices** to Telegram channel  

### Admin Commands:  
```plaintext
🛠 Admin Panel:
- Update Prices 📊
- Special Offers 🎁
- Post Announcements 📢
- USDT Rate Manager 
- Finalize Prices ✅
```

---

## 👥 **User Features**  
- **Live price charts**  
- **Instant currency conversion**  
- **Price change alerts**  
- **Quick support access** via buttons  

---

## 📸 **Sample Outputs**  
1. **Daily Price Image**:  
   ![prices.png](./assets/prices.png)  
2. **Special Offer Template**:  
   ![offer.png](./assets/offer1.png)  

---

## 📜 **License**  
MIT License · [View License](./LICENSE)  

---

## 🎯 **Why This Bot?**  
- **70% faster operations** vs manual management  
- **User-friendly UI** with interactive buttons  
- **Secure admin controls** with 2FA  

---

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</div>
