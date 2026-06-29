"""Minimal Microsoft Graph client (app-only / client credentials).
Downloads the workbook and uploads the rendered PNG. No third-party deps.

Env vars required:
  TENANT_ID, CLIENT_ID, CLIENT_SECRET   - the app registration
  DRIVE_ID                              - the OEB EXCO 'Documents' drive id
"""
import os, json, urllib.request, urllib.parse, sys

TENANT = os.environ["TENANT_ID"]
CLIENT = os.environ["CLIENT_ID"]
SECRET = os.environ["CLIENT_SECRET"]
DRIVE  = os.environ["DRIVE_ID"]
GRAPH  = "https://graph.microsoft.com/v1.0"

def get_token():
    data = urllib.parse.urlencode({
        "client_id": CLIENT,
        "client_secret": SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }).encode()
    url = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token"
    with urllib.request.urlopen(urllib.request.Request(url, data=data)) as r:
        return json.load(r)["access_token"]

def download(drive_path, dest, token=None):
    token = token or get_token()
    p = urllib.parse.quote(drive_path)
    url = f"{GRAPH}/drives/{DRIVE}/root:/{p}:/content"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
        f.write(r.read())
    print(f"downloaded {drive_path} -> {dest} ({os.path.getsize(dest)} bytes)")

def upload(src, drive_path, token=None):
    token = token or get_token()
    p = urllib.parse.quote(drive_path)
    url = f"{GRAPH}/drives/{DRIVE}/root:/{p}:/content"
    body = open(src, "rb").read()
    req = urllib.request.Request(url, data=body, method="PUT", headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "image/png",
    })
    with urllib.request.urlopen(req) as r:
        info = json.load(r)
    print(f"uploaded {src} -> {drive_path} (id {info.get('id','?')})")

if __name__ == "__main__":
    # smoke test: just acquire a token
    t = get_token()
    print("token acquired, length", len(t))
