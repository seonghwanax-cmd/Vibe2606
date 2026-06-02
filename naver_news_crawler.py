import requests
from bs4 import BeautifulSoup


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
    return response.text


def extract_news_titles(search_html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(search_html, "html.parser")

    # Naver 뉴스 검색 결과에서 기사 제목은 data-heatmap-target=".tit" 속성이 있는 링크 안에 있습니다.
    # 같은 URL이 여러 번 나타날 수 있으므로, URL별로 가장 긴 제목을 선택합니다.
    items = soup.select("a[data-heatmap-target='.tit']")
    news_by_url: dict[str, dict[str, str]] = {}

    for item in items:
        title = item.get_text(strip=True)
        href = item.get("href")
        if not title or not href:
            continue

        existing = news_by_url.get(href)
        if existing is None or len(title) > len(existing["title"]):
            news_by_url[href] = {"title": title, "url": href}

    return list(news_by_url.values())


def main() -> None:
    search_url = (
        "https://search.naver.com/search.naver?where=nexearch"
        "&sm=top_hty&fbm=0&ie=utf8&query=%EB%B0%98%EB%8F%84%EC%B2%B4&ackey=ud04xjkv"
    )

    print("Fetching Naver search results...")
    html = fetch_html(search_url)

    print("Extracting news article titles from links...")
    news_items = extract_news_titles(html)

    if not news_items:
        print("No news items found. The page structure may have changed.")
        return

    for index, item in enumerate(news_items, start=1):
        print(f"{index}. {item['title']}")
        print(f"   URL: {item['url']}")


if __name__ == "__main__":
    main()
