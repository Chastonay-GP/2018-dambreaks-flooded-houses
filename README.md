# 2018-dambreaks-flooded-houses
Modelling topological relationship between dambreaks and flooded houses with NetworkX
Script Geomodeling Version 1.0	23/07/2018

-------------------------------------------------------------------------------------------------------------------------------------

GENERAL USAGE NOTES
-------------------------------------------------------------------------------------------------------------------------------------

- This script serves as a template to simulate different dambreaks of the flow-right-hand side dam of the aare from thun to bern
and estimates, which buildings will be affected by the dambreak in the different time steps.

- The script was developed as a "Geodata analysis and modelling" seminar work - University of Bern.

- The readme contains the prerequisites YOU MUST HAVE to run the code, the set up and contact informations to the developers.


-------------------------------------------------------------------------------------------------------------------------------------

Prerequisites
-------------------------------------------------------------------------------------------------------------------------------------
- Basement - Basic Simulation Environment - ETH Zuerich	(http://www.basement.ethz.ch/)	[Script is written for Version 2.7,
			if you work with a newer version of Basement you have to change the execute code in line 132]	 
- Python Environment (e.g. PyCharm)
- Packages
	- XlsxWriter		(Version 1.0.5)
	- Networkx		(Version 2.1)	
	- matplotlib		(Version 2.2.2)
	- pandas			(Version 0.23.3)
	- numpy			(Version 1.15.0rc2)
	- pyshp			(1.2.12)
	- scipy 			(Version 1.1.0)
				If scipy import problems occur -> Follow the "scipy workaround" at the end of the readme
		
- ESRI ArcGIS Desktop Advanced license
- Source Data Folder "Geomodeling" which structure must not be changed!!!

-------------------------------------------------------------------------------------------------------------------------------------

Setup
-------------------------------------------------------------------------------------------------------------------------------------
1) Open Geomodeling script in a Python-Environment
2) Change the workdir directory in the script ("#Environment") to the path where the "SourceDataFolder <Geomodeling>" is located.
3) Run the script
!  Don't forget to enter the thread number in the python console!



-------------------------------------------------------------------------------------------------------------------------------------

Contact
-------------------------------------------------------------------------------------------------------------------------------------
developers	D. Vogt
		A. Eugster
web site:	-------
E-mail:		andreas.eugster@students.unibe.ch
		dominik.vogt@students.unibe.ch

Copyright 2018 University of Bern. All rights reserved.
Example Program and its use are subject to a license agreement
and are also subject to copyright, trademark, patent and/or other laws.



-------------------------------------------------------------------------------------------------------------------------------------

scipy workaround
-------------------------------------------------------------------------------------------------------------------------------------
1)	Go to "C:Python27/ArcGIS10.X/Lib/site-packages"
2)	Copy the file "desktop10.X.pth"
3)	Paste the file to your project folder of your Python-Environment into the site-packages ("/venv/Lib/site-packges")



