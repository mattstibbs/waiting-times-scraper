from bs4 import BeautifulSoup
import requests
import re
import pprint
import datetime
from CapacitySnapshot import CapacitySnapshot

pp = pprint.PrettyPrinter(indent=4)

url = 'https://www.midyorks.nhs.uk/ae-waiting-times'
print(f"Scraping {url} for live capacity data...")
r = requests.get(url)
data = r.text

soup = BeautifulSoup(data, "html.parser")

capacity_list = soup.find("ol", {"class": "live-service-data-list"})

for item in capacity_list.find_all("li", {"class": "list-content-item"},
                                   recursive=False):
    data_item = {
        "service_name": item.header.h3.text,
        "last_updated": item.header.p.text
    }
    item_list = item.article.ol.find_all("li", {"class": "data-item"})

    for item in item_list:
        data_item[item.div.header.h4.text] = item.div.article.p.text

    m = re.match("(?P<hours>\A\d{1,2})(?:\s(?:Hour|Hours)\s)(?P<mins>\d{2})",
                  data_item['Current longest waiting time to see a doctor'])
    waiting_time_mins = (int(m.groups()[0]) * 60) + int(m.groups()[1])

    data_item['longest_waiting_time_mins'] = waiting_time_mins
    data_item.pop('Current longest waiting time to see a doctor')

    data_item['patients_waiting_for_clinician'] = \
        int(data_item.pop('Patients waiting to see a Doctor/Nurse practitioner'))

    data_item['number_of_patients_in_dept'] = \
        int(data_item.pop('Number of patients in department'))

    pp.pprint(data_item)

    cap_snap = CapacitySnapshot(data_item['service_name'],
                                waiting_time_mins=data_item['longest_waiting_time_mins'],
                                pts_waiting=data_item['patients_waiting_for_clinician'],
                                pts_in_dept=data_item['number_of_patients_in_dept'])

    print(cap_snap)
    print(cap_snap.waiting_time_mins)
    print(cap_snap.patients_in_dept)

    if cap_snap.name == 'Pinderfields':
        service_id = '1311694098'
    elif cap_snap.name == 'Pontefract':
        service_id = '1334238418'
    elif cap_snap.name == 'Dewsbury':
        service_id = '1339681046'

    last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    post_data = {
        "serviceId": service_id,
        "numberOfPatientsWaiting": cap_snap.patients_waiting,
        "currentWaitingTime": cap_snap.waiting_time_mins,
        "lastUpdated": last_updated
    }

    headers = {'capacity.service.api.username': 'a2si-capacity-user',
               'capacity.service.api.password': 'AyTooEssEye'}

    p = requests.post('https://www.bjss-nhsd-capacityservice.co.uk/capacity',
                      json=post_data,
                      headers=headers
                      )

    print(p.status_code)
