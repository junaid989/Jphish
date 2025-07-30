# JPhish

**JPhish** is a simple phishing simulation tool developed in Python and HTML, designed for **educational** and **cybersecurity awareness** purposes. It mimics popular login pages (like Facebook and Instagram) to demonstrate how phishing attacks can be crafted and how users can stay protected.

> ⚠️ **Disclaimer:** This tool is intended for **educational purposes only**. Do not use it for illegal or unethical activities. The author is not responsible for any misuse.

---

## 📁 Project Structure
jphish/
├── templates/
│ ├── facebook.html
│ ├── instagram.html
│ ├── login.html
│ └── success.html
├── credentials.txt # Stores captured login credentials
├── sessions.log # Logs session data
└── jphish.py # Main Python script




---

## ⚙️ How It Works

1. The `jphish.py` script runs a simple web server.
2. Fake login pages (HTML) are served to the user.
3. When someone logs in, the entered credentials are stored in `credentials.txt`.
4. After logging in, the user is redirected to a fake success page.

---

## 🚀 How to Run

### 🧱 Requirements
- Python 3.x
- Flask (you can install it with `pip install flask`)

### ▶️ Start the Tool

```bash
python jphish.py

