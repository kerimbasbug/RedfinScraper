# Redfin Property Scraper

This project is a Python script that scrapes property listings from Redfin for a specified county in New Jersey, USA. The script allows you to filter properties by price range and collect property data such as price, location, and type. The collected data can be merged into a single CSV file for further analysis.

## Features

- Scrapes property listings that are sold or currently on sale from Redfin using web scraping techniques.
- Filters properties based on minimum and maximum price ranges.
- Handles pagination and rate limits.
- Automatically opens URLs in Chrome for downloading the data.
- Allows the merging of multiple CSV files into a single file for a given county.

## Requirements

- Python 3.x
- `requests` library for making HTTP requests.
- `BeautifulSoup` from `bs4` for parsing HTML.
- `pandas` for handling CSV data.
- `webbrowser` for opening URLs in Chrome.

## Notes
The script requires you to manually set the download path in your Chrome settings. When the script opens URLs in Chrome for downloading CSV files. You need to configure Chrome to automatically download files to the correct directory for the script to work properly. This needs to be done under Chrome’s settings (Settings > Downloads > Location).
