import os
import pandas as pd
from datetime import datetime
from utils import load_config, init_sheet, send_webhook
import logging

# 로깅 설정
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/weekly_reset.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    cfg = load_config()
    send_webhook("🧹 [Weekly Reset] 시트 백업 및 초기화 시작", cfg)

    spreadsheet = init_sheet(cfg)
    target_sheets = ["All News", "Filtered News"]
    backup_dir = os.path.join(os.getcwd(), "backups")
    os.makedirs(backup_dir, exist_ok=True)

    today = datetime.utcnow().strftime("%m-%d")

    for sheet_name in target_sheets:
        try:
            sheet = spreadsheet.worksheet(sheet_name)
            records = sheet.get_all_records()
            if not records:
                logging.warning(f"⚠️ '{sheet_name}' 시트에 백업할 데이터가 없습니다.")
                continue

            df = pd.DataFrame(records)
            filename = f"{sheet_name.replace(' ', '_')}_{today}.csv"
            backup_path = os.path.join(backup_dir, filename)

            df.to_csv(backup_path, index=False, encoding='utf-8-sig')
            logging.info(f"📁 '{sheet_name}' 시트 백업 완료: {backup_path}")

            sheet.clear()
            sheet.update([df.columns.tolist()])
            logging.info(f"🧹 '{sheet_name}' 시트 초기화 완료.")
        except Exception as e:
            logging.error(f"❌ '{sheet_name}' 처리 중 오류 발생: {e}")

    send_webhook("✅ [Weekly Reset] 모든 시트 백업 및 초기화 완료", cfg)

if __name__ == "__main__":
    main()
