from bs4 import BeautifulSoup
from selenium import webdriver
import sys, os, inspect
import time
import datetime

#import the database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from database_setup import Base, Hotel, Price

engine = create_engine('sqlite:///db.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

hotels = ["mandalaybay",
          "delanolasvegas",
          "luxor",
          "excalibur",
          "newyorknewyork",
          "montecarlo",
          "aria",
          "vdara",
          "bellagio",
          "mirage",
          "circuscircus",
          "mgmgrand",
          "signaturemgmgrand"]


def main():
    my_data = []
    for hotel in hotels:
        add_hotel_to_db(hotel)
        request = get_website(hotel)
        print(hotel)
        days, good = parse_data(request)
        if not good:
            continue
            print("Something bad happened skipping hotel")
        my_data = get_prices(days, my_data, hotel)
    my_data.sort(key=lambda x: x["price"])
    for price in my_data:
        print(price["date"] + ": $" + str(price["price"]) + " at " + price["hotel"])


def add_hotel_to_db(hotel):
    """
    Add a hotel to our database
    :param hotel: The hotel we want to add
    :return: nothing
    """
    if session.query(Hotel).filter_by(name=hotel).count():
        return
    new_hotel = Hotel(name = hotel)
    session.add(new_hotel)
    session.commit()


def add_price_to_db(date, rate, hotel):
    """
    Add a price for a specific hotel for a specific date
    :param date: the date for the price
    :param rate: the price for a specific date
    :param hotel: the hotel the price is from
    :return: nothing
    """
    hotel_obj = session.query(Hotel).filter_by(name=hotel).one()
    date_obj = datetime.datetime.strptime(date, "%m/%d/%Y").date()
    new_price = Price(hotel = hotel_obj, date = date_obj, price = rate)
    session.add(new_price)
    session.commit()


def parse_data(request):
    """
    Parse mgm's booking page to get all prices for a speciifc hotel
    :param request: the html generated by the page
    :return: a list of all days and there prices.
    """
    soup = BeautifulSoup(request.page_source, "html.parser")
    results = soup.find("div", {"class": "calendar__monthsWrapper"})
    #sometime the page will not load for what ever reason, if this happens we want to try again
    try:
        days = results.findAll("a", {"class": "dateWrapper"})
    except:
        return None, False
    return days, True


def get_prices(days, my_data, hotel):
    """
    For each day find out the price
    :param days: A list of all days and prices
    :param my_data: our list to save the data
    :param hotel: the hotel we are looking at
    :return: our data with the price for each day
    """
    for day in days:
        if day.attrs['data-status'] == 'past-date':
            continue
        data_date = day.attrs["data-date"]
        data_month = str(data_date.split('/')[0])
        data_year = str(data_date.split('/')[2])
        if not data_date:
            continue
        rate = day.find("span", {"class": "dateWrapper__button--rate"})
        if not rate:
            continue
        try:
            rate = int(rate.text.split("$")[1])
        except:
            rate = 9999
        date = data_date
        my_data.append({"date": date, "price": rate, "hotel": hotel})
        add_price_to_db(date, rate, hotel)
    return my_data


def get_website(hotel):
    """
    Load a website in Chrome and return the html (after java script has loaded
    :param url: the url to load
    :return: the urls html
    """
    url = format_url(hotel)
    #Because the website use Java script to inject the prices we have to
    #load the website like a normal user. This will open chrome in the background
    #wait for the page to load and capture the html once the load is complete
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(1)
    return driver


def format_url(hotel):
    """
    take a hotel names and create a url to parse
    :param hotel: The hotel name, with out spaces
    :return: a URL that parsable
    """
    return "https://www." + hotel + ".com/en/booking/room-booking.html"


if __name__ == "__main__":
    main()