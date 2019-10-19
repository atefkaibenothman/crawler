import re
from urllib.parse import urlparse
from lxml import etree
from io import StringIO, BytesIO
import time

# You need to "normalize" the links. Normalization includes making them absolute, and getting rid of the fragment part.

# Check to see if the link's been visited before
visited = set()

# Dictionary containing the last time visited of each link
time_visited = dict()

def scraper(url, resp):
    status = resp.status
    error = resp.error
    url = resp.url

    # print("--------")
    # print(status)
    # print(error)
    # print(url)
    # print("----")

    # Politeness. Check if diff is less than 500 miliseconds.
    # This is wrong though. It should just have a delay of 500 miliseconds.
    # Where to put this delay though? In this file??
    current_time = int(round(time.time() * 1000))
    if url in time_visited:
        if current_time - time_visited[url] < 500:
            return []
    time_visited[url] = current_time

    if status != 200 or (status == 200 and resp.raw_response.content == ''):
        return []

    content = resp.raw_response.content
    html = etree.HTML(content)
    result = etree.tostring(html, pretty_print=True, method="html")

    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

# this should be working now
def extract_next_links(url, resp):
    # Implementation requred.
    # passed in the url and response from scraper.
    # find all the links in the html and return a list of them

    urls=[]
    content = resp.raw_response.content
    html = etree.HTML(content)
    for href in html.xpath('//a/@href'):
        if href not in visited:
            urls.append(href)
    return urls

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.netloc not in set(["www.informatics.uci.edu", "www.ics.uci.edu", "www.cs.uci.edu", "www.stat.uci.edu", "www.today.uci.edu/department/information_computer_sciences"]):
            return False
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
