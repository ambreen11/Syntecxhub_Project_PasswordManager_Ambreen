# Syntecxhub_Project_PasswordManager_Ambreen


# 🔐 Secure Password Manager (Local - AES Encrypted)

## 📌 Overview

This project is a local password manager built using Python that securely stores credentials using strong encryption (AES-256).

It ensures confidentiality and integrity of stored data using:

* AES-GCM encryption
* PBKDF2 key derivation
* Secure random salt & nonce

---

## 🚀 Features

* Master password protection
* Add new credentials
* Retrieve stored credentials
* Search entries
* Delete entries
* Encrypted local storage (JSON format)

---

## 🔐 Security Design

### Key Derivation

* PBKDF2 with SHA-256
* 100,000 iterations
* Random salt

### Encryption

* AES-256 in GCM mode
* Provides authentication + confidentiality

### Storage Format

Encrypted JSON file:

```
{
  "salt": "...",
  "nonce": "...",
  "ciphertext": "..."
}
```

---

## 🛠️ Installation

```bash
pip install cryptography
```

---

## ▶️ Usage

```bash
python main.py
```

---

## ⚠️ Security Notes

* Master password is never stored
* Strong encryption prevents data leakage
* Changing master password invalidates old vault

---

## 📈 Future Improvements

* GUI version
* Argon2 key derivation
* Auto-lock system
* Clipboard protection
* Password strength meter

---

## 👨‍💻 Author

Ambreen Shaikh
