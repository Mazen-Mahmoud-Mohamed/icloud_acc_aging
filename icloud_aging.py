
import csv
import time
import base64
import requests
import configparser
from termcolor import colored
from colorama import Fore, Style

from libsrp import Srp, Mode, Client
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from utils import (
    bytes_from_bigint,
    Hash,
    hash as hash_func,
    to_hex,
)

from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import filedialog



import customtkinter as ctk
import threading

'''import sys
if sys.platform == "win32":
    import ctypes
    ctypes.windll.user32.ShowWindow(
        ctypes.windll.kernel32.GetConsoleWindow(), 0
    )'''

stop_event = threading.Event()




def display_banner():
    banner = """


███╗   ███╗           ███╗   ███╗
████╗ ████║           ████╗ ████║
██╔████╔██║           ██╔████╔██║
██║╚██╔╝██║           ██║╚██╔╝██║
██║ ╚═╝ ██║    ██╗    ██║ ╚═╝ ██║
╚═╝     ╚═╝    ╚═╝    ╚═╝     ╚═╝

_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
   Discord User:
   (1)   mazenmahmoud6550
   (2)   som3aa2001
_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-    
    """
    print(colored(banner, "red"))


# ================= CONFIG =================

def load_config():
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")

    use_proxy = config.getboolean("Settings", "use_proxy", fallback=False)
    proxy_string = config.get("Settings", "proxy", fallback="")

    return use_proxy, proxy_string


def parse_proxy(proxy_string):
    """Parse proxy string and return formatted proxy dict."""
    if not proxy_string or proxy_string.strip() == '':
        return None

    proxy_string = proxy_string.strip()

    if '://' in proxy_string:
        protocol = proxy_string.split('://')[0].lower()
        rest = proxy_string.split('://')[1]

        if '@' in rest:
            auth_part = rest.split('@')[0]
            server_part = rest.split('@')[1]
            user, password = auth_part.split(':')

            if protocol in ['socks5', 'socks5h']:
                return {
                    'http': f'socks5://{user}:{password}@{server_part}',
                    'https': f'socks5://{user}:{password}@{server_part}'
                }
            elif protocol == 'socks4':
                return {
                    'http': f'socks4://{user}:{password}@{server_part}',
                    'https': f'socks4://{user}:{password}@{server_part}'
                }
            else:
                return {
                    'http': f'http://{user}:{password}@{server_part}',
                    'https': f'http://{user}:{password}@{server_part}'
                }
        else:
            if protocol in ['socks5', 'socks5h']:
                return {
                    'http': f'socks5://{rest}',
                    'https': f'socks5://{rest}'
                }
            elif protocol == 'socks4':
                return {
                    'http': f'socks4://{rest}',
                    'https': f'socks4://{rest}'
                }
            else:
                return {
                    'http': f'http://{rest}',
                    'https': f'http://{rest}'
                }

    parts = proxy_string.split(':')

    if len(parts) == 2:
        return {
            'http': f'http://{proxy_string}',
            'https': f'http://{proxy_string}'
        }
    elif len(parts) == 4:
        ip, port, user, password = parts
        return {
            'http': f'http://{user}:{password}@{ip}:{port}',
            'https': f'http://{user}:{password}@{ip}:{port}'
        }
    elif '@' in proxy_string:
        auth_part = proxy_string.split('@')[0]
        server_part = proxy_string.split('@')[1]
        user, password = auth_part.split(':')
        return {
            'http': f'http://{user}:{password}@{server_part}',
            'https': f'http://{user}:{password}@{server_part}'
        }
    else:
        return {
            'http': f'http://{proxy_string}',
            'https': f'http://{proxy_string}'
        }

# ================= CORE =================

class iCloudCrypto:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.srp = Srp(Mode.GSA, Hash.SHA256, 2048)
        self.srp_client: Client = self.srp.new_client(I=bytes(username, encoding='utf-8'), p=bytes("", encoding='utf-8'))

    def get_client_ephemeral(self):
        return base64.b64encode(bytes_from_bigint(self.srp_client.A)).decode('utf-8')

    def derive_password(self, protocol, salt, iterations):
        pass_hash = hash_func(self.srp.h, self.password.encode())

        if protocol == 's2k_fo':
            pass_hash = to_hex(pass_hash)

        salt_bytes = base64.b64decode(salt)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=iterations,
            backend=default_backend()
        )
        derived_key = kdf.derive(pass_hash)
        return derived_key

    def get_proof_values(self, derived_password, server_public_value, salt):
        salt_bytes = base64.b64decode(salt)
        server_public_value_bytes = base64.b64decode(server_public_value)

        self.srp_client.p = derived_password
        M1 = bytes.fromhex(self.srp_client.generate(salt_bytes, server_public_value_bytes))
        M2 = self.srp_client.generate_m2()

        m1_base64 = base64.b64encode(M1).decode('utf-8')
        m2_base64 = base64.b64encode(M2).decode('utf-8')

        return m1_base64, m2_base64


def age_child(worker_id, proxy_dict, child_email, child_password,ans1, ans2, ans3, day, month, year):

    try:
        child_email_norm = child_email.strip().lower()
        print(f"{Fore.CYAN}[→] {worker_id} - Changing birthday for: {child_email}{Style.RESET_ALL}")
        authenticator = iCloudCrypto(username=child_email_norm, password=child_password)
        s = requests.Session()

        # Setup proxy if provided
        if proxy_dict:
            s.proxies.update(proxy_dict)
            print(f"{Fore.CYAN}[→] {worker_id} - Using proxy:")
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://idmsa.apple.com',
            'Referer': 'https://idmsa.apple.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'X-Apple-Auth-Attributes': 'Pj3te/Xq79OI7j0k7dMRjdjlseyBdgNjmLnR2LRcOmSuZl0agcCuddMrtdbV/EvoT3E5ztGXIKeiIqtvuPI4Sit8edBolHL6qHyr7i+N0/ty0P8gh08bzvtqnjTl7/FPMEeDuK3oTOxJBN6YAXcarM1MfwEvJdeYiyp4uFS646xP4QKaX8ZAMErIM6Dd9BkZ3tArO33g54ky2Bv+9L3JaN4IMQdxvxLriqpn2TZz0DpVg59HerWIAQi2dG+8HIwQytKRLQufDGrhcL+0+xj6ocUAFdXCvQmAjg==',
            'X-Apple-Domain-Id': '11',
            'X-Apple-Frame-Id': 'auth-66cbb9e9-spb3-vppo-yn2e-6vpkemfx',
            'X-Apple-I-FD-Client-Info': '{"U":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36","L":"en-US","Z":"GMT+02:00","V":"1.1","F":"sla44j1e3NlY5BNlY5BSs5uQ084akLJ6N38.7Fx_MKR0odm_dhrxbuJjkWxv55BPfs1eNk4ug4DKpDK1c5vmjoaUW2vqBBNlY5BPY25BNnOVgw24uy.2Wf"}',
            'X-Apple-ID-Session-Id': '920F016D116BE3AE42169EAC8539257D0B496E18A606863FD3E0A6DCA213C38FDBA68D16A830BE4BAFF09E1E07DD6040829B227B9446A615B0E80DE1D3EB8C2874EAA5E9DFAE98033910CB972B385F3991679060ADAB718B82D799C1D4CC6D176CFA196C2BA315D2DE615C9998C861E9B86004FB13414A8B',
            'X-Apple-OAuth-Client-Id': 'af1139274f266b22b68c2a3e7ad932cb3c0bbe854e13a79af78dcc73136882c3',
            'X-Apple-OAuth-Client-Type': 'firstPartyAuth',
            'X-Apple-OAuth-Redirect-URI': 'https://account.apple.com',
            'X-Apple-OAuth-Response-Mode': 'web_message',
            'X-Apple-OAuth-Response-Type': 'code',
            'X-Apple-OAuth-State': 'auth-66cbb9e9-spb3-vppo-yn2e-6vpkemfx',
            'X-Apple-Privacy-Consent': 'true',
            'X-Apple-Privacy-Consent-Accepted': 'true',
            'X-Apple-Widget-Key': 'af1139274f266b22b68c2a3e7ad932cb3c0bbe854e13a79af78dcc73136882c3',
            'X-Requested-With': 'XMLHttpRequest',
        }
        json_data = {
            'a': authenticator.get_client_ephemeral(),
            'accountName': child_email,
            'protocols': ['s2k', 's2k_fo'],
        }

        response = s.post('https://idmsa.apple.com/appleauth/auth/signin/init', headers=headers, json=json_data)
        init_data = response.json()
        derived_password = authenticator.derive_password(
            init_data["protocol"],
            init_data["salt"],
            init_data["iteration"]
        )
        m1_proof, m2_proof = authenticator.get_proof_values(
            derived_password,
            init_data["b"],
            init_data["salt"]
        )

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://idmsa.apple.com',
            'Referer': 'https://idmsa.apple.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'X-APPLE-HC': '1:10:20260112121003:66b28f8b48a455fa8d90de906bf54310::181',
            'X-Apple-Auth-Attributes': 'BH75VSlOAN9jLxPKVmxJyDdV6wqPZcxnKYWHMTB2iqoe+SVBNQczVSjZ1H2+jmQ6hVpGFWiiL3xmpGwQW83eJjt06KJgp5GystoQnHxJmQG002LxdgBkWOFAelMLey2okeL+X7oeoXq/8hXbeeIvWREG27DxBPXyhjN3EFET3xRCDyl1vIVKMSBBmBdsMrXGdyiKtW5KNxTmPhv0HaPWgqCeQwSS2Zf0EgGw8NoNmM8m142wnwCKnz+xmfAcWLGKEZZE12Wh/HMe7RdkKzVDNfIAFqHIVG9q4g==',
            'X-Apple-Domain-Id': '11',
            'X-Apple-Frame-Id': 'auth-yp4r1txm-002y-st2l-0bdx-m3mu2ehh',
            'X-Apple-I-FD-Client-Info': '{"U":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36","L":"en-US","Z":"GMT+02:00","V":"1.1","F":"sla44j1e3NlY5BNlY5BSs5uQ084akLJ6KGTrKMGpKSKk6Hb9LarUqUdHz16rgNNl_jV9dY.MekJseY_Fe0ixIwgAxHUTlWY5BNlYJNNlY5QB4bVNjMk.8Ty"}',
            'X-Apple-ID-Session-Id': 'FA7C676E3B6D330F7D5B0218402825111A4A577CF150E129E5620233EEE2AFC14E229A50696833A89BBD4A4FCE9C9269843BA3AAB8CEA109CD117A2FD6CC3A03B29042AB0B9EFB0FB84E5908E1F0FBAC86058F31491051454493D1067FEE43668E302FC205ED8F5F0E65BD87CFA89DA9A4B153E479919FF0',
            'X-Apple-OAuth-Client-Id': 'af1139274f266b22b68c2a3e7ad932cb3c0bbe854e13a79af78dcc73136882c3',
            'X-Apple-OAuth-Client-Type': 'firstPartyAuth',
            'X-Apple-OAuth-Redirect-URI': 'https://account.apple.com',
            'X-Apple-OAuth-Response-Mode': 'web_message',
            'X-Apple-OAuth-Response-Type': 'code',
            'X-Apple-OAuth-State': 'auth-yp4r1txm-002y-st2l-0bdx-m3mu2ehh',
            'X-Apple-Privacy-Consent': 'true',
            'X-Apple-Privacy-Consent-Accepted': 'true',
            'X-Apple-Widget-Key': 'af1139274f266b22b68c2a3e7ad932cb3c0bbe854e13a79af78dcc73136882c3',
            'X-Requested-With': 'XMLHttpRequest',
        }

        params = {'isRememberMeEnabled': 'true'}

        json_data = {
            'accountName': child_email_norm,
            'password': child_password,
            'rememberMe': True,
            'm1': m1_proof,
            'c': init_data["c"],
            'm2': m2_proof,
        }

        response = s.post(
            'https://idmsa.apple.com/appleauth/auth/signin/complete',
            params=params,
            headers=headers,
            json=json_data,
        )

        scnt = response.headers.get('scnt')
        if not scnt:
            print(f"{Fore.RED}[-] {worker_id} - Failed to get scnt for {child_email}{Style.RESET_ALL}")
            return False

        headers.update({'scnt': scnt})

        response = s.get('https://idmsa.apple.com/appleauth/auth', headers=headers)
        print(response.status_code)
        if response.status_code == 401:
            print(f"{Fore.RED}[-] {worker_id} - 401 Unauthorized for {child_email}{Style.RESET_ALL}")
            return "RELOGIN"

        try:
            boot_data = response.json()

        except Exception as e:
            print(f"{Fore.RED}[-] {worker_id} - boot_args not found for {child_email}{Style.RESET_ALL}")
            return "RELOGIN"

        questions = boot_data["securityQuestions"]["questions"]

        # Match answers to questions
        if questions[0]['id'] in range(130, 136):
            v1 = ans1
        elif questions[0]['id'] in range(136, 142):
            v1 = ans2
        elif questions[0]['id'] in range(142, 148):
            v1 = ans3
        else:
            v1 = ans1

        if questions[1]['id'] in range(130, 136):
            v2 = ans1
        elif questions[1]['id'] in range(136, 142):
            v2 = ans2
        elif questions[1]['id'] in range(142, 148):
            v2 = ans3
        else:
            v2 = ans2

        json_data = {
            'questions': [
                {
                    'question': questions[0]['question'],
                    'answer': v1,
                    'id': questions[0]['id'],
                    'number': questions[0]['number']
                },
                {
                    'question': questions[1]['question'],
                    'answer': v2,
                    'id': questions[1]['id'],
                    'number': questions[1]['number']
                }
            ]
        }

        response = s.post(
            'https://idmsa.apple.com/appleauth/auth/verify/questions',
            headers=headers,
            json=json_data,
        )

        token = response.headers.get("x-apple-repair-session-token")
        if not token:
            print(f"{Fore.RED}[-] {worker_id} - Failed to get repair token for {child_email}{Style.RESET_ALL}")
            return False

        headers.update({'x-apple-repair-session-token': token})
        response = s.post('https://idmsa.apple.com/appleauth/auth/repair/complete', headers=headers)

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://account.apple.com',
            'Referer': 'https://account.apple.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'X-Apple-I-Request-Context': 'ca',
            'X-Apple-I-TimeZone': 'Africa/Cairo',
        }

        response = s.get('https://appleid.apple.com/account/manage', headers=headers)
        scnt1 = response.headers.get('scnt')

        if not scnt1:
            print(f"{Fore.RED}[-] {worker_id} - Failed to get scnt1 for {child_email}{Style.RESET_ALL}")
            return False

        headers.update({'scnt': scnt1})
        headers.update({'X-Apple-Api-Key': 'cbf64fd6843ee630b463f358ea0b707b'})

        '''json_data = {
            'dayOfMonth': '01',
            'monthOfYear': '01',
            'year': '1990',
        }'''

        json_data = {
            'dayOfMonth': day,
            'monthOfYear': month,
            'year': year,
        }

        response = s.post(
            'https://appleid.apple.com/account/manage/security/birthday/verify',
            headers=headers,
            json=json_data,
        )

        response = s.put(
            'https://appleid.apple.com/account/manage/security/birthday',
            headers=headers,
            json=json_data,
        )

        if response.status_code == 200:
            print(f"{Fore.GREEN}[✓] {worker_id} - Birthday changed for: {child_email}{Style.RESET_ALL}")
            return True
        else:
            print(
                f"{Fore.RED}[-] {worker_id} - Failed to change birthday for {child_email} (Status: {response.status_code}){Style.RESET_ALL}")
            return False

    except Exception as e:
        print(f"{Fore.RED}[-] {worker_id} - Error changing birthday for {child_email}: {e}{Style.RESET_ALL}")
        return False


def age_child_with_retry(worker_id, proxy_dict, child_email, child_password,ans1, ans2, ans3, day, month, year, max_retries=10, delay=3):
    if stop_event.is_set():
        return False

    for attempt in range(1, max_retries + 1):
        if stop_event.is_set():
            return False

        print(colored(
            f"[→] Aging attempt {attempt}/{max_retries} for {child_email}",
            "cyan"
        ))

        result = age_child(
            worker_id,
            proxy_dict,
            child_email,
            child_password,
            ans1,
            ans2,
            ans3,
            day,
            month,
            year
        )

        # ✅ نجاح
        if result is True:
            print(colored(
                f"[✓] Aging success for {child_email}",
                "green"
            ))
            return True

        # 🔄 Session اتحرقت (401 / boot_args)
        if result == "RELOGIN":
            print(colored(
                f"[!] {child_email} session burned → retrying fresh session",
                "yellow"
            ))
            time.sleep(delay + 2)
            continue  # ⬅️ يعيد من الأول Session جديدة

        # ❌ فشل عادي
        print(colored(
            f"[!] Aging failed (attempt {attempt}), retrying...",
            "yellow"
        ))
        time.sleep(delay)

    print(colored(
        f"[✗] Aging permanently failed for {child_email}",
        "red"
    ))
    return False

def finish_ui():
    app.after(0, lambda: (
        start_btn.configure(state="normal"),
        csv_btn.configure(state="normal"),
        stop_btn.configure(state="disabled"),
        progress_var.set(1)
    ))

def log_callback(msg):
    app.after(0, lambda: (
        log_box.insert("end", msg + "\n"),
        log_box.see("end")
    ))
def log(msg, tag="INFO"):
    app.after(0, lambda: (
        log_box.insert("end", msg + "\n", tag),
        log_box.see("end")
    ))

def log_info(msg):
    log(msg, "INFO")

def log_success(msg):
    log(msg, "SUCCESS")

def log_error(msg):
    log(msg, "ERROR")

def log_retry(msg):
    log(msg, "RETRY")

def log_system(msg):
    log(msg, "SYSTEM")



def run_aging(MAX_THREADS, log_callback, day, month, year, csv_path):

    log_system("[*] Starting aging process...")

    use_proxy, proxy_string = load_config()
    proxy_dict = parse_proxy(proxy_string) if use_proxy else None

    SUCCESS = []
    FAILED = []
    ALL_ROWS = []

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        ALL_ROWS = list(reader)

    total = len(ALL_ROWS)
    if total == 0:
        log_callback("[!] CSV file is empty")
        finish_ui()
        return

    done = 0

    def process_row(row):
        email = row["email"]
        log_info(f"[→] Aging {email}")

        ok = age_child_with_retry(
            "AGING",
            proxy_dict,
            email,
            row["password"],
            row["ans1"],
            row["ans2"],
            row["ans3"],
            day,
            month,
            year
        )
        return ok, row

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(process_row, row) for row in ALL_ROWS]

        for future in as_completed(futures):
            if stop_event.is_set():
                log_system("[!] Process stopped by user")
                break

            ok, row = future.result()
            done += 1

            app.after(0, lambda v=done/total: progress_var.set(v))

            if ok:
                new_row = row.copy()
                new_row["birthdate"] = f"{int(day)}/{int(month)}/{year}"
                SUCCESS.append(new_row)
                log_success(f"[✓] {row['email']}")
            else:
                FAILED.append(row)
                log_error(f"[✗] {row['email']}")

    if SUCCESS:
        with open("aging_success.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=SUCCESS[0].keys())
            w.writeheader()
            w.writerows(SUCCESS)

    if FAILED:
        with open("accounts.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FAILED[0].keys())
            w.writeheader()
            w.writerows(FAILED)

    log_callback("[✓] Aging finished.")
    finish_ui()

# ================= GUI =================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
def on_close():
    stop_event.set()   # يوقف أي Thread شغالة
    app.destroy()      # يقفل الـ GUI
    import sys
    sys.exit(0)        # يقفل البروسيس كله (CMD كمان)

app.protocol("WM_DELETE_WINDOW", on_close)

app.title("iCloud Aging Tool")
app.geometry("700x520")
app.minsize(650, 500)
app.resizable(True, True)


selected_csv = None
progress_var = ctk.DoubleVar(value=0)

# ================= Title =================
title = ctk.CTkLabel(
    app,
    text="iCloud Aging Tool",
    font=("Segoe UI", 22, "bold")
)
title.pack(pady=10)

# ================= Threads =================
threads_frame = ctk.CTkFrame(app)
threads_frame.pack(pady=5)

ctk.CTkLabel(threads_frame, text="Threads:").pack(side="left", padx=10)

threads_entry = ctk.CTkEntry(threads_frame, width=80)
threads_entry.insert(0, "3")
threads_entry.pack(side="left")

# ================= Date =================
date_frame = ctk.CTkFrame(app)
date_frame.pack(pady=5)

ctk.CTkLabel(date_frame, text="Day").pack(side="left", padx=5)
day_entry = ctk.CTkEntry(date_frame, width=50)
day_entry.insert(0, "01")
day_entry.pack(side="left")

ctk.CTkLabel(date_frame, text="Month").pack(side="left", padx=5)
month_entry = ctk.CTkEntry(date_frame, width=50)
month_entry.insert(0, "01")
month_entry.pack(side="left")

ctk.CTkLabel(date_frame, text="Year").pack(side="left", padx=5)
year_entry = ctk.CTkEntry(date_frame, width=70)
year_entry.insert(0, "1990")
year_entry.pack(side="left")

# ================= Progress =================
# ================= CSV Button =================
def choose_csv():
    global selected_csv
    path = filedialog.askopenfilename(
        title="Select accounts CSV",
        filetypes=[("CSV files", "*.csv")]
    )
    if path:
        selected_csv = path
        log_success(f"[✓] Selected file: {path}")

csv_btn = ctk.CTkButton(
    app,
    text="Select CSV File",
    command=choose_csv,
    height=42,
    width=260,
    fg_color="#2b6cb0",
    hover_color="#2c5282",
    text_color="white",
    corner_radius=10,
    font=("Segoe UI", 13, "bold")
)
csv_btn.pack(pady=10)

# ================= Buttons =================
button_frame = ctk.CTkFrame(app)
button_frame.pack(pady=5)

def start_aging():
    try:
        max_threads = int(threads_entry.get())
        day = day_entry.get().zfill(2)
        month = month_entry.get().zfill(2)
        year = year_entry.get()

        if not day.isdigit() or not month.isdigit() or not year.isdigit():
            raise ValueError
    except:
        log_error("❌ Invalid input")
        return

    if not selected_csv:
        log_system("⚠️ Please select CSV file first")
        return

    # 🔒 Lock UI
    start_btn.configure(state="disabled")
    csv_btn.configure(state="disabled")
    stop_btn.configure(state="normal")

    progress_var.set(0)
    stop_event.clear()

    threading.Thread(
        target=run_aging,
        args=(max_threads, log_callback, day, month, year, selected_csv),
        daemon=True
    ).start()



def stop_aging():
    stop_event.set()
    log_system("🛑 Stopping process...")

    # 🔓 Unlock UI
    start_btn.configure(state="normal")
    csv_btn.configure(state="normal")
    stop_btn.configure(state="disabled")


stop_btn = ctk.CTkButton(
    button_frame,
    text="Stop",
    command=stop_aging,
    height=44,
    width=260,
    fg_color="#c53030",
    hover_color="#9b2c2c",
    text_color="white",
    corner_radius=10,
    font=("Segoe UI", 14, "bold")
)
stop_btn.pack(pady=6)


start_btn = ctk.CTkButton(
    button_frame,
    text="Start Aging",
    command=start_aging,
    height=44,
    width=260,
    fg_color="#38a169",
    hover_color="#2f855a",
    text_color="white",
    corner_radius=10,
    font=("Segoe UI", 14, "bold")
)
start_btn.pack(pady=6)


# ================= Progress Bar =================


progress_frame = ctk.CTkFrame(app)
progress_frame.pack(fill="x", padx=20, pady=(5, 10))

progress = ctk.CTkProgressBar(
    progress_frame,
    variable=progress_var,
    height=14,
    corner_radius=10,
    progress_color="#38a169"
)

progress.pack(fill="x", padx=10)
progress.set(0)


# ================= Log =================
log_frame = ctk.CTkFrame(app)
log_frame.pack(padx=15, pady=(5, 10), fill="both", expand=True)

log_box = ctk.CTkTextbox(log_frame)
log_box.pack(fill="both", expand=True, padx=10, pady=10)

# 🎨 Log colors (Text Tags)
log_box.tag_config("INFO", foreground="#3498db")     # أزرق (شغال)
log_box.tag_config("SUCCESS", foreground="#2ecc71")  # أخضر (نجاح)
log_box.tag_config("ERROR", foreground="#e74c3c")    # أحمر (فشل)
log_box.tag_config("RETRY", foreground="#f1c40f")    # أصفر (إعادة محاولة)
log_box.tag_config("SYSTEM", foreground="#bdc3c7")   # رمادي (سيستم)



app.mainloop()
