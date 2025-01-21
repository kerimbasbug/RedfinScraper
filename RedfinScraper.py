import os
import time
import pandas as pd
import requests
import webbrowser
from bs4 import BeautifulSoup
import random

class RedfinScraper:
    """
    A class to scrape property data from Redfin based on price range and county.
    
    Attributes:
        county_name (str): The county to scrape data for (default is 'Burlington').
        min_price (int): The minimum price for property listings (default is 0).
        max_price (int): The maximum price for property listings (default is 300000).
        increment (int): The price increment for each request (default is 10000).
        max_price_increment (int): The maximum allowed increment (default is 50000).
        user_agents (list): A list of user agents for the scraper.
        headers (dict): The headers to be used for HTTP requests.
        county_dict (dict): A dictionary mapping county names to Redfin county IDs.
    """

    def __init__(self, county_name='Burlington', min_price=0, max_price=300000, increment=10000, max_price_increment=50000, sold=False):
        """
        Initializes the RedfinScraper instance with the given parameters.

        Args:
            county_name (str): The county name to scrape data for (default is 'Burlington').
            min_price (int): The minimum price to start scraping (default is 0).
            max_price (int): The maximum price to stop scraping (default is 300000).
            increment (int): The price increment for each page request (default is 10000).
            max_price_increment (int): The maximum value for increment (default is 50000).
            sold (bool): Whether to include sold properties or currently on sale (default is False).
        """
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        self.headers = {'User-Agent': random.choice(self.user_agents)}
        self.county_dict = {
            'Burlington': 1893,
            'Camden': 1894,
            'Essex': 1897,
            'Bergen': 1892,
            'Hudson': 1899,
            'Union': 1910,
            'Sussex': 1909,
            'Passaic': 1906,
            'Morris': 1904,
            'Somerset': 1908,
            'Middlesex': 1902,
            'Mercer': 1901,
            'Monmouth': 1903
        }
        self.county_name = county_name
        self.min_price = min_price
        self.max_price = max_price
        self.increment = increment
        self.max_price_increment = max_price_increment
        self.sold = sold

    def fetch_page(self, url):
        """
        Fetches the page content from the specified URL.

        Args:
            url (str): The URL to fetch.

        Returns:
            response (requests.models.Response): The response object containing the server's response.
        """
        response = requests.get(url, headers=self.headers)
        if response.status_code == 429:
            print("Rate limit exceeded, retrying...")
            time.sleep(60)  # Wait for 1 minute
            return self.fetch_page(url)  # Retry the request
        return response

    def get_data(self):
        """
        Scrapes property data from Redfin for a given county and price range.

        Adjusts the price range dynamically based on the number of listings returned per request. Redfin allows a maximum of 350 listings per request.

        Returns:
            lt_350 (list): A list of URLs that returned fewer than 350 listings.
        """
        base_url = "https://www.redfin.com/stingray/api/gis-csv"
        al = 3  # Unknown
        market = "newjersey"  # State
        county_id = self.county_dict[self.county_name]  # County Id
        region_type = 5  # Search for county
        uipt = "1,5"  # Property type, House or Land 
        sold_within_days = 1825  # Past Sale in last 5 years
        lt_350 = []

        while self.min_price < self.max_price:
            if self.sold:
                url = f"https://www.redfin.com/county/{county_id}/NJ/Sussex-County/filter/property-type=house+land,min-price={self.min_price},max-price={self.min_price + self.increment},include=sold-5yr"
            else:
                url = f"https://www.redfin.com/county/{county_id}/NJ/Sussex-County/filter/property-type=house+land,min-price={self.min_price},max-price={self.min_price + self.increment}"
            
            response = self.fetch_page(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                span_elements = soup.find_all('div', class_='descriptionSummary font-body-small-bold reversePosition')
                n_listings = int(span_elements[0].text.split('of ')[1].split(" ")[0].replace(',', ''))
                print(f"Listings for {self.min_price} $ - {self.min_price + self.increment} $: {n_listings}")

                if n_listings < 350:  # Redfin only allows to download 350 listings per request
                    lt_350.append(url)
                    if self.sold:
                        url = f"{base_url}?al={al}&market={market}&region_id={county_id}&region_type={region_type}&uipt={uipt}&min_price={self.min_price}&max_price={self.min_price + self.increment}&sold_within_days={sold_within_days}"
                    else:
                        url = f"{base_url}?al={al}&market={market}&region_id={county_id}&region_type={region_type}&uipt={uipt}&min_price={self.min_price}&max_price={self.min_price + self.increment}"

                    webbrowser.get("chrome").open(url)
                    
                    self.min_price += self.increment
                    self.increment = min(self.increment * 2, self.max_price_increment)
                else:
                    self.increment = max(self.increment // 2, 1)
                    if self.increment == 1:
                        webbrowser.get("chrome").open(url)
                        self.min_price += self.increment
            else:
                print(f"Failed to retrieve the page, status code: {response.status_code}")      

        return lt_350

    def create_directories(self):
        """
        Creates the necessary directories for storing the scraped data.

        Checks if the 'Data' and county-specific directories exist, and creates them if they don't.
        Prompts the user to manually select the downloaded file path in Chrome.
        """
        if not os.path.exists('Data'):
            os.mkdir('Data')
            if not os.path.exists(f'Data/{self.county_name}/'):
                os.mkdir(f'Data/{self.county_name}/')
                print(f'A new directory created {os.getcwd()}/Data/{self.county_name}/')
                print(f'Please manually select the downloaded file path to {os.getcwd()}/Data/{self.county_name}/ in Chrome under the settings.')
                input('Press Enter to continue...')
            else:
                print(f'Please manually select the downloaded file path to {os.getcwd()}/Data/{self.county_name}/ in Chrome under the settings.')
                input('Press Enter to continue...')
        else:
            if not os.path.exists(f'Data/{self.county_name}/'):
                os.mkdir(f'Data/{self.county_name}/')
                print(f'A new directory created {os.getcwd()}/Data/{self.county_name}/')
                print(f'Please manually select the downloaded file path to {os.getcwd()}/Data/{self.county_name}/ in Chrome under the settings.')
                input('Press Enter to continue...')
            else:
                print(f'Please manually select the downloaded file path to {os.getcwd()}/Data/{self.county_name}/ in Chrome under the settings.')
                input('Press Enter to continue...')

    def merge_files(self, merge_files=True):
        """
        Merges the downloaded CSV files into one.

        This method reads all the CSV files in the county's directory, removes duplicates, and saves them into a single CSV file.

        Args:
            merge_files (bool): Whether to merge files into a single CSV (default is True).
        """
        if merge_files:
            time.sleep(5)
            directory = os.getcwd() + f'/Data/{self.county_name}/'
            csv_files = [directory + f for f in os.listdir(directory) if f.endswith('.csv')]
            merged_df = pd.concat([pd.read_csv(file).iloc[1:] for file in csv_files], ignore_index=True)
            merged_df = merged_df.drop_duplicates()
            merged_df.reset_index(drop=True)
            merged_df.to_csv(directory + f"/{self.county_name}.csv", index=False)
            print("Files merged and saved.")
    
    def start_scraping(self):
        """
        Starts the scraping process for the specified county and price range.

        This method initializes the scraping, handles the creation of directories, and calls the merging method after scraping.
        """
        print(f'Starting to scrape for {self.county_name} County. Price Range: {self.min_price} $ - {self.max_price} $')
        _ = self.get_data()

        self.merge_files()
        print("Completed.")

if __name__ == "__main__":
    scraper = RedfinScraper(county_name='Sussex', min_price=0, max_price=10000, sold=False)
    scraper.create_directories()
    scraper.start_scraping()
