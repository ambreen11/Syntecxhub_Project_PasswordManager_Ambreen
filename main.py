import json
import os
import base64
import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

vault_file = "vault.json"

# ---------------- Key Derivation ---------------- #
def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

# ---------------- Encryption ---------------- #
def encrypt_data(data, key):
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aes.encrypt(nonce, json.dumps(data).encode(), None)
    return nonce, ciphertext
1

# ---------------- Decryption ---------------- #
def decrypt_data(nonce, ciphertext, key):
    aes = AESGCM(key)
    data = aes.decrypt(nonce, ciphertext, None)
    return json.loads(data.decode())

# ---------------- Load Vault ---------------- #
def load_vault(password):
    if not os.path.exists(vault_file):
        return {"accounts": []}, os.urandom(16)
    try:
        with open(vault_file, "r") as f:
            vault = json.load(f)
        salt = base64.b64decode(vault["salt"])
        nonce = base64.b64decode(vault["nonce"])
        ciphertext = base64.b64decode(vault["ciphertext"])
        key = derive_key(password, salt)
        data = decrypt_data(nonce, ciphertext, key)
        return data, salt
    except Exception:
        print("\n[!] Error: Invalid master password or corrupted vault file.")
        exit(1)

# ---------------- Save Vault ---------------- #
def save_vault(data, password, salt):
    key = derive_key(password, salt)
    nonce, ciphertext = encrypt_data(data, key)
    vault = {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }
    with open(vault_file, "w") as f:
        json.dump(vault, f, indent=4)

# ---------------- Features ---------------- #
def add_entry(data):
    print("\n--- Add New Entry ---")
    site = input("Site/Service Name: ").strip()
    username = input("Username/Email: ").strip()
    password = getpass.getpass("Password to store: ")

    if not site or not username or not password:
        print("[!] All fields are required. Entry cancelled.")
        return

    data["accounts"].append({
        "site": site,
        "username": username,
        "password": password
    })
    print(f"[+] Successfully added credentials for {site}!")

def list_entries(data):
    if not data["accounts"]:
        print("\n[-] No accounts stored yet.")
        return
    print("\n--- Stored Credentials ---")
    for idx, acc in enumerate(data["accounts"]):
        print(f"[{idx}] Site: {acc['site']} | User: {acc['username']} | Pass: {acc['password']}")

def search_entries(data):
    print("\n--- Search Entries ---")
    query = input("Enter search term (site or username): ").strip().lower()
    if not query:
        return

    results = [acc for acc in data["accounts"] if query in acc['site'].lower() or query in acc['username'].lower()]

    if not results:
        print("[-] No matching records found.")
        return

    print(f"\n[+] Found {len(results)} match(es):")
    for acc in results:
        print(f"Site: {acc['site']} | User: {acc['username']} | Pass: {acc['password']}")

def delete_entry(data):
    if not data["accounts"]:
        print("\n[-] Vault is empty. Nothing to delete.")
        return

    list_entries(data)
    try:
        idx = int(input("\nEnter the index number [#] of the entry to delete: "))
        if 0 <= idx < len(data["accounts"]):
            removed = data["accounts"].pop(idx)
            print(f"[+] Successfully deleted entry for {removed['site']}.")
        else:
            print("[!] Invalid index number.")
    except ValueError:
        print("[!] Please enter a valid number.")

# ---------------- Main Interface ---------------- #
def main():
    print("==========================")
    print("   SECURE PASSWORD VAULT  ")
    print("==========================")
    master_password = getpass.getpass("Enter your Master Password: ")

    if not master_password:
        print("[!] Master password cannot be blank.")
        return

    data, salt = load_vault(master_password)
    print("[+] Vault accessed successfully.")

    while True:
        print("\nMenu Options:")
        print("1. Add Entry")
        print("2. List All Entries")
        print("3. Search Entries")
        print("4. Delete Entry")
        print("5. Save & Exit")

        choice = input("\nSelect an option (1-5): ").strip()

        if choice == "1":
            add_entry(data)
        elif choice == "2":
            list_entries(data)
        elif choice == "3":
            search_entries(data)
        elif choice == "4":
            delete_entry(data)
        elif choice == "5":
            save_vault(data, master_password, salt)
            print("[+] Vault encrypted and saved safely. Goodbye!")
            break
        else:
            print("[!] Invalid choice. Please choose between 1 and 5.")

if __name__ == "__main__":
    main()