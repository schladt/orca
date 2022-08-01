# ORCA

| ![space-1.jpg](https://user-images.githubusercontent.com/12025382/182262267-afee2857-844d-45ee-b25d-e3d1c9db992b.png) |
|:--:|
| ORCA Image by Vectorportal.com, CC BY |


- The Open aRtifact Classification and Analysis (ORCA) framework is a system that enables both cyber security analysts and researchers to perform data mining tasks on data collected from vast repositories of malicious artifacts. 
- The system is designed to be both modular and extensible. Each component of the system can be replaced or expanded to fit the organizational needs of the customer. 
- Cyber security analysts and operators utilize the efficient search and data exploration features of ORCA to quickly identify similar samples to an unknown target sample and discover candidates for detection rule creation. 
- Data scientists utilize ORCA to create classification models to identify malware families, determine sample disposition, and other arbitrary data mining tasks. 
- Performance evaluations of ORCA have shown it is a viable framework for creating meaningful classification models. In test, we were able to predict a sample’s disposition with 93% accuracy. This level of accuracy is significant in real world applications where static signature do not exist.
- Future work for the ORCA project will include developing a production environment, integrating standards such as STIX/TAXII protocols and developing many additional machine learning models.

![image](https://user-images.githubusercontent.com/12025382/182262631-724929b7-8c05-4f1f-bd89-fd64b907e78e.png)


![image](https://user-images.githubusercontent.com/12025382/182262618-7a2b17c4-e3ed-4917-8f43-b0c51e33159f.png)

| File Name |	Description |
| collect_clean.py | Utility script to collect clean binaries from a Windows OS |
collect_vx.py	Utility script to collect malware samples from VX underground
data-mining.ipynb	Jupyter Notebook with data mining example
docker-compose.yml	Docker compose file for running postgresql development server
features.pkl	Binary dataset used in data mining example
features.py	Default feature extraction script
requirements.txt	Python package requirements
submit_clean.py	Utility script to manage submission of benign files to CAPE
submit_vx.py	Utility script to manage submission of XV underground files to CAPE
tag_cape.py	Creates ORCA tags from CAPE JSON reports 
app/__init__.py 	Flask application factory file
app/artifact.py	Flask blueprint for artifact view
app/dashboard.py	Flask blueprint for dashboard view
app/database.py	Helper functions for managing database connection and session
app/mappings_cape.py	SQLAlchemy models for CapeAnalysis
app/mappings_orca.py	SQLAlchemy models for Artifact and Tag tables 
app/search.py	Flask blueprint for search view
app/setting.py	Contains secrets and settings used by ORCA (dummy values in public repo should be changed)
app/tag.py	Flask blueprint for tag view
app/templates/artifact.html	HTML template for artifact page
app/templates/base.html	Base HTML template (layout)
app/templates/dashboard.html	HTML template for dashboard page
app/templates/tag.html	HTML template for tag page
