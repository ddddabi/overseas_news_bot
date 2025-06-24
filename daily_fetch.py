import feedparser
import pandas as pd
from datetime import datetime, timedelta
import argparse
from utils import (
    load_config,
    init_sheet,
    hash_entry,
    get_worksheet_by_title,
    send_webhook,
    append_rows_in_batches,
    to_kst
)
from googletrans import Translator
import requests
import logging
import os
from dateutil import parser as dtparser

# 로깅 설정
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/daily_fetch.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="단일 기사 날짜 (예: 05-12)")
    parser.add_argument("--from_date", type=str, help="시작 날짜 (예: 05-10)")
    parser.add_argument("--to_date", type=str, help="종료 날짜 (예: 05-13)")
    return parser.parse_args()

def get_filter_dates(args):
    if args.date:
        return {args.date}
    elif args.from_date and args.to_date:
        from_dt = datetime.strptime(args.from_date, "%m-%d")
        to_dt = datetime.strptime(args.to_date, "%m-%d")
        return {
            (from_dt + timedelta(days=i)).strftime("%m-%d")
            for i in range((to_dt - from_dt).days + 1)
        }
    else:
        return {(to_kst(datetime.utcnow()) - timedelta(days=1)).strftime("%m-%d")}

def safe_parse(url, timeout=10):
    try:
        logging.info(f"⏳ 요청 중: {url}")
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return feedparser.parse(resp.text)
    except Exception as e:
        logging.warning(f"❌ 실패: {url}\n   이유: {e}")
        return None

def main():
    args = parse_args()
    cfg = load_config()
    send_webhook("✅ [Daily Fetch] 뉴스 수집 시작", cfg)

    feeds = cfg["feeds"]["urls"]
    keywords = [kw.lower() for kw in cfg["keywords"]]
    translator = Translator()
    spreadsheet = init_sheet(cfg)

    sheet_all = get_worksheet_by_title(spreadsheet, "All News")
    sheet_filtered = get_worksheet_by_title(spreadsheet, "Filtered News")

    existing_filtered = sheet_filtered.get_all_records()
    existing_hashes = set(row.get("해시") for row in existing_filtered if row.get("해시"))

    search_time = to_kst(datetime.utcnow()).strftime('%m-%d %H:%M')
    filter_dates = get_filter_dates(args)

    all_rows = []
    filtered_rows = []

    for url in feeds:
        feed = safe_parse(url)
        if not feed:
            continue

        for entry in feed.entries:
            title = entry.title
            link = entry.link
            entry_hash = hash_entry(title, link)

            published = entry.get("published", "") or entry.get("updated", "")
            try:
                dt = dtparser.parse(published)
                kst_time = to_kst(dt)
                article_date = kst_time.strftime("%m-%d")
            except Exception as e:
                article_date = ""
                logging.warning(f"⚠️ 날짜 파싱 실패: {published} → {e}")

            try:
                direct = translator.translate(title, src='en', dest='ko').text
                natural = direct  # 자연스러운 의역 대신 직역을 그대로 사용
            except Exception as e:
                logging.warning(f"⚠️ 번역 실패: {title}, 에러: {e}")
                continue

            row = [search_time, article_date, title, direct, natural, link, entry_hash]
            all_rows.append(row)

            if article_date in filter_dates:
                if any(kw in title.lower() for kw in keywords):
                    if entry_hash not in existing_hashes:
                        filtered_rows.append(row)

    columns = ["검색일시", "기사일자", "제목(원문)", "제목(직역)", "제목(의역)", "링크", "해시"]

    if all_rows:
        df_all = pd.DataFrame(all_rows, columns=columns)
        append_rows_in_batches(sheet_all, df_all.values.tolist())
        logging.info(f"📚 전체 뉴스 {len(df_all)}건 저장 (All News)")
    else:
        logging.warning("ℹ️ 전체 뉴스 없음")

    num_filtered = len(filtered_rows)
    if num_filtered > 0:
        df_filtered = pd.DataFrame(filtered_rows, columns=columns)
        append_rows_in_batches(sheet_filtered, df_filtered.values.tolist())
        logging.info(f"✅ 필터링된 뉴스 {num_filtered}건 저장 (Filtered News)")
    else:
        logging.warning("⚠️ 필터링된 뉴스 없음")

    send_webhook(f"✅ [Daily Fetch] 전체 {len(all_rows)}건 중 필터링된 {num_filtered}건 저장 완료", cfg)

if __name__ == "__main__":
    main()
