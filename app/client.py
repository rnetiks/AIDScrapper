import json
import requests
import getpass
from typing import Any, Type, Tuple, Dict
import time

import settings

class AIDScrapper:
    """
    AID Client to make API calls via requests.
    """
    def __init__(self, title, actions):
        
        self.url = 'https://api.aidungeon.io/graphql'

        # Get all settings
        for setting in settings.aid:
            setattr(self, setting, getattr(settings, setting))

        # requests settings
        self.session = requests.Session()
        self.session.headers.update(settings.headers)

        try:
            with open('token.txt') as file:
                key = file.read()
        
        except:
            key = self.get_login_token()
        
        self.session.headers.update({'x-access-token': key})

        adventures = Story(title, action)
        prompt = Scenario(title)

        self.discarded_stories = 0

    def __delete__(self):
        self.session.close()

    def get_object(query):
        query['variables']['input']['searchTerm'] = self.adventures.title

        try:
            res = self.session.post(
                self.url,
                data=json.dumps(
                    query
                )
            )
            if res.status_code > '399' or res.json()['errors']:
                raise AssertionError(f'Error: {[res.status_code, res.json()["errors"]]}')
            res = res.json()
        except requests.exceptions.ConnectionError or requests.HTTPError as e:
            print(e)
            print(e.read())

        result = res['data']
        return result

    def get_stories(self):
        while True:
            print('Getting a page of stories...')
            
            result = get_object(self.stories_query)['user']['search']

            if result:
                for story in result:
                    try:
                        self.adventure.add(story)
                    except ValidationError:
                        self.discarded_stories += 1
                print(f'Got {len(self.adventure)} stories so far')
                self.stories_query['variables']['input']['offset'] = len(self.adventure) + self.discarded_stories
            else:
                print('Looks like there\'s no more.')
                # return discarded stories to 0, since we are done
                self.discarded_stories = 0
                break

    def get_scenarios(self):
        while True:
            self.scenarios_query['variables']['input']['searchTerm'] = name
            print('Getting a page of scenarios...')
            
            result = get_object(self.scenarios_query)['user']['search']

            if len(result):
                for scenario in result:
                    try:
                        self.prompt.add(scenario)
                    except ValidationError:
                        self.discarded_stories += 1
                    if type(scenario['options']) is list:
                        for option in scenario['options']:
                            self.get_subscenario(option['publicId'])
                            # don not count suscens
                            self.discarded_stories -= 1
                            
                print('Got {len(self.prompt)} scenarios so far')
                self.scenarios_query['variables'] \
                                    ['input'] \
                                    ['offset'] = len(
                                                     self.prompt
                                                 ) + self.discarded_stories
            else:
                print('Looks like there\'s no more.')
                self.discarded_stories = 0
                break

    def get_subscenario(self, pubid):
        print(f'Getting subscenario {pubid}...')

        self.subscen_query['variables']['publicId'] = pubid
        
        result = self.get_object(self.subscen_query)['scenario']
        
        result['isOption'] = True
        try:
            self.prompt.add(result)
        except ValidationError:
            # With subscens there is no problem with offset
            pass
        if type(result['options']) is list:
            for option in result['options']:
                self.get_subscenario(option['publicId'])
                self.discarded_stories -= 1

    def get_login_token(self):
        while True:

            self.aid_loginpayload['variables']['identifier'] = \
                self.aid_loginpayload['variables']['email'] = \
                input('Your username or e-mail: ')
            self.aid_loginpayload['variables']['password'] = getpass.getpass('Your password: ')
            try:
                res = self.session.post(
                    self.url,
                    data=json.dumps(
                        self.aid_loginpayload
                    )
                ).json()
                if 'errors' in res:
                    print('Couldn\'t log in.')
                    for error in payload['errors']:
                        print(error['message'])
                        return ''
                elif 'data' in payload:
                    return res['data']['login']['accessToken']
                else:
                    print('no data?!')
            except requests.exceptions.ConnectionError or requests.HTTPError as e:
                print(e)

    def upload_in_bulk(self, stories):
        for scenario in stories['scenarios']:
            res = self.session.post(self.url,
                data=json.dumps(
                    self.create_scen_payload
                 )
            )
            if 'errors' in res:
                raise Exception(res, res.json)
            res = self.session.post(
                self.url,
                data=json.dumps(
                    self.update_scen_payload
                )
            )
            print(f'{scenario["title"]} successfully uploaded..')


class ClubClient:

    def __init__(self):
        self.url = 'https://prompts.aidg.club/'

        # Get all settings
        for setting in settings.club:
            setattr(self, setting, getattr(settings, setting))

        # requests settings
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _post(self, obj_url, params):
        url = self.url + obj_url
        self.session.headers.update(dict(Referer=url))

        params['__RequestVerificationToken'] = self.get_secret_token(url)

        res = self.session.post(url, data=params)
        if res.status_code >= 200:
            print('Successfully registered')
        else:
           print('Uh-oh...', res.text, res.status_code)

    def _get_scenario_tags(self, tags):
        nsfw = 'false'
        tags_str = ', '.join(tag for tag in tags)
        for tag in tags:
            if tag == 'nsfw':
                nsfw = 'true'
        return {'nsfw': nsfw, 'tags': tags_str}

    def get_secret_token(self, url):
        res = self.session.get(url)
        body = bs4.BeautifulSoup(res.text)
        hidden_token = body.find('input', {'name': '__RequestVerificationToken'})
        return hidden_token.attrs['value']

    def make_club_account(self):
        params = {
                 'ReturnUrl': '',
                 'Honey': '',
                 'Username': input('Username: '),
                 'Password': getpass.getpass('Password: '),
                 'PasswordConfirm': getpass.getpass('Password(Again): ')
        }

        res = self._post('user/register/', params)


    def login_into_the_club(self):
        params = {
                 'ReturnUrl': '',
                 'Honey': '',
                 'Username': input('Username: '),
                 'Password': getpass.getpass('Password: ')
        }

        res = self._post('user/login/', params)

    def publish(self, title=''):
        """
        Publish a scenario with the given name to the club.
        """
        print('Already have a club account?')
        print('\n[1] Register')
        print('\n[2] Log-in')

        selection = input('>')
        if selection == '1':
            self.make_club_account()
        elif selection == '2':
            self.login_into_the_club()
        else:
            print('Invalid selection...')
            return
        # variables
        variables = ('?savedraft=true', '?confirm=false#')


        with open('stories.json') as file:
            infile = json.load(file)

        for scenario in infile['scenarios']:
            if scenario['title'] == title or title == '*':
                # prepare the request
                # prepare tags
                tags = self._get_scenario_tags(scenario['tags'])

                try:
                    quests = "\n".join(scenario['quests']['quest'])
                except KeyError:
                    quests = []

                params = {
                    "Honey": "",
                    "Command.ParentId": "",
                    "Command.Title": scenario['title'],
                    "Command.Description": scenario['description'],
                    "Command.PromptContent": scenario['prompt'],
                    "Command.PromptTags": tags['tags'],
                    "Command.Memory": scenario['memory'],
                    "Command.Quests": quests,
                    "Command.AuthorsNote": scenario['authorsNote'],
                    "Command.Nsfw": tags['nsfw'],
                    "ScriptZip": "",#filename
                    "WorldInfoFile": "",#filename
                }
                # prepare WI
                counter = 0
                try:
                    for wi_entry in scenario['worldInfo']:
                        params[f'Command.WorldInfos[{counter}].Keys'] = wi_entry['keys']
                        params[f'Command.WorldInfos[{counter}].Entry'] = wi_entry['entry']
                        counter+=1
                except KeyError:
                    pass

                res = session.post(variables[1], params)

                print(f'Your prompt number is {res.url.split("/")[-1]}')
                # I don't want to overload his servers...
                time.sleep(1)


if __name__ == '__main__':
    pass

