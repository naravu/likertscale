# likertscale Thooya's Project

# Baby Care Beliefs & Behaviours Survey App

This document explains how to set up and run the Streamlit app that collects survey responses and stores them in Google Sheets.

---

## 1. Prerequisites
- Python 3.9+ installed
- A Google Cloud project with a **Service Account** created
- A Google Sheet created in your Google Drive
- Streamlit Cloud account (for deployment)

---

## 2. Service Account Setup
1. In Google Cloud Console, create a **Service Account**.
2. Generate a **JSON key** for the service account.
3. Copy the JSON key details into Streamlit Secrets (see below).
4. Share your Google Sheet with the **service account email** (e.g. `likertscale@gen-lang-client-0838395604.iam.gserviceaccount.com`) and give **Editor** access.

---

## 3. Streamlit Secrets Configuration
Paste the service account JSON into **Streamlit Cloud → Settings → Secrets** as TOML:

```toml
[service_account]
type = "service_account"
project_id = "gen-lang-client-0838395604"
private_key_id = "dc61cc573a2cf789b12d958f3b097bcdbe33b1de"
private_key = """-----BEGIN PRIVATE KEY-----
... full private key with line breaks ...
-----END PRIVATE KEY-----"""
client_email = "likertscale@gen-lang-client-0838395604.iam.gserviceaccount.com"
client_id = "113897166335540834049"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/likertscale%40gen-lang-client-0838395604.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
