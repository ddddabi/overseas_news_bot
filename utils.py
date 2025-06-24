import os
import yaml
import hashlib
import gspread
import requests
import pytz
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dateutil import parser as dtparser

KST = pytz.timezone("Asia/Seoul")

def to_kst(dt):
    """UTC 또는 naive datetime을 한국 시간으로 변환"""
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(KST)

def load_config(path="config.yaml"):
    """config.yaml 불러오기"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, path)
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def init_sheet(cfg):
    """구글 시트 인증 및 열기"""
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    # 절대경로로 credentials 경로 설정
    base_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(base_dir, cfg['google']['credentials_path'])

    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)
    return client.open(cfg['google']['spreadsheet_name'])

def get_worksheet_by_title(spreadsheet, title):
    """시트가 있으면 가져오고 없으면 생성"""
    try:
        return spreadsheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows="1000", cols="10")

def hash_entry(title, link):
    """뉴스 제목과 링크 기반 해시 생성"""
    return hashlib.md5((title + link).encode()).hexdigest()

def send_webhook(message, cfg):
    """웹훅으로 알림 메시지 전송"""
    url = cfg.get("webhook", {}).get("url")
    if not url:
        return
    try:
        now = to_kst(datetime.utcnow()).strftime("%m-%d %H:%M")
        full_message = f"[{now}] {message}"
        payload = {"text": full_message}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"⚠️ 웹훅 전송 실패: {e}")

def append_rows_in_batches(sheet, data, batch_size=50):
    """데이터를 일정 배치 크기로 나눠서 시트에 추가"""
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        try:
            sheet.append_rows(batch)
        except Exception as e:
            print(f"❌ append 실패: {e}")
