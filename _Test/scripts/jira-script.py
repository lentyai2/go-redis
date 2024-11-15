import requests
import json
import csv
from datetime import datetime

# "https://nabancard.atlassian.net/rest/api/2/search?jql=project='PaymentsHub - Integrations'&ORDER%20BY%20Created&maxResults=100&startAt=" +
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Basic cmlvcmRhY2hlQG5hYmFuY2FyZC5jb206UEpWWmNBT2xiNE10SGNISlJmOVJFRkQy"
}

with open('seed-data.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(row["Ticket"])
        # date = datetime.strptime(row["Date"], '%m/%d/%y')
        # print(type(date.text))
        # products_array = row["Products discussed"].split(",")
        # products = []
        # for item in products_array:
        #     obj = {}
        #     obj['value'] = item
        #     products.append(obj)
        # print(products)
        # post_payload = {
        #     "fields": {
        #         "project":
        #         {
        #             "key": "INT"
        #         },
        #         "summary": "Discovery Call - " + row['Company'],
        #         "issuetype": {
        #             "name": "Meeting"
        #         }
        #     }
        # }
        # post_response = requests.request(
        #     "POST",
        #     "https://nabancard.atlassian.net/rest/api/2/issue",
        #     headers=headers,
        #     data=json.dumps(post_payload)
        # )
        # response = post_response.json()
        # print(response["key"])
        # get_response = requests.request(
        #     "GET",
        #     "https://nabancard.atlassian.net/rest/api/2/issue/" +
        #     response["key"],
        #     headers=headers
        # )
        # print("GET: ====> " + get_response.text)
        # --------------------------------------------------------------
        # Primary Sales Contact: customfield_13481: row["salesAgent"],
        # Company: customfield_13828: row['company'],
        # Sales Group: customfield_13909: row['salesGroup'] {"Dropdown - ISV Sales"|"Inside Sales (Merchant / DAG)"|"Outside Sales (NSG: Agent / ISO)"|"NAB Subsidiary (Other NAB)"|"Other (see notes)"},
        # 3rd Party Agent: customfield_13910: row["thirdPartyAgent"] {"yes|no"},
        # Created: customfield_13911: row["dateCreated"] "yyyy-mm-dd",
        # Meeting type: customfield_13912: row['meetingType'] {"Initial Discovery"|"Follow-up Discovery"|"Troubleshooting"},
        # Products discussed: customfield_13915: Array of Objects: [{"value": row["products"]}] {"BigCommerce"|"Business Reporting API"|"Custom Pay API"|"EPX Hosted Checkout"|"EPX Hosted Pay Page"|"Gateway Pay API"|"Gateway Pay Page"|"Hospitality API"|"iFrame JavaScript SDK"|"Ingenico SI API"|"Invoicing API"|"MagTek Mobile SDK"|"Merchant Boarding API"|"PAX SI SDK"|"Payanywhere Mobile SDK"|"Payanywhere Semi-Integrated Web API"|"Server Post API"|"WooCommerce Plugin"|"Other (see notes)"}
        # --------------------------------------------------------------
        product = {}
        if row["Products discussed"]:
            product = {"value": row["Products discussed"]}
        put_payload = {
            "fields": {
                # "customfield_13481": row["salesAgent"],
                # "customfield_13828": row['company'],
                # "customfield_13909": {
                #     "value": row['salesGroup']
                # },
                # "customfield_13910": {
                #     "value": row["thirdPartyAgent"]
                # },
                # "customfield_13911": row['dateCreated'],
                # "customfield_13912": {
                #     "value": row['meetingType']
                # },
                # "customfield_13915": [product],
                # "reporter": {
                #     "self": "https://nabancard.atlassian.net/rest/api/2/user?accountId=617032f9062f4c0069417257",
                #     "accountId": "617032f9062f4c0069417257",
                #     "emailAddress": "ommcdowell@nabancard.com",
                #     "avatarUrls": {
                #         "48x48": "https://secure.gravatar.com/avatar/906ffbfe1ad0998daccbf7b820aace5b?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FOM-3.png",
                #         "24x24": "https://secure.gravatar.com/avatar/906ffbfe1ad0998daccbf7b820aace5b?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FOM-3.png",
                #         "16x16": "https://secure.gravatar.com/avatar/906ffbfe1ad0998daccbf7b820aace5b?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FOM-3.png",
                #         "32x32": "https://secure.gravatar.com/avatar/906ffbfe1ad0998daccbf7b820aace5b?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FOM-3.png"
                #     },
                #     "displayName": "Olivia-Mei McDowell",
                #     "active": True,
                #     "timeZone": "America/New_York",
                #     "accountType": "atlassian"
                # },
                "customfield_13884": {
                    "value": "Dev"
                }
            }
        }
        print(json.dumps(put_payload))
        put_response = requests.request(
            "PUT",
            "https://nabancard.atlassian.net/rest/api/2/issue/" +
            row["Ticket"],
            headers=headers,
            data=json.dumps(put_payload)
        )
        print("PUT RESPONSE: ===> " + row["Ticket"])


print('Done!')
