import asyncio
from urllib.parse import urlencode
from httpx import AsyncClient
from parsel import Selector

async def search_page(
    query,
    session: AsyncClient,
    checkin: str = "",
    checkout: str = "",
    number_of_rooms = 1,
    offset: int = 0
    ):
    checkin_year, checkin_month, checkin_day = checkin.split("-") if checkin else "","",""
    checkout_year, checkout_month, checkout_day = checkout.split("-") if checkout else "","",""
    
    url = "https://www.booking.com/searchresults.html"
    url += "?" + urlencode(
        {
            "ss": query,
            "checkin_year": checkin_year,
            "checkin_month": checkin_month,
            "checkin_monthday": checkin_day,
            "checkout_year": checkout_year,
            "checkout_month": checkout_month,
            "checkout_monthday": checkout_day,
            "no_rooms": number_of_rooms,
            "offset": offset,
        }
    )
    return await session.get(url, follow_redirects=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
}
def parse_search_total_results(html: str):
    """parse total number of results from search page HTML"""
    sel = Selector(text=html)
    # parse total amount of pages from heading1 text:
    # e.g. "London: 1,232 properties found"
    total_results = int(sel.css("h1").re("([\d,]+) properties found")[0].replace(",", ""))
    return total_results

def parse_search_page(html: str):
    """parse hotel preview data from search page HTML"""
    sel = Selector(text=html)

    hotel_previews = {}
    for hotel_box in sel.xpath('//div[@data-testid="property-card"]'):
        url = hotel_box.xpath('.//h3/a[@data-testid="title-link"]/@href').get("").split("?")[0]
        hotel_previews[url] = {
            "name": hotel_box.xpath('.//h3/a[@data-testid="title-link"]/div/text()').get(""),
            "location": hotel_box.xpath('.//span[@data-testid="address"]/text()').get(""),
            "score": hotel_box.xpath('.//div[@data-testid="review-score"]/div/text()').get(""),
            "review_count": hotel_box.xpath('.//div[@data-testid="review-score"]/div[2]/div[2]/text()').get(""),
            "stars": len(hotel_box.xpath('.//div[@data-testid="rating-stars"]/span').getall()),
            "image": hotel_box.xpath('.//img[@data-testid="image"]/@src').get(),
        }
    return hotel_previews


async def scrape_search(
    query,
    session: AsyncClient,
    checkin: str = "",
    checkout: str = "",
    number_of_rooms=1,
):
    """scrape all hotel previews from a given search query"""
    first_page = await search_page(
        query=query, session=session, checkin=checkin, checkout=checkout, number_of_rooms=number_of_rooms
    )
    total_results = parse_search_total_results(first_page.text)
    other_pages = await asyncio.gather(
        *[
            search_page(
                query=query,
                session=session,
                checkin=checkin,
                checkout=checkout,
                number_of_rooms=number_of_rooms,
                offset=offset,
            )
            for offset in range(25, total_results, 25)
        ]
    )
    hotel_previews = {}
    for response in [first_page, *other_pages]:
        hotel_previews.update(parse_search_page(response.text))
    return hotel_previews

import json


async def run():
    async with AsyncClient(headers=HEADERS) as session:
        results = await scrape_search("London", session)
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(run())


# async def run():
#     async with AsyncClient(headers=HEADERS) as session:
#         await search_page("London", session)

# if __name__ == "__main__":
#     asyncio.run(run())
    
