# https://www.youtube.com/watch?v=XQgXKtPSzUI

# parse the text
from bs4 import BeautifulSoup as soup
# web request 
from urllib.request import urlopen as uReq

my_url = 'https://www.newegg.com/Video-Cards-Video-Devices/Category/ID-38?Tpk=graphics%20card  '

# opening connection
uClient = uReq(my_url)

# loads content of the html to variable 
page_html = uClient.read()

# close the client session 
uClient.close()

# parse the html 
page_soup = soup(page_html, 'html.parser')

# grab each product 
containers = page_soup.findAll('div', {'class':'item-container'})

for container in containers:
    
    #brand = container.div.div.a.img['title']
    
    title_container = container.findAll('a',{'class':'item-title'})
    
    product_name = title_container[0].text
    
    shipping_container = container.findAll('li', {'class': 'price-ship'})
    
    shipping = shipping_container[0].textstrip()
    
    print(brand)
    print(product_name)
    print(shipping)