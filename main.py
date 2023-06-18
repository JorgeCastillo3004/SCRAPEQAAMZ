from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import random

# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver 
import chromedriver_autoinstaller 
import pandas as pd
 
def findSearchBoxClick(driver, product):
	# FIND ELEMENT TO INIT SEARCH
	element = driver.find_element(By.ID,"twotabsearchtextbox") # SEARCH INPUT AMAZON SEARCH
	element.clear() # CLEAN SEARCH BOX
	# SEND PRODUCT SEARCH WORD
	element.send_keys(product + '\n')

def changeDeliverCountry(driver, country):
	# FIND ELEMENT CHANGE COUNTRY DELIVER
	countrylist = driver.find_element(By.ID, "glow-ingress-block") # FIND COUNTRY BUTTON
	countrylist.click()

	# SELECT DELIVER COUNTRY
	time.sleep(3)
	countrylist = driver.find_element(By.ID, "GLUXCountryList") # LIST OF COUNTRIES SHIPS AVAILABLE

	# SELECT FROM DROPDOWN 
	countryselection = Select(countrylist)
	countryselection.select_by_visible_text(country)
	time.sleep(3)
	donebutton = driver.find_element(By.ID, "a-autoid-3") # SEARCH BUTTON DONE

	donebutton.click() # CLICK ON BUTTON DONE

def getLinksResults(driver):
	resultList = driver.find_elements(By.CLASS_NAME, "a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal")

	listlinksresults = []
	
	for result in resultList:
	    listlinksresults.append(result.get_attribute('href'))
	
	listlinksresults = list(dict.fromkeys(listlinksresults)) # Drop duplicates of the link

	return listlinksresults

def findFirstItemResult(driver):
	firstproduct = driver.find_element(By.CLASS_NAME, "a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal")
	firstproduct.click()
	# return firstproduct

def clickOffertsButton(driver):
	# CLICK IN ELEMENT TO SHOW OFERTS
	ofertlink = driver.find_element(By.CLASS_NAME, "a-section.olp-link-widget")
	ofertlink.click()
	time.sleep(2)

def getCurrentSellerLink(driver):	
    # Get URL of current seller
    sellerLinks = []
    currentsellerlink = driver.find_element(By.ID, 'sellerProfileTriggerId').get_attribute('href')
    sellerLinks.append(currentsellerlink)
    return sellerLinks

def getSellersLink(driver, sellerLinks):
	# GET LINKS HREF FOR EACH SHOPING DETAILS
	shopingdetails = driver.find_elements(By.CLASS_NAME, 'a-size-small.a-link-normal')
	
	for shopingdetail in shopingdetails:
	    if shopingdetail.text!='':
	        sellerLinks.append(shopingdetail.get_attribute('href'))
	return sellerLinks

def navigateSellerLinks(driver, sellerLinks, idproduct):
	# Explore each link for extrac shoping info.
	# Check if the info is appropiated load in contrary case reload again.
	
	dfsellers = pd.DataFrame()
	for idlink, shoppinglink in enumerate(sellerLinks):
		# sellerInfoDict = {} # Create a empty dict to save sellers info.
		# sellerInfoDict['idproduct']= idproduct
	    # Create key in empty dict
	    # sellerInfoDict[idlink] = {}
	    
	    driver.get(shoppinglink) # Load each seller information	    
	    
	    # Search by id class page-section-detail-seller-info that contains seller info.
	    # If seller info is not find it try again and reload the page. 
	    sellersInfo = driver.find_elements(By.ID, "page-section-detail-seller-info")

	    while len(sellersInfo)==0: # While the info is empty it continue trying until get some information
	        timewait = random.uniform(1.5, 6.3)    # Generate a ramdom time sleep for try again
	        time.sleep(timewait)                   # time sleep runing
	        driver.get(shoppinglink)                # reload again the seller info link
	        sellersInfo = driver.find_elements(By.ID, "page-section-detail-seller-info") # verify if sellerinfo is not empty.
	    
	    # Seller info extraction 
	    sellerdict = getSellerDetails(driver, idproduct)
	    
	    # Extract other brands offers by the same seller
	    for t in sellersInfo: # iterate or sweeping in each element of the list.
	    	# Some times seller link info is not available
	        try:
	            sellerinfo = driver.find_element(By.ID, "seller-info-storefront-link") # Find link to locate all the brands that the seller offert
	            sellerlink = sellerinfo.find_element(By.TAG_NAME, "a")
	            
	            print(sellerlink.get_attribute('href'))
	            sellerlink.click()
	            time.sleep(2)	            
	            sellerdict['SellerBrands'] = [findBrands(driver)]

	        except:
	            print("Seller info dont find")
	            sellerdict['SellerBrands'] = ['info not find']

	    dfseller = pd.DataFrame.from_dict(sellerdict)

	    dfsellers = pd.concat([dfsellers, dfseller])

	return dfsellers

def findBrands(driver):
    sellerbrands = driver.find_element(By.ID, 'brandsRefinements')    
    return (', '.join(sellerbrands.text.split('\n')[1:]))
    
def getSellerDetails(driver, idproduct):
	# Search block Seller Detail Info
    sellerdetailsblock = driver.find_element(By.ID, "page-section-detail-seller-info")    
    sellerdict = {}
    sellerdict['idproduct'] = [idproduct]

    sellerinfo = sellerdetailsblock.text.split('\n') # Create a list from element find with sellers details

    sellerdict['name'] = [sellerinfo[1].replace('Business Name: ','')]
    sellerdict['address'] = [sellerinfo[3]]
    sellerdict['city'] = [sellerinfo[-4]]
    sellerdict['state'] = [sellerinfo[-3]]
    sellerdict['zip code'] = [sellerinfo[-2]]
    sellerdict['country'] = [sellerinfo[-1]]
    return sellerdict

def productsInfo(driver):
	# Find block of product info.
    productDetails = driver.find_element(By.ID, 'detailBulletsWrapper_feature_div')
    
    productDict = {}

    productdetailist = productDetails.text.split('\n')

    # productDict
    for i, detail in enumerate(productdetailist):

        if 'Department :' in detail:
            productDict['Category'] = [detail.replace('Department :','')]    

        if 'ASIN :' in detail:
            productDict['ASIN'] = [detail.replace('ASIN :','').replace(' ','')]
    try:
        detailreview = productDetails.find_element(By.ID, 'detailBullets_averageCustomerReviews')
        productDict['Rating'] = [detailreview.text.split()[0]]
        productDict['Review Counts'] = [detailreview.text.split()[1]]
    except:
        productDict['Rating'] = ['without ratings']
        productDict['Review Counts'] = ['without reviews']

    return productDict

def getMoreInfoProduct(driver, productDict):

    # Find product URL
    productlink = driver.find_element(By.ID, 'bylineInfo')    
    productDict['URL'] = [productlink.get_attribute('href')]
    
    # Find title of product
    productTitle = driver.find_element(By.ID, 'productTitle')
    productDict['Title'] = [productTitle.text]
    
    # Find price   

    productWholePrice = driver.find_element(By.CLASS_NAME, 'a-price-whole') # Integer part
    productFractionPrice = driver.find_element(By.CLASS_NAME, 'a-price-fraction') # Fraction part
    productDict['Price $'] = [productWholePrice.text +'.'+productFractionPrice.text]
    
    return productDict


from main import *

chromedriver_autoinstaller.install() 
 
# Create Chromeoptions instance 
options = webdriver.ChromeOptions() 
 
# Adding argument to disable the AutomationControlled flag 
options.add_argument("--disable-blink-features=AutomationControlled") 
 
# Exclude the collection of enable-automation switches 
options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
 
# Turn-off userAutomationExtension 
options.add_experimental_option("useAutomationExtension", False) 
 
# Setting the driver path and requesting a page 
driver = webdriver.Chrome(options=options) 
 
# Changing the property of the navigator value for webdriver to undefined 
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
 
driver.get("https://www.amazon.com/-/en/")

# PENDING ADD WAIT UNTIL FIND ESPECIFIC ELEMENT

if __name__ == '__main__':

    dfsellersInfo = pd.DataFrame()
    dfProductsInfo = pd.DataFrame()

    idproduct = 0
    product, country = 'creave cream', 'Canada'
    findSearchBoxClick(driver, product)	
    print("Sent first search and give click")
    time.sleep(3)

    changeDeliverCountry(driver, country)
    print("Changed shippint country")
    time.sleep(3)

    # Click on first result (CHANGE TO MAKE A LOOP IN ALL THE LINKS)

    listlinksresults = getLinksResults(driver)
    print("List of links loaded")

    for idresult, linkresult in enumerate(listlinksresults[0:3]):        
        
        driver.get(linkresult)
        print("idresult", idresult,"Load each result from search")
        time.sleep(3)

        productDict = productsInfo(driver)
        productDict = getMoreInfoProduct(driver, productDict)

        dfproductDict = pd.DataFrame.from_dict(productDict)
        dfProductsInfo = pd.concat([dfProductsInfo, dfproductDict])
        # Click in current seller.
        try:
            sellerLinks = getCurrentSellerLink(driver)
            print("Get current seller link")
        except:
            print("Current seller without link")
            sellerLinks = []

        clickOffertsButton(driver)
        print("Click on offers button")
        time.sleep(3)

        sellerLinks = getSellersLink(driver, sellerLinks)
        print("Get seller links")

        # Navigate in each seller link 
        productID = product.replace(' ','_') + '_' + str(idresult)
        dfsellers = navigateSellerLinks(driver, sellerLinks, productID)
        dfsellersInfo = pd.concat([dfsellersInfo, dfsellers])

    ## nextbutton.click()
    print("Finish")