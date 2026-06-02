import requests
from bs4 import BeautifulSoup
from typing import Optional
from openpyxl import Workbook
import webbrowser
import csv
import json
import os
from datetime import datetime

BASE_URL = "https://finance.naver.com"
ENTRY_URL = "https://finance.naver.com/sise/entryJongmok.naver?type=KPI200"


def fetch_html(url: str, timeout: int = 10) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    response.encoding = "euc-kr"
    return response.text


def build_entry_url(page: int = 1) -> str:
    if page <= 1:
        return ENTRY_URL
    return f"{ENTRY_URL}&page={page}"


def parse_kpi200_entry_top(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.type_1")
    if table is None:
        raise ValueError("Could not find KPI200 entry table in the HTML.")

    items = []
    for tr in table.select("tr"):
        cells = tr.select("td")
        if len(cells) != 7:
            continue

        name = cells[0].get_text(strip=True)
        if not name:
            continue

        link_tag = cells[0].select_one("a[href]")
        item_url = BASE_URL + link_tag["href"] if link_tag else None

        items.append({
            "name": name,
            "current_price": cells[1].get_text(strip=True),
            "day_diff": cells[2].get_text(strip=True),
            "rate_diff": cells[3].get_text(strip=True),
            "volume": cells[4].get_text(strip=True),
            "transaction_value": cells[5].get_text(strip=True),
            "market_cap_100m": cells[6].get_text(strip=True),
            "detail_url": item_url,
        })

    return items


def get_total_pages_from_nav(html: str) -> int:
    """Parse the pagination nav and return the total number of pages.

    Falls back to 1 if pagination not found.
    """
    soup = BeautifulSoup(html, "html.parser")
    nav = soup.select_one("table.Nnavi")
    if not nav:
        return 1

    pages = []
    for a in nav.select("a[href]"):
        href = a.get("href", "")
        # look for page=NUMBER
        import re

        m = re.search(r"[?&]page=(\d+)", href)
        if m:
            try:
                pages.append(int(m.group(1)))
            except ValueError:
                continue

    return max(pages) if pages else 1


def fetch_all_pages(max_pages: int | None = None) -> list[dict[str, str]]:
    all_items: list[dict[str, str]] = []

    # Fetch first page to determine total pages
    print("Fetching KPI200 page 1 to determine total pages...")
    first_html = fetch_html(build_entry_url(1))
    total_pages = get_total_pages_from_nav(first_html)
    if max_pages is not None:
        total_pages = min(total_pages, max_pages)

    for page in range(1, total_pages + 1):
        print(f"Fetching KPI200 page {page}...")
        html = first_html if page == 1 else fetch_html(build_entry_url(page))
        page_items = parse_kpi200_entry_top(html)
        if not page_items:
            print(f"No items found on page {page}. Stopping pagination.")
            break
        all_items.extend(page_items)

    return all_items


def export_items_to_excel(items_to_save: list[dict[str, str]], filename: str | None = None) -> str:
    """Export items to an Excel file using openpyxl and return the saved path."""
    if filename is None:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"kpi200_entries_{now}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "KPI200"
    headers = ["rank", "name", "current_price", "day_diff", "rate_diff", "volume", "transaction_value", "market_cap_100m", "detail_url"]
    ws.append(headers)
    for i, it in enumerate(items_to_save, start=1):
        ws.append([i, it.get("name"), it.get("current_price"), it.get("day_diff"), it.get("rate_diff"), it.get("volume"), it.get("transaction_value"), it.get("market_cap_100m"), it.get("detail_url")])
    wb.save(filename)
    return os.path.abspath(filename)


def main() -> None:
    def print_grid(items: list[dict[str, str]], per_row: int = 10) -> None:
        # 그룹별로 컬럼 너비 계산 후 이름/현재가/등락률을 가로로 정렬해 출력합니다.
        for start in range(0, len(items), per_row):
            group = items[start : start + per_row]
            if not group:
                continue

            widths = []
            for it in group:
                nw = len(it["name"])
                pw = len(it["current_price"])
                rw = len(it["rate_diff"])
                widths.append(max(nw, pw, rw))

            # 이름 행
            # 순위 범위 헤더
            start_rank = start + 1
            end_rank = start + len(group)
            print(f"순위 {start_rank}~{end_rank}")

            name_line = "  ".join(
                it["name"].ljust(widths[i]) for i, it in enumerate(group)
            )
            # 현재가 행
            price_line = "  ".join(
                it["current_price"].rjust(widths[i]) for i, it in enumerate(group)
            )
            # 등락률 행
            rate_line = "  ".join(
                it["rate_diff"].rjust(widths[i]) for i, it in enumerate(group)
            )

            print(name_line)
            print(price_line)
            print(rate_line)
            print()

    items = fetch_all_pages(max_pages=20)

    if not items:
        print("No KPI200 entry items found. The page structure may have changed.")
        return

    print(f"Found {len(items)} KPI200 entry items. Displaying {min(20, (len(items) + 9) // 10)} pages (10 items per row):\n")
    print_grid(items, per_row=10)


def run_gui(max_pages: Optional[int] = None) -> None:
    try:
        from PyQt5.QtWidgets import (
            QApplication,
            QMainWindow,
            QTableWidget,
            QTableWidgetItem,
            QVBoxLayout,
            QWidget,
            QPushButton,
            QLabel,
            QHBoxLayout,
        )
    except Exception:
        print("PyQt5 is not available. Install PyQt5 to use the GUI.")
        return

    # Fetch data first (synchronous)
    items = fetch_all_pages(max_pages=max_pages)

    app = QApplication([])
    win = QMainWindow()
    win.setWindowTitle("KPI200 편입종목상위")
    central = QWidget()
    layout = QVBoxLayout(central)

    header_layout = QHBoxLayout()
    info_label = QLabel(f"총 항목: {len(items)}")
    refresh_btn = QPushButton("새로고침")
    export_csv_btn = QPushButton("CSV 저장")
    export_json_btn = QPushButton("JSON 저장")
    header_layout.addWidget(info_label)
    header_layout.addStretch()
    header_layout.addWidget(export_csv_btn)
    header_layout.addWidget(export_json_btn)
    header_layout.addWidget(refresh_btn)
    layout.addLayout(header_layout)

    table = QTableWidget()
    cols = [
        "순위",
        "종목명",
        "현재가",
        "전일비",
        "등락률",
        "거래량",
        "거래대금(백만)",
        "시가총액(억)",
        "URL",
    ]
    table.setColumnCount(len(cols))
    table.setHorizontalHeaderLabels(cols)
    table.setRowCount(len(items))

    for i, it in enumerate(items):
        table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
        table.setItem(i, 1, QTableWidgetItem(it.get("name", "")))
        table.setItem(i, 2, QTableWidgetItem(it.get("current_price", "")))
        table.setItem(i, 3, QTableWidgetItem(it.get("day_diff", "")))
        table.setItem(i, 4, QTableWidgetItem(it.get("rate_diff", "")))
        table.setItem(i, 5, QTableWidgetItem(it.get("volume", "")))
        table.setItem(i, 6, QTableWidgetItem(it.get("transaction_value", "")))
        table.setItem(i, 7, QTableWidgetItem(it.get("market_cap_100m", "")))
        table.setItem(i, 8, QTableWidgetItem(it.get("detail_url", "")))

    table.resizeColumnsToContents()
    layout.addWidget(table)

    def on_refresh():
        refresh_btn.setEnabled(False)
        info_label.setText("업데이트 중...")
        app.processEvents()
        new_items = fetch_all_pages(max_pages=max_pages)
        table.setRowCount(len(new_items))
        for i, it in enumerate(new_items):
            table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            table.setItem(i, 1, QTableWidgetItem(it.get("name", "")))
            table.setItem(i, 2, QTableWidgetItem(it.get("current_price", "")))
            table.setItem(i, 3, QTableWidgetItem(it.get("day_diff", "")))
            table.setItem(i, 4, QTableWidgetItem(it.get("rate_diff", "")))
            table.setItem(i, 5, QTableWidgetItem(it.get("volume", "")))
            table.setItem(i, 6, QTableWidgetItem(it.get("transaction_value", "")))
            table.setItem(i, 7, QTableWidgetItem(it.get("market_cap_100m", "")))
            table.setItem(i, 8, QTableWidgetItem(it.get("detail_url", "")))
        info_label.setText(f"총 항목: {len(new_items)}")
        table.resizeColumnsToContents()
        refresh_btn.setEnabled(True)

    def export_csv(items_to_save: list[dict[str, str]]):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"kpi200_entries_{now}.csv"
        with open(fname, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["rank", "name", "current_price", "day_diff", "rate_diff", "volume", "transaction_value", "market_cap_100m", "detail_url"])
            for i, it in enumerate(items_to_save, start=1):
                writer.writerow([i, it.get("name"), it.get("current_price"), it.get("day_diff"), it.get("rate_diff"), it.get("volume"), it.get("transaction_value"), it.get("market_cap_100m"), it.get("detail_url")])
        info_label.setText(f"CSV 저장됨: {os.path.abspath(fname)}")

    def export_json(items_to_save: list[dict[str, str]]):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"kpi200_entries_{now}.json"
        with open(fname, "w", encoding='utf-8') as f:
            json.dump(items_to_save, f, ensure_ascii=False, indent=2)
        info_label.setText(f"JSON 저장됨: {os.path.abspath(fname)}")

    export_csv_btn.clicked.connect(lambda: export_csv(items))
    export_json_btn.clicked.connect(lambda: export_json(items))
    
    export_excel_btn = QPushButton("Excel 저장")
    header_layout.insertWidget(2, export_excel_btn)
    export_excel_btn.clicked.connect(lambda: info_label.setText(f"Excel 저장됨: {export_items_to_excel(items)}"))

    # Open URL on double-click
    def on_cell_double_clicked(row, col):
        url_item = table.item(row, 8)
        if url_item:
            url = url_item.text()
            if url:
                try:
                    webbrowser.open(url)
                except Exception:
                    pass

    table.cellDoubleClicked.connect(on_cell_double_clicked)

    refresh_btn.clicked.connect(on_refresh)

    win.setCentralWidget(central)
    win.resize(1000, 600)
    win.show()
    app.exec_()


if __name__ == "__main__":
    import sys

    # 실행 인자: --gui 를 주면 GUI를 실행하고, 없으면 콘솔 출력을 실행합니다.
    if "--gui" in sys.argv or "-g" in sys.argv:
        run_gui()
    else:
        main()
