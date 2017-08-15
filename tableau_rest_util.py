#!/usr/bin/python3

import requests
import getpass


class Util:

    def login(self):
        """
        Provides a dictionary with a username and pass collected from user input
        :return:
        """

        user = input("username: ")
        passwd = getpass.getpass("password: ")

        assert user != "", 'username cannot be blank!'
        assert passwd != "", 'password cannot be blank!'

        creds = {}
        creds['username'] = user
        creds['pass'] = passwd

        return creds

    def signOutFromTableauServer(self, authToken, tableauServer, tableauServerUrl, tableauSite, logger):
        """

        :param authToken:
        :param headers:
        :param tableauServer:
        :param tableauServerUrl:
        :param tableauSite:
        :param logger:
        :return:
        """

        """
        Used to sign out from tableau server when transactions are done
        :param authToken:
        :return:
        """

        apiCallUrl = tableauServerUrl + 'auth/signout'
        headers = {'X-tableau-auth': authToken}

        req = requests.post(apiCallUrl, data=b'', headers=headers)


        if req.status_code == 204:
            logger.info("")
            logger.info("Closing connection to Tableau Server " + tableauServer + ", site " + tableauSite)
        else:
            logger.error(req.json())