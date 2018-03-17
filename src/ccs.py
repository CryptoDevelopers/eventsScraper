from __future__ import print_function
import re
import csv
import pandas as pd
from bs4 import BeautifulSoup
import requests
import html5lib
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


class coinmarketcapScrape:
    def __init__(self):
        return

    def inspectEvent(self, description):
        print(description)
        listing = False
        deliverable = False
        partnership = False
        meetup = False
        if 'listing' in description:
            listing = True

        if 'listed' in description:
            listing = True

        if 'delisting' in description:
            listing = False

        if ('exchange' in description):
            listing = True

        if ('release' in description):
            deliverable = True

        if ('launch' in description):
            deliverable = True

        if ('releases' in description):
            deliverable = True

        if ('roadmap' in description):
            deliverable = True

        if ('road map' in description):
            deliverable = True

        if ('update' in description):
            deliverable = True

        if ('upgrade' in description):
            deliverable = True

        if ('partnership' in description):
            partnership = True

        if ('meetup' in description):
            meetup = True

        if ('meet up' in description):
            meetup = True

        if ('summit' in description):
            meetup = True

        if ('conference' in description):
            meetup = True

        return listing, deliverable, partnership, meetup

    def exportData(self, data):
        return(data.to_csv('eventscalendar.csv', sep=',', encoding='utf-8', index=False))

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'sheets.googleapis.com-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def googleSheets(self):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('calendarscraper.json', scope)
        client = gspread.authorize(creds)

        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        sheet = client.open('Events calendar').sheet1
        with open('eventscalendar.csv') as csv:
            client.import_csv('1MhI2x6at1UkCbVM4WwCRR0PCHv7zNkUzf4zmdezXry4', csv)
        # Extract and print all of the values
        list_of_hashes = sheet.get_all_records()
        print(list_of_hashes)


    # function to fill dataframe for one page
    def filldf(self, soup, pagenum):
        print('fill them dataframes')
        # Get lists ready to fill
        dates = []
        names = []
        symbols = []
        brief = []
        description = []
        validation = []
        votes = []
        date_added = []
        # listing = []
        # deliverable = []
        # partnership = []
        # meetup = []

        for page in range(pagenum):
            eventList = soup[page].find_all('div', {'class': 'content-box-general'})
            for event in eventList:
                try:
                    vote = event.find_all('span', {'class': 'votes'})
                    vote = vote[0].text
                    b = '( votes)'
                    for char in b:
                        vote = vote.replace(char, "")
                    votes.append(vote.encode('utf-8'))
                    print(vote)

                    val = event.find_all('div', {'class': 'progress-bar'})
                    val = val[0].get('aria-valuenow')
                    validation.append(val.encode('utf-8'))
                    print(val)

                    reminder = event.find_all('a', {'class': 'reminder'})
                    date = reminder[0].get('data-date')
                    dates.append(date.encode('utf-8'))
                    print(date)

                    coin = reminder[0].get('data-coin')
                    names.append(coin.encode('utf-8'))
                    print(coin)

                    symbol = re.search('\(([^)]+)', coin).group(1)
                    symbols.append(symbol.encode('utf-8'))
                    print(symbol)

                    title = reminder[0].get('data-title')
                    brief.append(title.encode('utf-8'))
                    print(title)

                    desc = event.find_all('p', {'class': 'description'})
                    desc = desc[0].text
                    desc = desc.encode('utf-8').strip()
                    #desc = desc.replace("\"","")
                    description.append(desc)
                    print(desc)

                    dateAdded = event.find_all('p', {'class': 'added-date'})
                    dateAdded = dateAdded[0].text.encode('utf-8')
                    dateAdded = dateAdded[1:(len(dateAdded) - 1)]
                    dateAdded = dateAdded.replace('Added ','')
                    date_added.append(dateAdded)
                    print(dateAdded)

                    # l,d,p,m = self.inspectEvent(title+' '+desc)
                    # listing.append(l)
                    # deliverable.append(d)
                    # partnership.append(p)
                    # meetup.append(m)

                except Exception as e:
                    print(e)
                    dates.append('')
                    names.append('')
                    symbols.append('')
                    brief.append('')
                    description.append('')
                    validation.append(0)
                    votes.append(0)
                    date_added.append('')
                    # listing.append(False)
                    # deliverable.append(False)
                    # partnership.append(False)
                    # meetup.append(False)
                    continue

            # Obtain links from soup
            # links = event.find_all('a')
            # source = links[2].get('href')
            # eventItem['source'] = source.encode('utf-8')
            # #print(source)

        # turn lists into a dataframe
        db = pd.DataFrame({'Dates': dates,
                           'Name': names,
                           'Symbol': symbols,
                           'Brief': brief,
                           'Description': description,
                           'Votes': votes,
                           'Validation%': validation,
                           'Date Added': date_added
                           # 'Listing': listing,
                           # 'Deliverable':deliverable,
                           # 'Partnership':partnership,
                           # 'Meet-up':meetup
                           })
        db = db[['Dates', 'Name', 'Symbol', 'Brief', 'Description', 'Votes', 'Validation%', 'Date Added']]

        return db

    def main(self):
        print("im in main")
        # number of pages to scrape
        pagenum = 1

        # put scraped pages into a list
        pages = []
        soups = []

        try:
            for n in range(pagenum):
                if n == 0:
                    pages.append(requests.get('https://coinmarketcal.com/'))
                else:
                    pages.append(requests.get('https://coinmarketcal.com/?page=' + str(n + 1)))

                soups.append(BeautifulSoup(pages[n].content, 'html5lib'))

        except Exception as e:
            print("Unable to authenticate: ", e)

        print("Soup requested for first {} pages of coinmarketcal.com".format(pagenum))
        df = self.filldf(soups, pagenum)
        print(df)
        csv = self.exportData(df)

        """Shows basic usage of the Sheets API.

            Creates a Sheets API service object and prints the names and majors of
            students in a sample spreadsheet:
            https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
            """
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)

        spreadsheetId = '1MhI2x6at1UkCbVM4WwCRR0PCHv7zNkUzf4zmdezXry4'
        rangeName = 'A1:B3'
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId, range=rangeName).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
        else:
            print('Name, Major:')
            for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                print(values)


        #self.googleSheets()


if __name__ == '__main__':
    scraper = coinmarketcapScrape()
    scraper.main()
