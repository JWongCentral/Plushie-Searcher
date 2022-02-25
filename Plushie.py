import tkinter.filedialog

from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
from tkinter import *
import tkinter as tk
from xlwt import Workbook
import os
import PySimpleGUI as sg
import threading

# GUI should ask for user to search for a specific plushie and check/uncheck all websites it wants to look for
# when searching it will print out an excel sheet that will list off the website and embed


# item object
class Product:
    def __init__(self):
        self.name = ""
        self.URL = ""
        self.price = 0

    def __str__(self):
        return self.name+"|"+self.price+"|"+self.URL

# var to hold results from all searches
productList = []

# var to hold watchlist products to continuously check for updates
watchList = []

excelFilePath = ""
wordFilePath = ""

#askFilePath
def askFilePath():
    root = tk.Tk()
    root.withdraw
    file_path = tkinter.filedialog.askopenfilename()
    root.destroy()
    return file_path

def saveExcel(filePath):
    wb = Workbook()
    sheet1 = wb.add_sheet('Results')


    # first labels for first row
    sheet1.write(0, 0, 'Name')
    sheet1.write(0, 1, "Price")
    sheet1.write(0, 2, "Product Url")
    for x in range(0, len(productList)):
        sheet1.write(x + 1, 0, productList[x].name)
        sheet1.write(x + 1, 1, productList[x].price)
        sheet1.write(x + 1, 2, productList[x].URL)

    print(filePath)
    wb.save(filePath)

# saves the list as an excel doc
def saveProductList():
    if(len(productList)!=0):

        #checks to see if we have excelFilePathLoaded
        if(excelFilePath==""):
            fileName = 'ProductList'

            #grabs root directory for the program
            directory = os.getcwd() +"\\"+fileName+".xlsx"

            #looks for a unique name to save
            exists = os.path.exists(directory)
            temp = 1
            while(exists == True):

                directory = os.getcwd() +"\\"+fileName+str(temp)+".xlsx"
                exists = os.path.exists(directory)
                if(exists == False):
                    fileName = fileName+str(temp)
                else:
                    temp= temp+1

        if(excelFilePath == ""):
            #trying to save as new file since we did not load one

            saveExcel(directory)

        elif(excelFilePath!=""):
            #trying to overwrite save of loaded filepath
            saveExcel(excelFilePath)







# clears list
def clearProductList():
    productList.clear()


# loads pre-existing filePath
def loadProductList():
    #ask for filepath
    directory = askFilePath()

    #validate if player has selected a filepath
    if(directory == ""):
        return

    #emptying list to be filled by excel input
    clearProductList()

    global excelFilePath
    excelFilePath = directory

    #using pandas to read excel
    df = pd.read_excel(excelFilePath)

    #going through all rows to add product to path
    for x in range(0,len(df.index)):

        #creating and grabbing info from excel cells
        item = Product()
        item.name = df.loc[x,'Name']
        item.price = df.loc[x,'Price']
        item.URL = df.loc[x,'Product Url']

        #adding to list
        productList.append(item)



#saving the watchlist as a txt doc
def saveTxtFile(filePath):
    File = open(filePath,'w')
    for x in watchList:
        File.write(x)
    File.close()

# saves watchlist as a word doc
def saveWatchlist():

    global wordFilePath

    #checking that there is something to save
    if (len(watchList) != 0):

        # checks to see if we have existing file txt file loaded
        if (wordFilePath == ""):
            fileName = 'WatchList'

            # grabs root directory for the program
            directory = os.getcwd() + "\\" + fileName + ".txt"

            # looks for a unique name to save
            exists = os.path.exists(directory)
            temp = 1
            while (exists == True):

                directory = os.getcwd() + "\\" + fileName + str(temp) + ".txt"
                exists = os.path.exists(directory)
                if (exists == False):
                    fileName = fileName + str(temp)
                else:
                    temp = temp + 1

        if (wordFilePath == ""):
            # trying to save as new file since we did not load one
            wordFilePath = directory
            saveExcel(directory)

        elif (wordFilePath != ""):
            # trying to overwrite save of loaded filepath
            saveExcel(excelFilePath)

#loads the watchlist from the txt file
def loadWatchList():

    #asks player which txt file to load
    filePath = askFilePath()

    #Checks if user has input a directory
    if(filePath ==""):
        return

    global wordFilePath
    wordFilePath = filePath

    #File to read
    File = open('r', filePath)

    #read each product line in the txt file
    for x in File.readlines():

        temp = x

        #creating item to store result
        item = Product()
        item.name = temp[0:temp.find('|')]
        temp = temp[temp.find('|')+1:]
        item.price = temp[0:temp.find('|')]
        item.URL = temp[temp.find('|')+1:]

        watchList.append(item)

    File.close()


#process to check if watchlist URLS have changed
def runWatchList():
    for x in range(0,len(watchList)):
        URL = watchList[x].URL

def clearWatchList():
    watchList.clear()

# check for duplicate entries
def addProduct(product):
    global productList

    for x in product:

        for y in productList:

            if (x.URL == y.URL):
                return False

        productList.append(x)

    return True



# Web Scraping
def loadWalGreens(itemName):

    #grabbing html source from link
    URL = "https://www.walgreens.com/search/results.jsp?Ntt=" + itemName
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    page = "&page="



    html_text = requests.get(URL, headers=headers)
    soup = BeautifulSoup(html_text.content, features="html.parser")

    #checks if we have any results
    if(soup.find('Looks like we don\'t have any matches for') != -1):
        return
    # grabbing all results on current page
    results = soup.find_all('div', class_='product__text')

    # stores individual products
    productResults = []
    for x in results:

        productURL = 'https://www.walgreens.com' + x.find(class_='color__text-black').get('href')

        html_text = requests.get(productURL, headers=headers)
        soup = BeautifulSoup(html_text.content,features='html.parser')

        productName = soup.find(class_='wag-text-black pr10 wag-ounce-price product-span-style').getText()

        price = float(soup.find(class_='product__price').getText().replace("$",''))/100

        #creating item based off of information obtained
        item = Product()
        item.name = productName
        item.price = price
        item.URL = productURL

        productResults.append(item)

    #adds and checks to see if it has already been added to the list
    addProduct(productResults)


def getPaperStore():

    #grabbing all squishmallow results
    URL = "https://w0rayx.a.searchspring.io/api/search/search.json?ajaxCatalog=v3&resultsFormat=native&siteId=w0rayx&domain=https%3A%2F%2Fwww.thepaperstore.com%2Fc%2Fsquishmallows&bgfilter.hierarchy=Brands%2FSquishmallows&q=&lastViewed=61309300005&lastViewed=63839500005&lastViewed=62610400005&lastViewed=62610600005"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    page = "&page="

    html_text = requests.get(URL, headers=headers)
    soup = BeautifulSoup(html_text.content, features="html.parser")

    # grabbing all results on current page
    temp = soup.text
    results = []

    #storing finished scraped items into an array
    productResults = []


    while (temp.find("\"url\":") != -1):
        productUrl = temp[temp.find("\"url\":"):temp.find(",", temp.find("\"url\":"))]
        results.append(productUrl.replace("\"", "").replace("url:", ""))
        temp = temp[temp.find(",", temp.find("\"url\":")):]

    #loop to grab the
    for x in results:
        productUrl = x

        html_textProduct = requests.get(productUrl, headers=headers)
        productSoup = BeautifulSoup(html_textProduct.content, features="html.parser")

        productName = productSoup.find(class_='nm product-information--purchase_name bold').getText()

        productPrice = float(productSoup.find(class_='product-information--purchase_price js-price-value').getText().replace("$",''))

        #creates item from gathered information above
        item = Product()
        item.name = productName
        item.price = productPrice
        item.URL = productUrl

        productResults.append(item)

    addProduct(productResults)

def loadCrackerBarrel(itemName):

    #grabs html source from item search
    URL2 = "https://www.crackerbarrel.com/crackerbarrel/api/get/searchresults?searchterm=" + itemName + "&currentPage=1&pageSize=25&datasource={AEFA1F7D-CCCD-44D2-90BA-384CAC73E9B4}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    html_text = requests.get(URL2, headers=headers)
    soup = BeautifulSoup(html_text.text, features="html.parser")

    # grabbing all results on current page
    text = soup.text

    #Stores web-scraped items in here
    productResults = []

    # checks if results are in
    if (text.find("\"totalResults\":0") == -1):
        # finding product details
        while (text.find("\"title\":") != -1):
            # temp to store result found
            temp = text[text.find("\"title\":"):text.find(",", text.find("\"title\":"))]
            name = temp[8:]
            text = text[text.find(name):]
            name = name.replace("\"", "").replace("\\", "")

            temp = text[text.find("\"price\":"):text.find(",", text.find("\"price\":"))]
            temp = temp[8:]
            price = float(temp.replace("\"", ""))

            temp = text[text.find("\"pageUrl\":"):text.find(",", text.find("\"pageUrl\":"))]
            temp = temp[10:]
            text = text[text.find(temp):]
            productUrl = temp
            productUrl = "https://www.crackerbarrel.com" + productUrl

            productResult = Product()
            productResult.price = price
            productResult.name = name
            productResult.URL = productUrl


            productResults.append(productResult)
        addProduct(productResults)


def loadOwlAndGooseGifts(itemName):

    #url and headers for requesting source code from website
    URL = "https://owlandgoosegifts.com/search?q=" + itemName
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    page = "&page="
    pageNumber = 1

    #stores finished and scraped product
    productResult = []

    #stores all url for all products found
    productUrl = []

    # initial search(page 1 search)
    html_text = requests.get(URL, headers=headers)
    soup = BeautifulSoup(html_text.content, features="html.parser")
    # grabbing all results on current page
    results = soup.find_all('a', class_='full-width-link')

    #no results found
    if(results == None):
        return

    #adding url to lists
    for x in results:
        productUrl.append("https://owlandgoosegifts.com" + x.get('href'))

    #checks how many more pages we have
    results = soup.find('li', class_='pagination__text')
    if(results != None):
        pager = results.getText()
        pager = pager[pager.find("of ") + 3:]
        pager = pager.replace(" ", "").replace("\n", "")

        #loop to go through all pages
        while (pageNumber <= int(pager)):

            #grabbing source code from the current page
            pageUrl = "https://owlandgoosegifts.com/search?options%5Bprefix%5D=last" + page + "&q=" + itemName
            html_text = requests.get(pageUrl, headers=headers)
            soup = BeautifulSoup(html_text.content, features="html.parser")

            # grabbing all product URLS on current page
            results = soup.find_all('a', class_='full-width-link')

            #adding the link to the list ProductURl
            for x in results:
                productUrl.append("https://owlandgoosegifts.com" + x.get('href'))

            #updates current page
            results = soup.find('li', class_='pagination__text')
            pager = results.getText()
            pager = pager[pager.find("of ") + 3:]
            pager = pager.replace(" ", "").replace("\n", "")
            pageNumber = pageNumber + 1

    #filtering through all URLS to add to list
    for x in productUrl:

        #grabbing source code from productUrl
        html_textProduct = requests.get(x, headers=headers)
        productSoup = BeautifulSoup(html_textProduct.content, features="html.parser")

        #grabbing elements for the item
        productName = productSoup.find(class_='product-single__title').getText()
        productPrice = float(productSoup.find(class_='price-item price-item--regular').getText().replace('$',''))

        #creating item and adding it to the list
        item = Product()
        item.URl = x
        item.name = productName
        item.price = productPrice

        productResult.append(item)

    addProduct(productResult)




def loadBannersHallmark(itemName):

    #grabs html source code from URL
    URL = "https://www.bannershallmark.com/search?type=product%2Carticle%2Cpage&q=" + itemName
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    html_text = requests.get(URL, headers=headers)
    soup = BeautifulSoup(html_text.content, features="html.parser")

    #list to store all product Url's across multiple pages
    productUrl = []

    # grabbing all results on current page
    results = soup.find_all('a', class_='grid-product__link')

    #initial page search results
    for x in results:
        productUrl.append("https://www.bannershallmark.com/" + x.get('href'))

    #find all next page URl
    pages = soup.find('div', class_="pagination")
    if(pages!=None):
        pages =pages.find_all('span', class_="page")

        #adding multiple pages of results
        for x in pages:
            pages = x.find('a', href=True)

            #checks if the page URL exists
            if (pages != None):
                #getting the page URL and HTML code
                URL = "https://www.bannershallmark.com" + pages.get('href')
                html_text = requests.get(URL, headers=headers)
                soup = BeautifulSoup(html_text.content, features="html.parser")
                # grabbing all results on current page
                results = soup.find_all('a', class_='grid-product__link')

                #adding results from the page
                for y in results:
                    productUrl.append("https://www.bannershallmark.com/" + y.get('href'))

        #reading in each productUrl
        for x in productUrl:

            #getting html source from productUrl
            html_textProduct = requests.get(x, headers=headers)
            soupProduct = BeautifulSoup(html_textProduct.content, features="html.parser")

            #filtering data to get the desired elements
            productName = soupProduct.find(class_='h2 product-single__title').getText()
            productPrice = float(soupProduct.find(class_='product__price').getText().replace("$",''))

            #creating item based off of search
            item = Product()
            item.URL= x
            item.name = productName
            item.price = productPrice

            productList.append(item)

    addProduct(productList)
def loadClaires(itemName):

    #URl and headers to webscrape
    URL = "https://www.claires.com/us/search/?q=" + itemName + "&lang=en_US"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    #stores all product URL's
    productUrl = []

    #stores finished results
    productResult = []

    currentPage = 1

    #getting html code from URL
    html_text = requests.get(URL, headers=headers)
    soup = BeautifulSoup(html_text.content, features="html.parser")

    # grabbing all results on current page
    results = soup.find_all('a', class_='link-wrap thumb-link')

    #adding first page product URL to array
    for x in results:
        productUrl.append("https://www.claires.com/" + x.get('href'))

    #grabbing all next page URL's
    pages = soup.find('div', class_='pagination').find_all('a', class_=('page-' + str(currentPage + 1)))
    currentPage = currentPage + 1

    #loop to continue going to next page
    while (len(pages)!=0):

        #going through all the pages
        for x in pages:

            #getting html source code of the pages
            URL = x.get('href')
            html_text = requests.get(URL, headers=headers)
            soup = BeautifulSoup(html_text.content, features="html.parser")

            # grabbing all results on current page
            results = soup.find_all('a', class_='link-wrap thumb-link')

            #adding all productsUrl's on that page
            for x in results:
                productUrl.append("https://www.claires.com/" + x.get('href'))


        #checks if there are any more pages we can go to
        pages = soup.find('div', class_='pagination').find_all('a', class_=('page-' + str(currentPage + 1)))

    #grabbing information from all products
    for x in productUrl:

        #grabs the html source code from the productUrl
        html_textProduct = requests.get(x, headers=headers)
        soupProduct = BeautifulSoup(html_textProduct.content, features="html.parser")

        #searching for our desired elements from the source code
        productName = soupProduct.find(class_='product-name desktop-tablet').getText()
        productPrice = float(soupProduct.find(class_='price-sales base-price').getText().replace("$",'').replace('Sale Price',''))

        #storing it as a Product to add
        item = Product()
        item.URL = x
        item.name = productName
        item.price = productPrice

        productResult.append(item)

    addProduct(productResult)


def loadGameStop(itemName):
    #creates header and link to search for item
    URL = "https://www.gamestop.com/search/?q=" + itemName
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    #stores finished results in list
    productResult = []

    #request and grab source code from link
    html_text = requests.get(URL, headers=headers)
    soup = BeautifulSoup(html_text.content, features="html.parser")

    #filters results for URL
    results = soup.find_all('a', class_='product-tile-link')

    #for loop to filter through all product URLS
    for x in results:

        #gets product link
        productUrl = "https://www.gamestop.com" + x.get('href')

        #grabs html source code from website
        html_textProduct = requests.get(productUrl, headers=headers)
        soupProduct = BeautifulSoup(html_textProduct.content, features="html.parser")

        #searches elements to store
        productName = soupProduct.find(class_='product-name-section').getText().replace('\n','')
        productPrice = float(soupProduct.find(class_="row main-product-section").find(class_='actual-price').getText().replace("\n",'').replace("$",''))

        #creates item to store results
        item = Product()
        item.name = productName
        item.URL= productUrl
        item.price = productPrice

        productResult.append(item)

    addProduct(productResult)

def loadHallMark(itemName):

    #grabs search URL to search Item
    URL = "https://www.hallmark.com/search?q=" + itemName
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    #stores all products in the list
    productResult = []

    #requesting html source code of website
    html_text = requests.get(URL, headers=headers)
    soup = BeautifulSoup(html_text.content, features="html.parser")

    # grabbing all product URLS on current page
    results = soup.find_all('a', class_='title-anchor')

    #for loop to go through all productUrls
    for x in results:

        try:
            productURL="https://www.hallmark.com" + x.get('href')

            #requesting source code from product URL
            html_textProduct = requests.get(productURL, headers=headers)
            soupProduct = BeautifulSoup(html_textProduct.content, features="html.parser")

            #filtering source code for specific elements
            productName = soupProduct.find(class_='page-title').getText()
            productPrice = float(soupProduct.find(class_='price js-for-total').getText().replace('\n','').replace('Regular price','').replace('$',''))

            #creating item from the found elements
            item = Product()
            item.name = productName
            item.URL = productURL
            item.price = productPrice

            productResult.append(item)
        except:
            continue

    addProduct(productResult)

class ThreadingQueue:

    def __init__(self):
        self.Queue = []

    def startQueue(self):
        while(True):
            if(len(self.Queue) != 0):
                self.Queue.__getitem__(0).start()
                self.Queue.remove(0)

    def addSearchThread(self, search,event):
        if(event == '-CB Walgreens-'):
            self.Queue.append(threading.Thread(target = loadWalGreens, args=(search)))
        elif(event == '-CB Cracker Barrel-'):
            self.Queue.append(threading.Thread(target=loadCrackerBarrel, args=(search)))
        elif (event == '-CB Owl and Goose Gifts-'):
            self.Queue.append(threading.Thread(target = loadOwlAndGooseGifts, args=(search)))
        elif (event == '-CB Banners Hallmark-'):
            self.Queue.append(threading.Thread(target = loadBannersHallmark, args=(search)))
        elif (event == '-CB Claires-'):
            self.Queue.append(threading.Thread(target = loadClaires, args=(search)))
        elif (event == '-CB GameStop-'):
            self.Queue.append(threading.Thread(target = loadGameStop, args=(search)))
        elif (event == '-CB Hallmark-'):
            self.Queue.append(threading.Thread(target = loadHallMark, args=(search)))




# creating GUI for webscraper
class GUI:
    #note:
    #add in multi-threading to handle function calls
    #add into search to check which checkbox is checked
    #Use the search to check all the checkboxes and add to the queue





    def __init__(self):
        check_list = [
            [sg.Checkbox('Walgreens', default=True, key="-CB Walgreens-", text_color="#000000",
                         background_color="#FFFFFF")],
            [sg.Checkbox('Cracker Barrel', default=True, key="-CB Cracker Barrel-", text_color="#000000",
                         background_color="#FFFFFF")],
            [sg.Checkbox('Owl and Goose Gifts', default=True, key="-CB Owl and Goose Gifts-", text_color="#000000",
                         background_color="#FFFFFF")],
            [sg.Checkbox('Banners Hallmark', default=True, key="-CB Banners Hallmark-", text_color="#000000",
                         background_color="#FFFFFF")],
            [sg.Checkbox('Claires', default=True, key="-CB Claires-", text_color="#000000",
                         background_color="#FFFFFF")],
            [sg.Checkbox('GameStop', default=True, key="-CB GameStop-", text_color="#000000",
                         background_color="#FFFFFF")],
            [sg.Checkbox('Hallmark', default=True, key="-CB Hallmark-", text_color="#000000",
                         background_color="#FFFFFF", )]
        ]

        Searching_column = [
            [sg.Button("Save", key="-Save-"), sg.Button("Load", key="-Load-")],
            [
                sg.Text("Search"),
                sg.In(size=(25, 1), enable_events=True, key="-Search-", default_text="Type search here"),
                sg.Button(button_text="Search", key='-SearchButton-'),
            ],
            [
                sg.Column(check_list, scrollable=True, size=(300, 400), vertical_scroll_only=True,
                          background_color="#FFFFFF")
            ],
        ]

        Results_column = [
            [sg.Text("Search Results:", font=16)],
            [sg.Listbox(size=(50, 25), values=['result1', 'result2', 'result3', 'result4'], key="-Results-",
                        enable_events=True)]
        ]

        WatchList_column = [
            [sg.Button("Add To Watchlist", key="-Add Watchlist-")],
            [sg.Button("Load Watchlist", key='-Load Watchlist-')],
            [sg.Button("View Watchlist", key="-View Watchlist-")],
        ]
        ViewWatchList_column = [
            [sg.Listbox(size=(50, 25), values=['watchlist1', 'watchlist2'], key='-WatchList-', enable_events=True)]
        ]
        layout = [
            [
                sg.Column(Searching_column),
                sg.VSeparator(),
                sg.Column(Results_column),
                sg.VSeparator(),
                sg.Column(WatchList_column),
                sg.VSeparator(),
                sg.Column(ViewWatchList_column, key='-ColWatchList-', visible=False)
            ]
        ]

        self.window = sg.Window("Image Viewer", layout).finalize()
        self.QueueThread = ThreadingQueue()

    #runs the main thread for loop and the alt thread
    #to handle request webscraping

    def runMainLoop(self):
        #threading.Thread(target=self.QueueThread.startQueue()).start()

        selected = ''
        viewingWatchList = False

        while True:
            event, values = self.window.read()

            if (event == "Exit" or event == sg.WIN_CLOSED):
                break
            elif (event == '-Save-'):
                saveProductList()
                print("save Product list")
            elif (event == '-Load-'):
                loadProductList()
            elif (event == '-SearchButton-'):
                clearProductList()
                search = values['-Search-']
                if(values['-CB Walgreens-'] == True):
                    threading.Thread(target = loadWalGreens, args=(search,)).start()
                if(values['-CB Cracker Barrel-'] == True):
                    threading.Thread(target=loadCrackerBarrel, args=(search,)).start()
                if(values['-CB Owl and Goose Gifts-'] == True):
                    threading.Thread(target=loadOwlAndGooseGifts, args=(search,)).start()
                if(values['-CB Banners Hallmark-'] == True):
                    threading.Thread(target=loadBannersHallmark, args=(search,)).start()
                if (values['-CB Claires-'] == True):
                    threading.Thread(target=loadClaires, args=(search,)).start()
                if (values['-CB GameStop-'] == True):
                    threading.Thread(target=loadGameStop, args=(search,)).start()
                if (values['-CB Hallmark-'] == True):
                    threading.Thread(target=loadHallMark, args=(search,)).start()

            elif (event == '-Add Watchlist-'):
                printProductList()
            elif (event == '-Load watchlist-'):
                loadWatchList()
            elif (event == "-Results-"):
                if(len(values['-Results-']) != 0):
                    print("add in bottom gui later")
            elif (event == '-View Watchlist-'):
                if (viewingWatchList == True):
                    self.window['-ColWatchList-'].update(visible=False)
                    viewingWatchList = False
                elif (viewingWatchList == False):
                    self.window['-ColWatchList-'].update(visible=True)
                    viewingWatchList = True
            if(len(productList) != self.window['-Results-'].get()):
                self.window['-Results-'].update(values=getProductListNames())
        try:
            self.window.close()
            sys.exit(0)
        except:
            print("exited")
def getProductListNames():
    temp = []
    for x in productList:
        temp.append(x.name)
    return temp
def printProductList():
    for x in productList:
        print("Product Name:" + x.name)
        print("URL:" + x.URL)
        print("Price:" + str(x.price))
        print("\n")


if __name__ == '__main__':
    gui = GUI()
    gui.runMainLoop()




#note:
#make sure to add rest of buttons
#possibly work on a watchlist function later
