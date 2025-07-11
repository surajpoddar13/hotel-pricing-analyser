from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import date, timedelta

# Set today's and tomorrow's dates
today = date.today()
tomorrow = today + timedelta(days=1)
checkin = today.strftime("%Y-%m-%d")
checkout = tomorrow.strftime("%Y-%m-%d")

def scrape_booking(page):
    url = f"https://www.booking.com/searchresults.en-gb.html?ss=Mumbai&ssne=Mumbai&ssne_untouched=Mumbai&efdco=1&label=en-in-booking-desktop-CmH43mrsjzqEEFQPgVycoAS652796016141%3Apl%3Ata%3Ap1%3Ap2%3Aac%3Aap%3Aneg%3Afi%3Atikwd-65526620%3Alp9303279%3Ali%3Adec%3Adm&aid=2311236&lang=en-gb&sb=1&src_elem=sb&src=index&dest_id=-2092174&dest_type=city&checkin={checkin}&checkout={checkout}&group_adults=2&no_rooms=1&group_children=0"

    page.goto(url)
    page.wait_for_timeout(15000)
    hotels = page.locator("[data-testid='property-card']")
    data = []

    for i in range(min(hotels.count(),30)):
        hotel = hotels.nth(i)
        name = hotel.locator("[data-testid='title']").inner_text()
        try:
            price = hotel.locator("[data-testid='price-and-discounted-price']").first.inner_text()
        except:
            price = "N/A"
        data.append({"Hotel": name.strip(), "Price": price.strip(), "OTA": "Booking.com"})
    return data

def scrape_makemytrip(page):
    url = f"https://www.makemytrip.com/hotels/hotel-listing/?checkin={today.strftime('%m%d%Y')}&checkout={tomorrow.strftime('%m%d%Y')}&locusId=CTBOM&locusType=city&city=CTBOM&country=IN&searchText=Taj+Mahal+Hotel+Mumbai&roomStayQualifier=2e0e"
    page.goto(url)
    page.wait_for_timeout(17000)
    
    data = []
    hotels = page.locator("div.makeFlex.column.flexOne.appendRight20")  

    for i in range(min(hotels.count(), 2)):
        try:
            name = hotels.nth(i).locator("span.wordBreak.appendRight10").inner_text()
            price = hotels.nth(i).locator("p.priceText").inner_text()
            data.append({"Hotel": name.strip(), "Price": price.strip(), "OTA": "MakeMyTrip"})
        except:
            continue
    return data

def scrape_agoda(page):
    url = f"https://www.agoda.com/search?city=17072&checkIn={checkin}&checkOut={checkout}&rooms=1&adults=2&children=0&search=Taj+Mahal+Hotel+Mumbai"
    page.goto(url)
    page.wait_for_timeout(10000)
    data = []
    hotels = page.locator("h3[data-selenium='hotel-name']")

    for i in range(min(hotels.count(), 2)):
        try:
            name = hotels.nth(i).locator("h3").inner_text()
            price = hotels.nth(i).locator("span[class*='bhLehO']").inner_text()
            data.append({"Hotel": name.strip(), "Price": price.strip(), "OTA": "Agoda"})
        except:
            continue
    return data

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        all_data = []
        print("Scraping Booking.com...")
        all_data += scrape_booking(page)
        print("Scraping MakeMyTrip...")
        all_data += scrape_makemytrip(page)
        print("Scraping Agoda...")
        all_data += scrape_agoda(page)

        browser.close()

        df = pd.DataFrame(all_data)
        df.to_csv("MumbaiHotelPrices.csv", index=False)
        print("✅ Data Saved")

if __name__ == "__main__":
    main()