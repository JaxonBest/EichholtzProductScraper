import urllib.request
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
import json
import colorama
from datetime import datetime
import string
import random
import webbrowser
import requests
import time
import os
import threading
import xlsxwriter as ex
import os.path

ipgeo_key = '8bcd904869914aa786cfc56de192e33c'


class Data:
    def __init__(self):
        # get all the required elements.
        self.required_page_json = json.load(open('./product-info.json'))


def MakeRandomString():
    x = string.ascii_letters +  "1234567890"
    length = random.randint(10, 25)
    result = ''
    for i in range(length):
        result += random.choice(x)
    return result

# Controls all of the requests


class Http:
    def __init__(self):
        self.origin_url = "https://www.eichholtz.com/en/collection/new/new-arrivals.html"
        self.temp_filename = MakeRandomString() + ".json"
        json.dump({'indv-html': []}, open(self.temp_filename, 'w'), indent=4)
        self.temp_json = {'indv-html': []}
        json.dump({'indv-html': []},
                  open(f"./{self.temp_filename}", 'w'), indent=4)
        USER_AGENT = UserAgent()
        self.uas = None  # User agents
        config = json.load(open('./config.json', 'r'))

        # 0 User agents are inserted as this point.
        if len(config['user-agents']) < 1:
            print("""oops.. not enough user agents found..\nuser agents are used for http requests, some websites block requests with weird looking user-agents.\ni like to use firefox useragent's
            because why not.""")
            print("inserting 200 user agents")
            self.uas = []
            for i in range(1, 200):
                cua = USER_AGENT.firefox
                print(f"adding user agent no. {i} ({str(cua)})")
                self.uas.append(cua)
                time.sleep(0.05)
            config['user-agents'].append(self.uas)
            config = json.dump(config, open('./config.json', 'w'), indent=4)
        else:
            self.uas = config['user-agents']

    def UpdatePageOrigin(self, by_no=1):
        try:
            int(self.origin_url[-1])
        except:
            print("Updating page origin query")
            self.origin_url += '?p=2'
            print("finished.. returning data")
            return 2

        print('page no. is not 0 diverting methods..')

        new_page_no = None

        x = int(self.origin_url[-1])
        x += by_no

        chars = list(self.origin_url)
        chars.pop(-1)
        chars.append(x)
        result = ''
        print("concatanating origin string")
        for i_char in chars:
            result += i_char
        self.origin_url = result
        print("finished and updated concat. now returning.")
        return i_char

    def GrabPagesOfProductInfo(self, pages):
        print('running "for" loop for every page...')
        ua = random.choice((self.uas))
        for i in range(pages):
            print('going through loop no. %s' % i)
            if i == 0:
                config = json.load(open('./config.json', 'r'))
                config['pages_scraped'] += 1
                json.dump(config, open("./config.json", 'w'))
                print(f'GET REQUEST TO {self.origin_url}')
                req = urllib.request.Request(
                    url=self.origin_url, headers={"user-agent": ua})
                html = urllib.request.urlopen(req).read().decode(
                    'utf-8')  # decode string into writeable format (utf-8)
                print("Assigned html variable to site html")

                data = json.load(open(f'./{self.temp_filename}', 'r'))
                data['indv-html'].append(html)
                return json.dump(data, open(f'./{self.temp_filename}', 'w'), indent=4)
            else:
                config = json.load(open('./config.json', 'r'))
                config['pages_scraped'] += 1
                json.dump(config, open("./config.json", 'w'))
                self.UpdatePageOrigin()
                print(f'GET REQUEST TO {self.origin_url}')
                req = urllib.request.Request(
                    url=self.origin_url, headers={"user-agent": ua})
                html = urllib.request.urlopen(req).read().decode(
                    'utf-8')  # decode string into writeable format (utf-8)
                print("Assigned html variable to site html")
                data = json.load(open(f'./{self.temp_filename}', 'r'))
                data['indv-html'].append(html)
                return json.dump(data, open(f'./{self.temp_filename}', 'w'), indent=4)

def GetIPInfo():
    req = requests.get(
        f"https://api.ipgeolocation.io/ipgeo?apiKey={ipgeo_key}")
    JSON = req.json()
    return JSON

class HtmlParser:
    def __init__(self):
        self.all_products = None

    def GetProducts(self, html, page_info):
        soup = BS(html, "lxml")
        ol = soup.find(
            'ol', {"class": page_info['product-div'][1]})
        product_items = ol.find_all('li')
        product_dicts = []
        for product_item in product_items:
            print("__________________")
            sp = page_info['single-product'][0]
            info = {}
            # Label Div
            md = product_item.find_all('div')[0]
            label = md.find('div', {"class": sp['label'][1]})
            label_a = label.find_all('a')[0]
            info['product-url'] = label_a['href']
            print("Product URL: " + label_a['href'])
            label_a_span = label_a.find_all('span')[0]
            info['img_url'] = label_a_span.img['src']
            print("Image URL: " + label_a_span.img['src'])

            #  Details bottom div.
            product_details = product_item.find(
                'div', {"class": "product details product-item-details"})
            sku = product_details.find(
                'div', {"class": f"{sp['product-details-sku'][1]}"})
            sku = sku.string
            info['sku'] = sku
            print("SKU: " + sku)

            name_container = product_details.find(sp['product-details-name-container'][0],
                                            {f"{sp['product-details-name-container'][2]}": 
                                            sp['product-details-name-container'][1]})

            # name_a = name_container.find_all('a', {"class": "product-item-link"})[0]
            name_a = name_container.find('a', {"class": "product-item-link"})
            print(name_a.string)

            info['name'] = name_a.string

            product_dicts.append(info)
            
        self.all_products = product_dicts
        return product_dicts

    def CompileAllProducts(self, folder_name, products):
        os.mkdir(folder_name)
        global images_downloaded

        def DownloadImage(p: dict):
            img_bytes = requests.get(p['img_url']).content
            with open(f"./{folder_name}/{p['name'].replace(' ', '')}/product-image.png", 'wb') as IF:
                IF.write(img_bytes)
            print("Downloaded image for %s" % p['name'].replace(' ', ''))
        threads = []
        for product in products:
            try:
                os.mkdir(f"./{folder_name}/{product['name'].replace(' ', '')}")
            except:
                pass
            threads.append(threading.Thread(target = DownloadImage, kwargs={"p": product}))
            with open(f"./{folder_name}/{product['name'].replace(' ', '')}/information.txt", 'w') as f:
                f.write(f"""Name: {product['name']}
Product URL: {product['product-url']}
Images can be found in the same folder, but here is the link: {product['img_url']}
SKU: {product['sku']}
Product Description: Hopefully will be added later...
                """)

        for i in range(len(threads)):
            threads[i].start()

        for i in range(len(threads)):
            threads[i].join()

    def log_all_sku(self):
        if self.all_products is None:
            return
        config = json.load(open("./config.json", 'r'))
        config['sku-log'].append(p['sku'] for p in self.all_products)
        json.dump(config, open('./config.json', 'w'))



class Excel:
    def __init__(self):
        self.workbook = None
        self.info = {}

    def CreateNotebook(self, products, custom_format_options=None, product_folder_name=None):
        if product_folder_name is None:
            raise Exception("CreateNotebook not supplied with the product folder name")
        
        print("Creating notebook..")

        options = {"human-readable": True, "dear-exportable": True, "category_guidance_fields": True}
        
        if custom_format_options is not None:
        
            for option in custom_format_options:
                options[option['name']] = option['value']
        
        try:
            os.mkdir("EXCEL")
        except:
            return print(f"There seems to already be a folder called excel inside of {product_folder_name}.\bMaybe try deleting that folder.")

        workbook = ex.Workbook(f"{product_folder_name}/EXCEL/products.xlsx")
        ws = workbook.add_worksheet()

        bold_cell = workbook.add_format({"bold": True})

        if options['category_guidance_fields']:
            row, col = 1, 0

            # Write categories
            ws.write(0, 0, "name", bold_cell)
            ws.write(0, 1, "sku", bold_cell)
            ws.write(0, 3, "image url", bold_cell),
            ws.write(0, 4, "product url", bold_cell)

        else:
            row, col = 0, 0  

        for product in products:
            ws.write(row, col, product['name'])
            ws.write(row, col+1, product['sku'])
            ws.write(row, col+2, product['img_url'])
            ws.write(row, col+3, product['product_url'])

        print("Closing notebook!")

        ws.close()

class Customize:
    def __init__(self):
        if not os.path.exists("./customize.txt"):
            with open('./customize.txt', 'w') as f:
                f.write('''# This is the customize file.
                # This is where you can tweak the settings and performance of the program.
                # Everytime I use a "#" at the start of the line, the program ignores the line
                # If I didn't it would read the line and tweak settings.
                # This program is highly customizeable. 
                # Please visit https://github.com/M3Horizun/EicholtzProductScraper/guide.md
                # Version 0.0.1 by Jaxon Best
                ''')

def main():
    colorama.init()
    print(colorama.Fore.GREEN + "Eichholtz Product Info Scraper.")
    print(colorama.Fore.LIGHTYELLOW_EX + "Version: 0.0.1 By Jaxon Best")
    IPInfo = GetIPInfo()
    User_Data = json.load(open("./config.json", 'r'))
    new_user_formatted = ''
    if User_Data['new_user']:
        new_user_formatted = """When using this tool, all of your previous session data will be stored in this folder.
My recommendation is to not delete the folder.
Things like the amount of pages you have got products from will be stored.
What's great about the local database is that you will never get the same sku number twice!

IMPORTANT:

Make sure this program is in it's own folder with config.json & product-info.json.
Files may be generated when running this program. And some may stay if needed.
All of the products will be stored in a extra folder. It's optional to also download images..
        """
        webbrowser.open("https://github.com/M3Horizun/EicholtzProductScraper")
    else:
        new_user_formatted = "Welcome back... No need to tell you the details."
    print(colorama.Fore.GREEN + f"""No Syntax Running Issues!
IP: {IPInfo['ip']},
Internet Servide Provider: {IPInfo['isp']},
Current Time: {datetime.now()}
Country: {IPInfo['country_name']}
    """)
    print(colorama.Fore.CYAN + new_user_formatted)
    _ = colorama.Fore.RESET

    config = json.load(open('./config.json', 'r'))
    config['new_user'] = False
    json.dump(config, open("./config.json", 'w'))

    page_amounts = input("""Press ENTER to start scraping..
    """)

    http = Http()
    http.GrabPagesOfProductInfo(4)

    print("All requests have been made, now getting the information.")

    temp_filename = http.temp_filename

    pages = json.load(open(temp_filename, 'r'))['indv-html']

    product_info = json.load(open('./product-info.json', 'r'))

    pages_of_products = []
    parser = HtmlParser()

    for page in pages:
        pages_of_products.append(parser.GetProducts(page, product_info))

    product_folder_name = f"eiholtz.{datetime.now().strftime(r'%d.%m.%Y').replace(' ', '')}"

    parser.CompileAllProducts(product_folder_name, parser.all_products)




if __name__ == '__main__':
    main()
