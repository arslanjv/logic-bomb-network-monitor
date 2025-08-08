# 🚨 Logic Bomb Network Monitor 🚨

A stealthy **network monitoring & alerting tool** for **ethical testing only**.  
Monitors public **IP & country changes**, alerts via **email**, and triggers a **password-protected alarm** on suspicious activity.

> ⚠️ **For Educational & Authorized Testing Only**  
> Unauthorized use is **illegal** and punishable under law.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🌍 **IP & Country Monitoring** | Tracks changes in your public IP & location |
| 📡 **Connectivity Alerts** | Notifies when internet is lost or restored |
| 📧 **Email Notifications** | Sends detailed system info to your email |
| 🔊 **Audible Alarm + GUI** | Password-protected alarm with popup window |
| ⏱️ **Custom Intervals** | Adjustable check & retry times |
| 📝 **Logging** | Saves all activity to `network_monitor.log` |

---

## ⚙️ Quick Setup

### 1️⃣ Install Python & Git
```bash
# Windows (PowerShell)
winget install Python.Python.3.10
winget install Git.Git
```

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/arslanjv/logic-bomb-network-monitor.git
cd logic-bomb-network-monitor
```

### 3️⃣ Install Dependencies
```bash
pip install requests pyinstaller
```

---

## 🔧 Configuration

Edit `logic_bomb.py` and update `CONFIG`:
```python
CONFIG = {
    'check_interval': 5, # seconds between IP checks
    'retry_interval': 10, # seconds between internet retry
    'alarm_password': '123', # Password to stop alarm
    'email_config': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': 'your_email@example.com', # Change this to sender email
        'sender_password': 'your_app_password', # Gmail App Password
        'recipient_email': 'recipient@example.com' # Change this to recipient email
    },
    'log_file': 'network_monitor.log' # Log file in current directory
}
```

💡 **Tip:** For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833).

---

## ▶️ Running

### Run Directly
```bash
python logic_bomb.py
```

### Build `.exe` (Windows)
```bash
pyinstaller --onefile --windowed --name=pic logic_bomb.py
```
📁 Output: `dist/pic.exe`

---

## 🎨 Optional Customization

### Change Icon (Windows)

1. Prepare an image (`.png` or `.jpg`).
2. Convert it to `.ico`:
   - Use an online converter like [ICOConvert](https://icoconvert.com/).
   - Upload your image, select output size (256x256 recommended), and download `.ico`.
3. Download & install [Resource Hacker](http://www.angusj.com/resourcehacker/).
4. Open your `.exe` in Resource Hacker:
   - Go to **Icon Group** → `1` → `1033` (or similar).
   - Right-click `Icon Group` → `Replace Icon...`.
   - Click **Open file with new icon...**, select your `.ico`, then **Replace**.
5. Save changes (`File → Save`).

---

### Extension Spoofing (Unicode RLO Trick)

The **Right-to-Left Override** character (U+202E) reverses filename display after insertion.

**Steps:**
1. Rename `pic.exe` → `picgnp.exe`.
2. Place cursor **between `c` and `g`** in `picgnp.exe`.
3. Right-click → **Insert Unicode control character** → **RLO (U+202E)**.
4. Press Enter.

💡 Windows will now display it as **picexe.png**, but it's still an `.exe` internally.

---

## 🛡 Security Notes

- ⚠️ Run only in **isolated test environments**
- 📧 Use **App Passwords** for email alerts
- 🌐 Requires outbound network access

---

## 👨‍💻 Author

**Muhammad Arsalan Javed**  
[GitHub Profile](https://github.com/arslanjv)

---

## 📜 License
[MIT License](https://github.com/arslanjv/logic-bomb-network-monitor/edit/main/README.md) — Use responsibly.
