import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import connect

parser = argparse.ArgumentParser()
parser.add_argument("--page_num_max", help = "Enter the number of pages to parse", type = int)
parser.add_argument("--dbName", help = "Enter the name of Database", type = str)
args = parser.parse_args()

oyo_url = "https://www.oyorooms.com/hotels-in-madiwala-bangalore/?page="
hdrs = {'User-Agent': 'Mozilla / 5.0 (X11 Linux x86_64) AppleWebKit / 537.36 (KHTML, like Gecko) Chrome / 52.0.2743.116 Safari / 537.36'}
pageNumMax = args.page_num_max
scraped_info_list = []
connect.connect(args.dbName)

for page_num in range(1, pageNumMax + 1):
    url = oyo_url + str(page_num)
    print("GET Request for: ", url)
    req = requests.get(url, headers = hdrs)
    # print(req)
    content = req.content
    # print(content)

    soup = BeautifulSoup(content, 'html.parser')

    all_hotels = soup.find_all('div', {'class': 'hotelCardListing'})
    # print(all_hotels)

    for hotel in all_hotels:
        # print("For hotels...")
        hotel_dict = {}
        hotel_dict["name"] = hotel.find("h3", {'class': 'listingHotelDescription__hotelName'}).text
        hotel_dict["address"] = hotel.find("span", {'itemprop': 'streetAddress'}).text
        hotel_dict["price"] = hotel.find("span", {'class': 'listingPrice__finalPrice'}).text

        try:
            hotel_dict["rating"] = hotel.find("span", {'class': 'hotelRating__ratingSummary'}).text
        except AttributeError:
            hotel_dict["rating"] = None

        parent_ammenities_element = hotel.find('div', {'class': 'amenityWrapper'})

        amenitiesList = []
        for amenity in parent_ammenities_element.find_all('div', {'class': 'amenityWrapper__amenity'}):
            amenitiesList.append(amenity.find('span', {'class': 'd-body-sm'}).text.strip())

        hotel_dict['amenties'] = ', '.join(amenitiesList[:-1])

        scraped_info_list.append(hotel_dict)
        # print(hotel_dict['name'], hotel_dict['address'], hotel_dict['price'], hotel_dict['rating'], hotel_dict['amenties'])
        connect.insert_into_table(args.dbName, tuple(hotel_dict.values()))

dataframe = pd.DataFrame(scraped_info_list)
print("Creating csv file...")
dataframe.to_csv("My Captain\Python\WebScrapper\Oyo.csv")
connect.get_hotel_info(args.dbName)