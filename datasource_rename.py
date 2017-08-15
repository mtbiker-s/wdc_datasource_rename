#!/usr/bin/python3

import requests
import json
import getpass
from configparser import ConfigParser
import logging

from tableau_rest_util import Util


class RenameDataSourceConnection:
    """
    This class is used for renaming Tableau DataSources utilizing Tableau's REST API
    The call's to this REST API are being done with JSON in this class.
    """

    def __init__(self):
        """
        Provides the constants for the program
        """

        self.util = Util()

        self.config = ConfigParser()
        # Read data from .conf file
        self.config.read('datasource_rename.conf')
        self.tableauSection = 'tableau'
        logType = self.config.get(self.tableauSection, 'logType')
        loggingType = self.setLogType(logType)

        # Logging piece
        # Start
        # create logger with 'spam_application'
        self.logger = logging.getLogger('datasource_rename.RenameDataSourceConnection()')
        self.logger.setLevel(loggingType)
        # create file handler which logs even debug messages
        fh = logging.FileHandler('datasource_rename.log')
        fh.setLevel(loggingType)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(loggingType)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        # End

        # Set TableauServer info from conf file
        self.tableauServer = self.config.get(self.tableauSection, 'tableauServer')
        self.tableauSite = self.config.get(self.tableauSection, 'tableauSite')

        self.tableauServerUrl = self.tableauServer + '/api/' + self.config.get(
            self.tableauSection,
            'apiVersion') + '/'
        self.headers = {'Content-Type': 'application/json'}
        self.headers['Accept'] = 'application/json'

    def setLogType(self, loggingType):

        if 'info' in loggingType or 'INFO' in loggingType or 'Info' in loggingType:
            return logging.INFO
        elif 'debug' in loggingType or 'DEBUG' in loggingType or 'Debug' in loggingType:
            return logging.DEBUG
        elif 'warn' in loggingType or 'WARN' in loggingType or 'Warn' in loggingType:
            return logging.WARN
        else:
            return logging.INFO

    def getSignInResponse(self, userName, passwd):
        """
        Provides a request that contains the JSON response after you logged in.
        From this you can get various values like authorization token and site id that are
        utilized int the Tableau REST API calls to perform actions on Tableau Server
        :return:
        """
        apiCallUrl = self.tableauServerUrl + 'auth/signin'
        payload = {'credentials': {'name': userName, 'password': passwd,
                                   'site': {'contentUrl': self.tableauSite}}}
        data = json.dumps(payload)

        req = requests.post(apiCallUrl, headers=self.headers, data=json.dumps(payload))

        return req

    def getAuthToken(self, request):
        """
        Provides the authorization token you can use to perform actions with the Tableau REST API
        :param request:
        :return:
        """
        authToken = request.json()['credentials']['token']

        return authToken


    def getSiteId(self, request):
        """
        Provides the Site ID collected from the request provided
        :param request:
        :return:
        """
        siteId = request.json()['credentials']['site']['id']
        self.logger.info("Site ID: " + siteId)
        return siteId

    def queryDataSources(self, siteId, authToken):
        """
        Provides a Dictionary of DataSources from the siteId being passed
        :param siteId:
        :param authToken:
        :return:
        """
        apiCallUrl = self.tableauServerUrl + 'sites/' + siteId + '/datasources'

        req = requests.get(apiCallUrl, headers=self.headers)

        totalDataSourcesAvailable = req.json()['pagination']['totalAvailable']
        self.logger.info("Total DataSources Available : " + totalDataSourcesAvailable)
        self.logger.debug("All DataSource info")
        self.logger.debug(req.json())
        if int(totalDataSourcesAvailable) > 0:
            dataSource = req.json()['datasources']['datasource']
            self.logger.debug("Just the info for the DataSource")
            self.logger.debug(dataSource)

            return dataSource
        else:
            self.logger.info("")
            self.logger.info("There are no DataSources available under the ")
            self.logger.info("Site : " + self.tableauSite)
            self.logger.info("Tableau Server : " + self.tableauServer)
            self.logger.info("to process.")
            self.util.signOutFromTableauServer(authToken,self.tableauServer, self.tableauServerUrl, self.tableauSite, self.logger)
            self.logger.info("Exiting program...")
            exit()

    def queryDataSourceConnections(self, siteId, authToken, dataSource):
        """
        Provides a List made up of wdc dictionaries that contain information
        about the the dataSources but the wdc dictionaries contain the connectionId's
        and the serverAddress and serverPorts
        :param siteId:
        :param authToken:
        :param dataSource:
        :return:
        """

        wdcList = []
        for data in dataSource:
            self.logger.info('Getting connection id for ' + data['contentUrl'])
            apiCallUrl = self.tableauServerUrl + 'sites/' + siteId + '/datasources/' + data['id'] + '/connections'
            req = requests.get(apiCallUrl, headers=self.headers)

            self.logger.debug("Data for connections")
            self.logger.debug(req.json())

            wdc = {}
            wdc['contentUrl'] = data['contentUrl']
            wdc['siteId'] = siteId
            wdc['dataSourceId'] = data['id']
            wdc['connectionId'] = req.json()['connections']['connection'][0]['id']
            wdc['serverAddress'] = req.json()['connections']['connection'][0]['serverAddress']
            wdc['serverPort'] = req.json()['connections']['connection'][0]['serverPort']

            wdcList.append(wdc)

        return wdcList

    def updateDataSourceConnections(self, authToken, wdcConnections, newServerAddress, newPortNumber):

        for wdc in wdcConnections:
            existingWDC = wdc['contentUrl']
            existingServerAddress = wdc['serverAddress']
            existingPortNumber = wdc['serverPort']

            if newServerAddress is not existingServerAddress and newPortNumber is not existingPortNumber:
                self.logger.info("")
                self.logger.info("Attempting to do a DataSource Connection Update on WDC " + existingWDC)
                self.logger.info(
                    "Existing server address : " + existingServerAddress + ", existing port number : " + existingPortNumber)
                self.logger.info("Replacing with the following :")
                self.logger.info("New server address : " + newServerAddress)
                self.logger.info("New port address : " + newPortNumber)

                apiCallUrl = self.tableauServerUrl + 'sites/' + wdc['siteId'] + "/datasources/" + wdc[
                    'dataSourceId'] + '/connections/' + wdc['connectionId']

                payload = {
                    'connection': {'serverAddress': newServerAddress, 'serverPort': newPortNumber, 'userName': '',
                                   'password': '', 'embedPassword': 'False'}}

                self.logger.debug('This debug output will create a curl call you can use to try send this via curl')
                self.logger.debug(
                    "curl -H 'Content-Type: " + self.headers['Content-Type'] + "' -H 'Accept: " + self.headers[
                        'Accept'] + "' -H 'X-tableau-auth: " + self.headers['X-tableau-auth'] + "' "
                    + "-X PUT -d '" + json.dumps(payload) + "' " + apiCallUrl)

                try:
                    req = requests.put(apiCallUrl, headers=self.headers, data=json.dumps(payload))
                    if req.status_code != 200:
                        self.logger.warning("Could not update DataSource Connection")
                        self.logger.warning(req.json())
                    else:
                        self.logger.info("Updated the DataSource Connections successfully!")
                except:
                    self.logger.warning("Something went wrong")
                    self.logger.error(req.json())

            else:
                self.logger.info("")
                self.logger.info("No need to update.")
                self.logger.info(
                    "Existing server address " + existingServerAddress + " is the same as the new server address " + newServerAddress)
                self.logger.info(
                    "Existing port number " + existingPortNumber + " is the same as the new port number " + newPortNumber)


    def main(self):

        self.logger.info("")
        self.logger.info(
            "Program will run a DataSource Update of connection parameters  on specified Tableau Server for all WDCs")
        self.logger.info("Would you like to continue?")

        answer = input("Enter 'y' for Yes or 'n' for No: ")
        self.logger.info("Response = " + answer)

        if answer is 'y' or answer is 'Y':

            self.logger.info("")
            self.logger.info("Tableau Server : " + self.tableauServer)
            self.logger.info("Tableau Site : " + self.tableauSite)

            creds = self.util.login()
            self.logger.info("Ran by : " + creds['username'])

            req = self.getSignInResponse(creds['username'], creds['pass'])

            authToken = self.getAuthToken(req)
            self.logger.debug("AuthToken = " + authToken)

            siteId = self.getSiteId(req)

            # Add Tableau-Auth Header
            self.headers['X-tableau-auth'] = authToken

            dataSources = self.queryDataSources(siteId, authToken)

            wdcDataSourceConnections = self.queryDataSourceConnections(siteId, authToken, dataSources)

            # This section here will do all of the data source connection updates
            dataSourcesSection = 'dataSources'
            newServerAddress = self.config.get(dataSourcesSection, 'newServerAddress')
            newPortAddress = self.config.get(dataSourcesSection, 'newPortAddress')
            self.updateDataSourceConnections(authToken, wdcDataSourceConnections, newServerAddress, newPortAddress)

            # Signing out once all calls have completed
            self.util.signOutFromTableauServer(authToken, self.tableauServer, self.tableauServerUrl,
                                               self.tableauSite, self.logger)
        else:
            self.logger.info("Exiting program...")


if __name__ == '__main__':
    RenameDataSourceConnection().main()
