from bs4 import BeautifulSoup
import requests

def get_price(artist, album):
    # buid URL
    artist_transformed = artist.replace(" ", "+")
    album_transformed = album.replace(" ", "+")
    url = f"https://www.discogs.com/search/?q={artist_transformed}+{album_transformed}&type=all&format_exact=Vinyl"

    # retrieve master_id
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # check if albums were found:
    if soup.find("div", {"id": "pjax_container"}):
        all_ids = []

        for element in soup.find_all('div'):
            if element.has_attr('data-master-id'):
                element_id = element.attrs["data-master-id"]
                all_ids.append(element_id)

        if len(all_ids) > 0:
            master_id = all_ids[0]

            # dynamically update the result URL
            link = f"https://www.discogs.com/sell/list?sort=price%2Casc&limit=25&master_id={master_id}&ev=mb&format=Vinyl&currency=EUR"
            response_3 = requests.get(link)
            soup = BeautifulSoup(response_3.content, "html.parser")

            #retrieve all listings
            listings = soup.find_all("tr", class_="shortcut_navigable")

            # retrieve all total prices
            items = []
            for listing in listings:
                if listing.find("span", class_="converted_price"):
                    price = listing.find("span", class_="converted_price")
                    price_stripped = float(price.text.strip('about').strip('total').strip(' ').replace('€', '').replace('$', ''))
                    items.append(price_stripped)

            if items == []:
                return ["no price found", "no price found"]

            #find_minimum price
            min_price = min(items)
            min_price_index = items.index(min_price)

            all_urls = []


            for listing in listings:
                if listing.find("span", class_="converted_price"):
                    tag = listing.find("a")
                    url = tag['href']
                    all_urls.append(url)

            url_min_price = f"https://www.discogs.com/{all_urls[min_price_index]}"


            return [url_min_price, min_price]

        return ["no price found","no price found"]

    # if no albums were found
    return ["no price found", "no price found"]
