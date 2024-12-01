#IMPORTING REQUIRED LIBRARIES AND MODULES
from urllib.request import urlparse, urljoin
from colorama import init, Fore, Back, Style
from bs4 import BeautifulSoup as bs
from pprint import pprint
from lxml import etree
import validators
import requests
import regex
import time
import os
import re
from art import *

#SETTING APPLICATION
is_debug = False
init(autoreset=True)
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"

#DEFINNNG PAYLOADS
payloads = []
payloads.append(["<script>alert('Hello From XSS Scanner')</script>","<script>alert('Hello From XSS Scanner')</script>"])
payloads.append(["<scr<script>ipt>alert('Hello From XSS Scanner')</scr<script>ipt>","<script>alert('Hello From XSS Scanner')</script>"])
payloads.append(["<img src=x onerror=\"alert('Hello From XSS Scanner');\"","<img src=x onerror=\"alert('Hello From XSS Scanner');\""])
#SETTING UP THE COOKIES
cookies = {}
#HOLD LINKS TO EXCLUDE (DO NOT VISIT)
exclued_url = [];
#HOLD VULNERABLE LINKS APPLIED PAYLOADS
success = []
#DECLARING SOME VARIABLES
start_time = time.time()
internal_urls = set()
external_urls = set()
fuzzable_urls = set()
total_urls_visited = 0
#DEFINNNG FORE COLOURS FOR COLOURFUL TEXT PRINT
GREEN = Fore.GREEN
GRAY = Fore.LIGHTBLACK_EX
RED = Fore.RED
BLUE = Fore.BLUE
WHITE = Fore.WHITE

#PRINT A GIVEN MSG IF DEBUGGING FLAG IS TRUE
def debug(msg):
    if is_debug:
        print(f"{BLUE}[*] {msg}")

#CONFIRM FUNTION
def confirm(msg):
    response = input(f"\n[*] {msg} (Yes or No): ")
    while (not response.lower() == "yes" and not response.lower() == "no" ):
        print(f"{RED}[*] Invalid Choice!")
        response = input(f"\n[*] {msg} (Yes or No): ")
    if(response.lower() == "yes"):
        return True
    else:
        return False

#LOADING SETTINGS FROM SETTINGS.XML FILE
def load_settings():
	global cookies
	global exclued_url
	path = os.path.dirname(os.path.realpath(__file__))
	settings_file = os.path.join(path, 'settings.xml')
	with open(settings_file) as f: 
		xml_content = f.read() 
	xml_content = xml_content.encode('utf-8') 
	xml_root = etree.XML(xml_content) 
	exclue_elements = xml_root.xpath('//settings/excleded/exclude')  
	exclued_url = [e.get('value')for e in exclue_elements]
	cookies_elements = xml_root.xpath('//settings/cookies/cookie')  
	for c in cookies_elements:
		cookies[c.get('name')]=c.get('value')

#CHECKING WEATHER URL IS IN EXCLEDED URL LIST DEFINED IN SETTINGS.XML FLIE
def is_excluded(url):
	global exclued_url
	flag = False
	for end in exclued_url:
		if url.endswith(end):
			flag = True
	return flag

#CHECKING URL VALIDATY
def is_valid_url(url):
    global is_debug
    if '#' in url:
        return False
    if url == "":
        return False
    if is_excluded(url):
        return False
    if (url == None):
        return False
    if (validators.url(url)):
        return True
    else:
        return False

def is_fuzzable(url):
    global fuzzable_urls
    if '=' in url and url not in fuzzable_urls:
        return True;
    else:
        return False

#CREATING ABSOLUTE URL LINK
def create_absolute_href(url,href):
    domain_scheme = urlparse(url).scheme
    if href[0] == '/' or domain_scheme not in href:
        href = urljoin(url, href)
    else:
        href = href
    return href

#FETCHING LINKS IN GIVEN URL
def get_all_website_links(url):
    debug(f"Getting link from url: {url}")
    urls = set()
    hrefs = set()
    domain_name = urlparse(url).netloc
    domain_scheme = urlparse(url).scheme
    soup = bs(requests.get(url,cookies=cookies).content, "lxml")
    iframes = soup.find_all('iframe', src=True)
    anchors = soup.find_all('a', href=True)
    debug(f"{len(iframes)} iframe(s) found")
    for iframe in iframes:
        iframe_url = iframe['src']
        debug(f"   IFrame Src: {iframe_url}")
        hrefs.add(iframe_url)
    debug(f"{len(anchors)} Link(s) found")
    for a in anchors:
        debug(f"   Link: {a['href']}")
        hrefs.add(a['href'])
    for h in hrefs:
        href = create_absolute_href(url,h)
        if href in internal_urls:
            continue
        if not is_valid_url(href):
            continue
        if domain_name not in href:
            if href not in external_urls:
                print(f"{GRAY}[!] External link: {href}")
                external_urls.add(href)
            continue
        if is_fuzzable(href):
            fuzzable_urls.add(href)
            print(f"{RED}[*] Fuzzable link: {href}")
            urls.add(href)
        parsed_href = urlparse(href)
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path  
        if href not in internal_urls:
            print(f"{GREEN}[*] Internal link: {href}")	
            internal_urls.add(href)
            urls.add(href)
    return urls

#CRAWLING URL FOR ALL AWAILABLE LINKS
def crawl(url, max_urls=30):
    debug(f"Crawling Started!")
    global total_urls_visited
    total_urls_visited += 1
    links = get_all_website_links(url)
    for link in links:
        if total_urls_visited > max_urls:
            break
        crawl(link, max_urls)

#FETCHING ALL FORMS IN GIVEN URL
def get_all_forms(url):
    soup = bs(requests.get(url,cookies=cookies).content, "html.parser")
    return soup.find_all("form")

#GETTING FORM INFORMATION
def form_info(form):
    details = {}
    action = form.attrs.get("action").lower()
    method = form.attrs.get("method", "get").lower()
    inputs = []
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value","")
        inputs.append({"type": input_type, "name": input_name,"value":input_value})
    for input_tag in form.find_all("textarea"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value","")
        inputs.append({"type": input_type, "name": input_name,"value":input_value})
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details

#CREATE FORM FROM URL PARAMETERS
def url_to_form(url):
    parsed_href = urlparse(url)
    url = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path  
    details = {}
    action = url
    method = "get"
    query = parsed_href.query
    params = query.split("&")
    inputs = []
    for param in params:
        input_name = param.split("=")[0]
        inputs.append({"type": "text", "name": input_name})
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details

#SUBMITTING FORM DATA  
def submit_data_form(form_details, url, value):
    global cookies
    target_url = urljoin(url, form_details["action"])
    inputs = form_details["inputs"]
    debug(f"Submiting to {target_url}")
    data = {}
    for input in inputs:
        if input["type"] == "text" or input["type"] == "search":
            input["value"] = value
        if input["type"] == "email" :
            input["value"] = "adikhanofficial@gmail.com"
        input_name = input.get("name")
        input_value = input.get("value")
        if input_name and input_value:
            data[input_name] = input_value
    if form_details["method"] == "post":
        debug(f"Sending POST Request on {target_url}")
        response = requests.post(target_url,cookies=cookies, data=data)
    else:
        debug(f"Sending GET Request on {target_url}")
        response = requests.get(target_url,cookies=cookies, params=data)
    return response

#APPLYING XSS IN GIVEN URL USING FORM SUBMITION
def find_xss_in_form(url, payload, forms):
    is_vuln = False
    count = 1
    for form in forms:
        debug(f"Submiting Form {count}")
        form_details = form_info(form)
        content = submit_data_form(form_details, url, payload[0]).content.decode()
        if payload[1] in content:
            debug(f"XSS vulnerability found in form {count}")
            debug(f"Form details:")
            debug(form_details)
            is_vuln = True
        count = count + 1
    return is_vuln

#APPLYING XSS IN URL USING URL PARAMETERS
def find_xss_in_url(url,payload=""):
    is_vuln = False
    form_details = url_to_form(url)
    content = submit_data_form(form_details, url, payload[0]).content.decode()
    if payload[1] in content:
        debug(f"Form details:")
        debug(form_details)
        is_vuln = True
    return is_vuln

#START FORM BASED XSS TEST
def form_base_xss_test(urls):
    for url in urls:
        try:
            print(f"\n{WHITE}[*] Detecting XSS in: {url}")
            forms = get_all_forms(url)
            if (len(forms) == 0):
                print(f"{RED}[*] XSS not detected in {url}")
                debug(f" No Form Found found in {url}")
                continue
            else:
                debug(f"{len(forms)} form(s) found in {url}")
            counter = 0;
            for payload in payloads:
                counter = counter+1
                print(f"{BLUE}[*] Using Payload {counter} '{payload[0]}'")
                if (find_xss_in_form(url,payload, forms)):
                    print(f"{GREEN}[*] XSS detected in {url}")
                    success.append({"url":url,"payload":payload[0]})
                    break
                else:
                    print(f"{RED}[*] XSS not detected in {url}")
        except:
            pass

#START URL BASED XSS TESTING
def url_base_xss_test(urls):  
    for url in urls:
        try:
            print(f"\n{WHITE}[*] Detecting XSS in: {url}")
            counter = 0
            for payload in payloads:
                counter = counter+1
                print(f"{BLUE}[*] Using Payload {counter} '{payload[0]}'")
                if (find_xss_in_url(url,payload)):
                    print(f"{GREEN}[*] XSS detected in {url}")
                    success.append({"url":url,"payload":payload[0]})
                    break
                else:
                    print(f"{RED}[*] XSS not detected in {url}")
        except:
            pass

def main():
    global internal_urls
    global fuzzable_urls
    global is_debug
    global success
    internal_urls = set()
    fuzzable_urls = set()
    success = []
    url = input("\nEnter URL: ")
    while (not is_valid_url(url)):
        print(f"{RED}[*] Invalid Url!")
        url = input("Enter URL: ")
    if(is_fuzzable(url)):
        fuzzable_urls.add(url)
    else:
        internal_urls.add(url)
    load_settings()
    is_debug = confirm("Do you want to turn on debugging?")
    
    if(confirm("Do you want to crawl whole site? ")):
        print(f"{BLUE}[*] Crawling url: {url}")
        crawl(url)

    if(len(internal_urls) > 0):
        print(f"{GREEN}\n[*] {len(internal_urls)} Internal Links found")
    else:
        print(f"{RED}\n[*] No Internal Link Found!")
    if(len(fuzzable_urls) > 0):
        print(f"{GREEN}\n[*] {len(fuzzable_urls)} Fuzzable Links found")
    else:
        print(f"{RED}\n[*] No Fuzzable Link Found!")

    if(len(internal_urls) > 0 and confirm("Do you want to run Form Based XSS on Internal Links")):
        print(f"\n[*] Testing Form Based XSS on {len(internal_urls)} internal links")
        form_base_xss_test(internal_urls)
    if(len(fuzzable_urls) > 0 and confirm("Do you want to run Form Based XSS on Fuzzable Links")):
        print(f"\n[*] Testing Form Based XSS on {len(fuzzable_urls)} Fuzzable links")
        form_base_xss_test(fuzzable_urls)
    if(len(fuzzable_urls) > 0 and confirm("Do you want to run URL Based XSS on Fuzzable Links")):
        print(f"\n[*] Testing URL Based XSS on {len(fuzzable_urls)} Fuzzable links")
        url_base_xss_test(fuzzable_urls)
    if(len(success) > 0):
        print(f"\n{BLUE}[*] {len(success)} Vulnerable Link(s) Found!")
        count = 1;
        for s in success:
            print(f"\n[*] Link: {s.get('url')}")
            print(f"{GREEN}[*] Payload: {s.get('payload')}")
            count += 1
    else:
        print(f"\n{RED}[*] No XSS Vulnerable Link Found!")

if __name__ == "__main__":
    print(f"\n{RED}********************************************************************************")
    tprint("           AdiKhanOfficial\n    XSS Scanner",font="standard")
    print(f"\n{RED}********************************************************************************\n\n")
    main()
    while(confirm("Do you want to Run again? ") == True):
        main()
