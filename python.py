import json
import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

VAULT_FILE = "vault.json"

# -------- KEY DERIVATION -------- #
def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    return kdf.derive(password.encode())

# -------- ENCRYPT -------- #
def encrypt_data(data, key):
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aes.encrypt(nonce, json.dumps(data).encode(), None)
    return nonce, ciphertext

# -------- DECRYPT -------- #
def decrypt_data(nonce, ciphertext, key):
    aes = AESGCM(key)
    decrypted = aes.decrypt(nonce, ciphertext, None)
    return json.loads(decrypted.decode())

# -------- LOAD VAULT -------- #
def load_vault(password):
    if not os.path.exists(VAULT_FILE):
        return {"accounts": []}, os.urandom(16)

    with open(VAULT_FILE, "r") as f:
        vault = json.load(f)

    salt = base64.b64decode(vault["salt"])
    nonce = base64.b64decode(vault["nonce"])
    ciphertext = base64.b64decode(vault["ciphertext"])

    key = derive_key(password, salt)
    data = decrypt_data(nonce, ciphertext, key)

    return data, salt

# -------- SAVE VAULT -------- #
def save_vault(data, password, salt):
    key = derive_key(password, salt)
    nonce, ciphertext = encrypt_data(data, key)

    vault = {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }

    with open(VAULT_FILE, "w") as f:
        json.dump(vault, f, indent=4)

# -------- FEATURES -------- #
def add_entry(data):
    site = input("Site: ")
    username = input("Username: ")
    password = input("Password: ")
    notes = input("Notes: ")

    data["accounts"].append({
        "site": site,
        "username": username,
        "password": password,
        "notes": notes
    })

def view_entries(data):
    for acc in data["accounts"]:
        print(acc)

def search_entries(data):
    keyword = input("Search keyword: ")
    for acc in data["accounts"]:
        if keyword.lower() in acc["site"].lower():
            print(acc)

def delete_entry(data):
    site = input("Enter site to delete: ")
    data["accounts"] = [acc for acc in data["accounts"] if acc["site"] != site]

# -------- MAIN -------- #
def main():
    master_password = input("Enter master password: ")
    data, salt = load_vault(master_password)

    while True:
        print("\n1.Add 2.View 3.Search 4.Delete 5.Exit")
        choice = input("Choose: ")

        if choice == "1":
            add_entry(data)
        elif choice == "2":
            view_entries(data)
        elif choice == "3":
            search_entries(data)
        elif choice == "4":
            delete_entry(data)
        elif choice == "5":
            save_vault(data, master_password, salt)
            print("Vault saved securely.")
            break

if __name__ == "__main__":
    main()
