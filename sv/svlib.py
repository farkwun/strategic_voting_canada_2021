import requests
import re
from bs4 import BeautifulSoup

from sv.district import District

MEAN="projected_vote_percentage"
ERROR="projected_vote_error"

def get_parties_from_script(data):
    p = re.compile('var parties = \[([^\]]*)\]')
    # print(str(data.contents))
    m = p.search(str(data.contents))
    # print(m.groups()[0])
    parties_str = m.groups()[0]
    parties = parties_str.split(",")
    parties = [x.replace("\\", "").replace("'","") for x in parties if x]
    return parties

def get_percentages_from_script(data):
    p = re.compile('var moyennes = \[([^\]]*)\]')
    # print(str(data.contents))
    m = p.search(str(data.contents))
    # print(m.groups()[0])
    means_str = m.groups()[0]
    means = means_str.split(",")
    means = [float(x) for x in means if x]
    return means

def get_error_from_script(data):
    p = re.compile('var moes = \[([^\]]*)\]')
    # print(str(data.contents))
    m = p.search(str(data.contents))
    # print(m.groups()[0])
    errors_str = m.groups()[0]
    errors = errors_str.split(",")
    errors = [float(x) for x in errors if x]
    return errors

def get_electoral_history(soup):
    data  = soup.find_all("script")[18]
    # REMOVE ALL TEH VARIABLE DECLARATIONS BEFORE AND INCLUDING THE CHART, AND CONVERT EVERYTHING TO JSON REMOVING LAST BRACKET
    p = re.compile('var chart = new Chart\(ctx, {')
    m = p.search(str(data.contents))
    print(m.group(0))

def get_district_info_by_id(district_id):
    # this function returns district information from 338 given a district ID
    url = f"https://338canada.com/{district_id}e.htm"
    r = requests.get(url)
    # print(r.content)
    soup = BeautifulSoup(r.content, 'html5lib')
    links = soup.find_all('a')
    for link in links:
        if link.get_text().startswith("Last update: "):
            last_updated = link.get_text().split(":")[1].strip()
            break
    properties = {}
    properties[MEAN] = {}
    properties[ERROR] = {}
    data  = soup.find_all("script")[10]
    parties = get_parties_from_script(data)
    means = get_percentages_from_script(data)
    errors = get_error_from_script(data)
    for i in range(len(parties)):
        properties[MEAN][parties[i]] = means[i]
        properties[ERROR][parties[i]] = errors[i]
    print(properties)
    # print(get_electoral_history(soup))
    district = District((district_id, properties, last_updated))
    return district



# federal vote projection graphic
# vote projection history graphic
# electoral history graphic
# electoral history data points