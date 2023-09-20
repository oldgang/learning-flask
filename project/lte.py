import re
from selenium.webdriver.common.by import By
from .helperFunctions import driver_init
from routeros_api import api, RouterOsApiPool
from routeros_api.exceptions import RouterOsApiCommunicationError
import json

ipv4_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'

def is_valid_ipv4(ip):
    match = re.match(ipv4_pattern, ip)
    if not match:
        return False

    groups = match.groups()

    # ignore addresses that end with .0
    if groups[-1] == '0':
        return False
    
    # WaveX addresses are in the range 10.12.0.1-254
    # if groups[0] != '10' or groups[1] != '12' or groups[2] != '0' or int(groups[3]) > 254:
    #     return False

    return True

def convert_to_megabits(text):
    # bits
    if re.search(r'\d+b$', text):
        value = text[0:-1]
        return float(value)/1000000
    # kilobits
    if re.search(r'\d+Kb$', text):
        value = text[0:-2]
        return float(value)/1000
    # megabits
    if re.search(r'\d+Mb$', text):
        value = text[0:-2]
        return float(value)
    # gigabits
    if re.search(r'\d+Gb$', text):
        value = text[0:-2]
        return float(value)*1000

def filter_data(divs):
    # create empty dictionaries for each period
    daily = {}
    weekly = {}
    monthly = {}
    yearly = {}

    # get average download and upload speeds for each period
    for div in divs:
        title = div.find_element(By.TAG_NAME, 'h3').text
        if "Daily" in title:
            emTagsDaily = div.find_elements(By.TAG_NAME, 'em')
            daily['title'] = title
            daily['averageDownload'] = (emTagsDaily[0].text.split(';')[1]).strip().split(' ')[-1]
            daily['averageUpload'] = (emTagsDaily[1].text.split(';')[1]).strip().split(' ')[-1]
        elif "Weekly" in title:
            emTagsWeekly = div.find_elements(By.TAG_NAME, 'em')
            weekly['title'] = title
            weekly['averageDownload'] = (emTagsWeekly[0].text.split(';')[1]).strip().split(' ')[-1]
            weekly['averageUpload'] = (emTagsWeekly[1].text.split(';')[1]).strip().split(' ')[-1]
        elif "Monthly" in title:
            emTagsMonthly = div.find_elements(By.TAG_NAME, 'em')
            monthly['title'] = title
            monthly['averageDownload'] = (emTagsMonthly[0].text.split(';')[1]).strip().split(' ')[-1]
            monthly['averageUpload'] = (emTagsMonthly[1].text.split(';')[1]).strip().split(' ')[-1]
        elif "Yearly" in title:
            emTagsYearly = div.find_elements(By.TAG_NAME, 'em')
            yearly['title'] = title
            yearly['averageDownload'] = (emTagsYearly[0].text.split(';')[1]).strip().split(' ')[-1]
            yearly['averageUpload'] = (emTagsYearly[1].text.split(';')[1]).strip().split(' ')[-1]

    return [daily, weekly, monthly, yearly]

def calculateUsage(usage):
    # Combine average data usage and set units to Mb
    for period in usage:
        averageDownload = period.pop('averageDownload')
        averageUpload = period.pop('averageUpload')
        averageUsage = convert_to_megabits(averageDownload) + convert_to_megabits(averageUpload)
        period['averageUsageMegabits'] = round(averageUsage, 2)
    
    daily = usage[0]
    weekly = usage[1]
    monthly = usage[2]
    yearly = usage[3]
    usage = {}
    # Calculate data usage for each period
    usage['dailyGigabytes'] = round(daily.pop('averageUsageMegabits') * 24*3600/8 /1000, 2)
    usage['weeklyGigabytes'] = round(weekly.pop('averageUsageMegabits') * 24*3600/8 * 7 /1000, 2)
    usage['monthlyGigabytes'] = round(monthly.pop('averageUsageMegabits') * 24*3600/8 * 30 / 1000, 2)
    usage['yearlyGigabytes'] = round(yearly.pop('averageUsageMegabits') * 24*3600/8 * 365 /1000, 2)
    return usage

# FETCH DATA
def fetch_lte_usage(ip):
    driver = driver_init()
    # FETCH DATA
    try:
        driver.get(f"http://{ip}/graphs/iface/lte1/")
    except:
        driver.quit()
        return None
    
    divs = driver.find_elements(By.CLASS_NAME, 'box')[0:4]
    data = filter_data(divs)
    data = calculateUsage(data)
    driver.quit()
    return data

def fetch_lte_stats(ip):
    connection = RouterOsApiPool(ip, username='dlbot', password='0Fb4EEewAxbQWm7i', plaintext_login=True)
    try:
        api = connection.get_api()
    except:
        print("Couldn't connect to the device.")
        return None

    try:
        lteMonitor = api.get_binary_resource('/interface/lte').call('monitor', {'numbers': b'0', 'once': b' '})
        connection.disconnect()
    except:
        connection.disconnect()
        print("Couldn't get binary resource")
        return None
    
    data = lteMonitor[0]
    keys = data.keys()
    stats = ''
    for key in keys:
        stats += f"{str(key)}: {str(data[key].decode())}\n"
    
    return stats.split('\n')

if __name__ == "__main__":
    ip = '10.12.0.52'
    print(fetch_lte_usage(ip))
    print(fetch_lte_stats(ip))