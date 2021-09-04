import urllib.request
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import colorama
from datetime import datetime
import string
import random
import os.path
import os
import webbrowser
import requests

ipgeo_key = '8bcd904869914aa786cfc56de192e33c'


class Data:
    def __init__(self):
        # get all the required elements.
        self.required_page_json = json.load(open('./product-info.json'))


def MakeRandomString():
    x = string.ascii_letters + "1234567890"
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
        self.uas = None# User agents
        config = json.load(open('./config.json', 'r'))
        
        if len(config['user-agents']) < 1: # 0 User agents are inserted as this point.
            print("""oops.. not enough user agents found..\nuser agents are used for http requests, some websites block requests with weird looking user-agents.\ni like to use firefox useragent's
            because why not.""")
            print("inserting 200 user agents")
            self.uas = []
            for i in range(1, 200):
                cua = USER_AGENT.firefox
                print(f"adding user agent no. {i} ({str(cua)})")
                self.uas.append(cua)
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
                req = urllib.request.Request(url=self.origin_url, headers={"user-agent": ua})
                html = urllib.request.urlopen(req).read().decode('utf-8') # decode string into writeable format (utf-8)
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

def main():
    colorama.init()
    print(colorama.Fore.GREEN + "Eichholtz Product Info Scraper.")
    print(colorama.Fore.LIGHTYELLOW_EX + "Version: 0.0.1 By Jaxon Best")
    IPInfo = GetIPInfo()
    User_Data = json.load(open("./config.json"))
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

    page_amounts = int(input("""Enter in the amount of pages you would like to scrape. 
    I don't recommend doing more than 5.
    """))

    http = Http()
    http.GrabPagesOfProductInfo(4)

if __name__ == '__main__':
    main()
    
