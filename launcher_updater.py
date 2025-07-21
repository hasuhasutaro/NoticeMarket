import os
import sys
import requests
import shutil
import tempfile
import time
import subprocess
from bs4 import BeautifulSoup

# GitHub最新リリースページ
LATEST_RELEASE_URL = "https://github.com/hasuhasutaro/NoticeMarket/releases/latest/download/"
# exeファイル名（GitHub上のアセット名と一致させること）
EXE_NAME = "market_app.exe"


def get_latest_version_and_url():
    # リリースページからバージョン取得
    resp = requests.get("https://github.com/hasuhasutaro/NoticeMarket/releases/latest")
    soup = BeautifulSoup(resp.text, "html.parser")
    ver_tag = soup.find("span", {"class": "css-truncate-target"})
    latest_version = ver_tag.text.strip() if ver_tag else None
    # exeダウンロードURLは直接組み立て
    exe_url = f"https://github.com/hasuhasutaro/NoticeMarket/releases/latest/download/{EXE_NAME}"
    return latest_version, exe_url


def is_newer_version(latest_version, current_version):
    def parse(v):
        return [int(x) for x in v.strip("v").split(".")]
    try:
        return parse(latest_version) > parse(current_version)
    except Exception:
        return False


def download_and_replace_exe(exe_url, target_exe):
    temp_dir = tempfile.gettempdir()
    temp_exe = os.path.join(temp_dir, EXE_NAME)
    print(f"Downloading new version: {exe_url}")
    with requests.get(exe_url, stream=True) as r:
        with open(temp_exe, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    # 置き換え
    shutil.copy2(temp_exe, target_exe)
    print("Update complete.")


def run_main_exe(target_exe):
    print("Starting main app...")
    subprocess.Popen([target_exe])
    sys.exit()


def main():
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(exe_dir, EXE_NAME)
    latest_version, exe_url = get_latest_version_and_url()
    need_download = False
    if not os.path.exists(exe_path):
        print("market_app.exe not found. Downloading latest version...")
        need_download = True
        current_version = "0.0.0"
    else:
        try:
            import subprocess
            result = subprocess.run([exe_path, "--version"], capture_output=True, text=True)
            current_version = result.stdout.strip()
        except Exception:
            current_version = "0.0.0"
        if latest_version and exe_url and is_newer_version(latest_version, current_version):
            print(f"Updating from {current_version} to {latest_version}")
            need_download = True
    if need_download and latest_version and exe_url:
        download_and_replace_exe(exe_url, exe_path)
    if not os.path.exists(exe_path):
        print("Error: market_app.exe not found after download.\nGitHubリリースに正しいexeがあるか確認してください。")
        sys.exit(1)
    run_main_exe(exe_path)

if __name__ == "__main__":
    main()
