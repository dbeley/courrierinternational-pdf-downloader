import requests
from bs4 import BeautifulSoup
import time
import os
import errno
import configparser
import shutil


temps_debut = time.time()
config = configparser.RawConfigParser()
config.optionxform = str
config.read('config')
cookies = config['COOKIE']
for k, v in cookies.items():
    key = k.strip('"')
    value = v.strip('"')
jar = requests.cookies.RequestsCookieJar()
jar.set(key, value)


def search_mag_in_url(url):
    html_doc = requests.get(url).content
    soup = BeautifulSoup(html_doc, features="lxml")

    for m in soup.find_all("div", class_="view-main-content"):
        for d in m.find_all("article", class_="item"):
            for a in d.find_all("a", href=True):
                url_mag = "https://www.courrierinternational.com{0}".format(
                    a['href'])
                print("URL magazine : {0}".format(url_mag))
                extract_pdf_in_url(url_mag)


def extract_pdf_in_url(url):
    mag_requests = requests.get(url, allow_redirects=True, cookies=jar).content
    mag_soup = BeautifulSoup(mag_requests, features="lxml")
    for d in mag_soup.find_all("div", class_="issue-offers"):
        for a in d.find_all("a", class_="issue-download", href=True):
            print("PDF trouvé")
            url_pdf = a['href'].split("&url=", 1)[1]
            print(url_pdf)
            mag_name = url_pdf.split("magazine/", 1)[1]
            filename = "Exports/{0}/{1}".format(str(year), str(mag_name))
            save_pdf(url_pdf, filename)


def save_pdf(url, filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    pdf_requests = requests.get(url, stream=True, cookies=jar)
    # print(pdf_requests.content)
    with open(filename, 'wb') as f:
        # f.write(pdf_requests.content)
        shutil.copyfileobj(pdf_requests.raw, f)


url_base = "https://www.courrierinternational.com/magazine/"
# year_min = 1990
min_year = 2003
max_year = 2018

for year in range(max_year, min_year, -1):
    print("Année : {0}".format(str(year)))
    url_year = url_base + str(year)
    search_mag_in_url(url_year)

print("Temps d'exécution : %.2f secondes" % (time.time() - temps_debut))
