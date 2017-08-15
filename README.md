# wdc\_datasource\_rename - datasource\_rename.py
A Python (Python3) script that utilize the Tableau Server REST API to modify the a DataSource Connection's **serverAddress** and **portAddress** to the provided info being passed in the wdc\_datasource\_rename.conf file

## To run the program make sure you have a datasource\_rename.conf setup

* To create one rename the **datasource\_rename.conf.sample** file to **datasource\_rename.conf**
* Modify the following fields in the conf file

		# tableauServer is the name of the Tableau server you want to work with
		tableauServer = https://your.tableau.server.u.want.to.use
		
		# tableauSite is the name of the Site in Tableau you want to work with
		tableauSite = TABLEAU_SITE_YOU_WANT_TO_USE
		
		# logType will help set the type of logging you want for the program
		# You can set to "debug, info, warn, error"
		# If nothing is passed it will be set to info
		logType = debug
		
		# newServerAddress is used to specify the new server address that will be used when the call to
		# change the DataSources connection is made, note that there is no https:// or http:// prefix
		# it's not required
		newServerAddress = address.of.tabserver.you.want.to.change.to
		
		# newPortAddress is used to specify the new port number that will be used when the call to
		# change the DataSources connection is made.
		newPortAddress = port.number
		
*  Run the python script. NOTE: a log file will be generated on first run.

		# Rember this is written for python3 if your default python is not
		# set to use python3 run with **python3 scriptName.py**
		
		python datasource_rename.py

