import requests
import re
import pyjson5
from bs4 import BeautifulSoup

from sv.district import District

LAST_UPDATED = "last_updated"
MEAN = "projected_vote_percentage"
ERROR = "projected_vote_error"
HISTORY_CHART = "electoral_history_chart"
ELECTORAL_HISTORY = "electoral_history"
VOTE_PROJECTION = "vote_projection"
VOTE_PROJECTION_HISTORY = "vote_projection_history"
PROJECTION_CHART = "vote_projection_chart"
PROJECTION_HISTORY_CHART = "vote_projection_history_chart"
CANVASES = {
    ELECTORAL_HISTORY: '<canvas id="histoChart" class="chartjs-render-monitor"></canvas>',
    VOTE_PROJECTION: '<canvas id="graphvotedistrict" class="chartjs-render-monitor"></canvas>',
    VOTE_PROJECTION_HISTORY: '<canvas id="timevotechart" class="chartjs-render-monitor"></canvas>'
}

SCRIPT_IMPORTS = '<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.2/Chart.bundle.js" integrity="sha512-SRW1NuegWCD4fowVB3sUwr2LnLnVAcKTCtYT9z84rskfoqqtIZfEW1iKB0uF1RzvdSbqcVIs6FkONjj5j88RYw==" crossorigin="anonymous" referrerpolicy="no-referrer"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/hammer.js/2.0.8/hammer.js" integrity="sha512-qRj8N7fxOHxPkKjnQ9EJgLJ8Ng1OK7seBn1uk8wkqaXpa7OA13LO6txQ7+ajZonyc9Ts4K/ugXljevkFTUGBcw==" crossorigin="anonymous" referrerpolicy="no-referrer"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-datalabels/0.7.0/chartjs-plugin-datalabels.js" integrity="sha512-yvu1r8RRJ0EHKpe1K3pfHF7ntjnDrN7Z66hVVGB90CvWbWTXevVZ8Sy1p+X4sS9M9Z+Q9tZu1GjGzFFmu/pAmg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-zoom/0.7.5/chartjs-plugin-zoom.min.js" integrity="sha512-zk7yFI526LXuJ2Av7n05jBKslJkqBG8DgLRW8+Eev4xm/lo2v86ZJ78+HQkkFX+9/Rn5jy3YS3CQqqoIQCPR1A==" crossorigin="anonymous" referrerpolicy="no-referrer"></script><script src="https://qc125.com/verticalBar.js"></script><script src="https://qc125.com/moments.js"></script> <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-annotation/0.5.3/chartjs-plugin-annotation.min.js"></script>'

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

def get_last_updated(soup):
    links = soup.find_all('a')
    for link in links:
        if link.get_text().startswith("Last update: "):
            last_updated = link.get_text().split(":")[1].strip()
            break
    return last_updated

def get_vote_projections(soup, properties):
    properties[MEAN] = {}
    properties[ERROR] = {}
    data  = soup.find_all("script")[10]
    parties = get_parties_from_script(data)
    means = get_percentages_from_script(data)
    errors = get_error_from_script(data)
    for i in range(len(parties)):
        properties[MEAN][parties[i]] = means[i]
        properties[ERROR][parties[i]] = errors[i]

def get_electoral_history_chart(data, properties):
    properties[HISTORY_CHART] = data.get_text()

def get_electoral_history_data(data, properties):
    chart_script = data.get_text()
    chart_data_str = chart_script[chart_script.find("var chart"):]
    chart_data_str = chart_data_str[chart_data_str.find("{"):]
    chart_data_str = chart_data_str.rstrip().rstrip(";").rstrip(")")
    p = re.compile("\{\s+label: '(\w+)'[^\[]+\[([^a-zA-Z\]]+)")
    # print(str(data.contents))
    m = p.findall(chart_data_str)
    electoral_history = {}
    for item in m:
        if "min" in item[0] or "max" in item[0]:
            break
        party = item[0]
        # print(party)
        percentages_str = item[1].split(",") 
        percentages_str = percentages_str[1:-1]
        percentages_str = [x.strip() for x in percentages_str]
        for i in range(len(percentages_str)):
            if percentages_str[i] == '':
                percentages_str[i] = "0"
        percentages = [float(x) for x in percentages_str]
        # print(percentages)
        electoral_history[party] = percentages
    # print(electoral_history)
    properties[ELECTORAL_HISTORY] = electoral_history

def get_electoral_history(soup, properties):
    data  = soup.find_all("script")[18]
    get_electoral_history_chart(data, properties)
    get_electoral_history_data(data, properties)

def get_vote_projection_chart(soup, properties):
    data  = soup.find_all("script")[10]
    properties[PROJECTION_CHART] = data.get_text()

def get_vote_projection_history_chart(soup, properties):
    data  = soup.find_all("script")[11]
    properties[PROJECTION_HISTORY_CHART] = data.get_text()

def get_district_info_by_id(district_id):
    # this function returns district information from 338 given a district ID
    url = f"https://338canada.com/{district_id}e.htm"
    r = requests.get(url)
    # print(r.content)
    soup = BeautifulSoup(r.content, 'html5lib')
    properties = {}
    get_vote_projections(soup, properties)
    get_electoral_history(soup, properties)
    get_vote_projection_chart(soup, properties)
    get_vote_projection_history_chart(soup, properties)
    print(properties)
    last_updated = get_last_updated(soup)
    district = District((district_id, properties, last_updated))
    return district

"""
To build a page with the charts, you need to make an HTML file that has
- script imports (SCRIPT_INPORTS variable)
- canvas elements (CANVASES variable)
- scripts with the chart data (HISTORY_CHART for electoral history, PROJECTION_CHART for voting projection chart, PROJECTION_HISTORY_CHART for voting projection history chart)

(the next step is probably to construct the static HTML)
"""