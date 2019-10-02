# Scraping hertz (July 2019 - site changed in the meantime)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import re
import ast

# Auxiliary functions
def get_indicatiors(title, details, price):
	# For title
	title_list = re.split('[(|)]', title)
	car_class = title_list[0]
	car_gibberish = title_list[1]
	title_list[2] = title_list[2].replace(' Sau similar', '')
	car_name = title_list[2]
	# For description
	details_list = re.split(', ', details)
	car_type_1 = details_list[0]
	car_type_2 = details_list[1]
	car_type_3 = details_list[2]
	car_ac = details_list[3]
	# For price
	price = price.replace('€', '')
	price = price.replace(' ', '').strip()
	print(price)
	print(car_class, '/', car_gibberish, '/', car_name, '/', car_type_1, '/', car_type_2, '/', car_type_3, '/', car_ac, '/', price)
	price = float(price)

def generate_dates():
	#Dates
	now = datetime.now()
	y = now.year
	m = now.month
	to_end_year = list(range(m+1,13))
	years = {y:to_end_year}
	if len(to_end_year) < 6:
		next_year = 6 - len(to_end_year)
		next_year = list(range(1,next_year+1))
		years[y+1] = next_year
	return years

# Opening the desired site
driver = webdriver.Chrome()
url = "https://www.hertz.ro/ro"
driver.get(url)

# Get all cities as a list of strings
cities = driver.find_elements_by_xpath("//select[@name ='outCity']/option")
cities = [city.text for city in cities][1:]

# For every city, selecting available locations;
#   dictionary 'location' has key = city, value = available shops
cities_dropdown = driver.find_element_by_xpath("//select[@name ='outCity']")
shops_dropdown = driver.find_element_by_xpath("//select[@name ='outShop']")
locations = dict()
for city in cities:
    cities_dropdown.send_keys(city)
    shops = shops_dropdown.find_elements_by_xpath(".//option")
    shops = [x.text for x in shops][1:]
    locations[city] = shops
    time.sleep(1) # slow down usain

years = generate_dates()

for city,locations in locations.items():
	element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//select[@name ='outCity']")))
	for location in locations:
		for year in years:
			for month in years[year]:
				for day in [1,15]:
					startdate = '/'.join([str(day),str(month),str(year)])
					print(startdate,day,month,year)
					cities_dropdown = driver.find_element_by_xpath("//select[@name ='outCity']")
					shops_dropdown = driver.find_element_by_xpath("//select[@name ='outShop']")
					cities_dropdown.send_keys(city)
					shops_dropdown.send_keys(location)
					outdate = driver.find_element_by_name('outDate')
					script = "arguments[0].value = '{startdate}'".format(startdate=startdate)
					print(script)
					driver.execute_script(script, outdate)
					days = driver.find_element_by_name("ReservationDays")
					days.send_keys("1 Zi")
					reserve_btn = driver.find_element_by_id("BtnReserveNew_td2")
					reserve_btn.click()
					element2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "divShowAll")))
					show_pages_btn = driver.find_element_by_id("divShowAll")
					show_pages_btn.click()
					frame = driver.find_element_by_id("KratisisList")
					offers = frame.find_elements_by_xpath(".//div[contains(@id,'ctl00_MainAreaPlaceHolder_carResults_')]")
					prices = driver.find_elements_by_xpath("//span[@class='Price']")
					prices = [x.text for x in prices]
					print(prices)
					for offer in offers:
						data = offer.find_element_by_xpath(".//table//td[@valign='top']").text
						try:
							price = offer.find_element_by_xpath(".//span[@class ='Price']").text
						except:
							price = "Sold out for these dates"
						data_list = data.split("\n")
						title = data_list[0]
						details = data_list[1]
						get_indicatiors(title, details, price)
	driver.execute_script("window.history.go(-1)")
	continue

