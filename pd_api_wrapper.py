#! /usr/bin/env python3

import requests
import json
import pprint
from datetime import datetime


class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, status, text):
        self.status = status
        self.text = text

    def __str__(self):
        return "\nAPIError:\nfunction={0}\nstatus={1}".format(self.text, self.status)


class Pipedrive():
    '''
    Pipedrive API wrapper in Python3
    '''

    with open('pd_api_key.txt', 'r') as f:
        API_KEY = f.read().strip()

    def __init__(self):
        pass


    def get_url(self, options):
        '''
        Return well-formed url for API call
        '''
        u = 'https://api.pipedrive.com/v1/'
        u += str(options)
        u += '?api_token=' + self.API_KEY

        return u


    def write_to_log(self, record):
        '''
        Log any changes made to PD records with UTC timestamp.
        '''
        timestamp = datetime.strftime(datetime.utcnow(), '%Y-%m-%dT%H-%M-%S')
        record.insert(0, timestamp)

        with open('log_file.txt', 'a') as text_file:
            text_file.write(', '.join(map(str, record)) + '\n')


    def check_date(date, last_check):
        '''
        Check if update time is later than time of last check.

        Takes:
            date - string
            last_check - datetime object in UTC timezone

        Returns True if update time is after last check
        '''
        # update_time field UTC timezone
        d1 = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

        # check if record update time is later than last data download
        if d1 > last_check:
            return True
        else:
            return False


class Organization(Pipedrive):
    '''
    Actions on Organization objects
    '''
    def __init__(self):
        super().__init__()


    def get_org(self, org_id):
        '''
        Returns the details of a single Organization as a dictionary
        '''
        options = 'organizations/' + str(org_id)
        url = self.get_url(options)
        #print(url)
        resp = requests.get(url)

        if resp.status_code != 200:
            # something went wrong.
            raise APIError(resp.status_code, 'get_org')

        return resp.json()['data']


    def get_all_orgs(self):
        pass


class Person(Pipedrive):
    '''
    Actions on Person objects
    '''
    def __init__(self):
        super().__init__()


    def get_person(self, person_id):
        '''
        Take a PD Person ID and returns all the fields
        associated with this record in a dictionary.
        '''
        options = 'persons/' + str(person_id)
        url = self.get_url(options)

        resp = requests.get(url)

        if resp.status_code != 200:
            raise APIError(resp.status_code, 'get_person')

        return resp.json()['data']


    def get_person_field(self, person_id, field):
        '''
        Take a PD Person ID and field name of interest.

        Returns the value in the field as a string.
        '''
        # need to add error handling for when field is not a key in details.
        details = self.get_person(person_id)

        field = "{}".format(field.replace("'", "").strip())

        if resp.status_code != 200:
            raise APIError(resp.status_code, 'get_person_field')

        return str(details[field])


    def update_person(self, person_id, details_dict):
        pass


class Activity(Pipedrive):
    '''
    Actions on an Activity object
    '''
    def __init__(self):
        super().__init__()


    def add_activity(self, data_dict):
        '''
        Takes a dictionary and uploads it to fields in a new
        Activity record.
        '''
        options = 'activities'
        url = self.get_url(options)
        json_data = json.dumps(data_dict, ensure_ascii=False)

        headers = {'content-type': 'application/json'}

        resp = requests.post(url, data=json_data, headers=headers)

        if resp.status_code == 201:
            message = 'Activity created for org_id {}.'.format(resp.json()['data']['org_id'])
            print(message)
            record = [resp.json()['data']['id'], message, json_data]
            self.write_to_log(record)
        else:
            raise APIError(resp.status_code, 'add_activity')


class Deal(Pipedrive):
    '''
    Actions on an Deal object
    '''
    def __init__(self):
        super().__init__()


    def get_deal(self, deal_id):
        '''
        Take a PD Person ID and returns all the fields
        associated with this record in a dictionary.
        '''
        query = 'https://api.pipedrive.com/v1/deals/'
        query += str(deal_id)
        query += '?api_token=' + API_KEY

        resp = requests.get(query)

        if resp.status_code != 200:
            # something went wrong.
            raise APIError(resp.status_code, 'get_deal')

        return resp.json()['data']


    def get_deals_ids(self):
        # first call of all deals; need to filter this though
        q = 'deals?status=all_not_deleted&start=0&limit=100'

        resp = requests.get(get_url(q))

        data = resp.json()['data']

        limit = 100
        # loop through any remaining records
        # possibly make this a shared method in Pipedrive()
        # for any method where multiple records are returned
        while resp.json()['additional_data'][
                'pagination']['more_items_in_collection']:
            start = resp.json()['additional_data'][
                'pagination']['next_start']

            q = ('deals?status=all_not_deleted&start={}&limit={}').format(start, limit)

            resp = requests.get(get_url(q))
            data += resp.json()['data']

        deals_list = []
        for i in data:
            deals_list.append(i['id'])

        return deals_list


    def update_deal(self, deal_id, deal_details):
        pass


    def get_deals_by_filter(self, filter_id):
        pass
