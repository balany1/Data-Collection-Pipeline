import argparse
import boto3 
from cgitb import text
import json
from lib2to3.pgen2.pgen import DFAState
import logging
import numpy as np
from numpy import append
import os
import pandas as pd
from psycopg2 import errors
from requests import request
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlite3 import ProgrammingError
import time
from tracemalloc import start
from traitlets import Bool
import urllib
import urllib.request
import uuid
from webdriver_manager.chrome import ChromeDriverManager


class Scraper:

    """Scrapes driver, team and champions data from the given website.

    Args:
        URL(str): The URL of the F1 statistics website containing the data
        driver: The webdriver used to access the webpage
        parent_dir: The parent directory of where the raw data is to be stored

    Returns:
        A dictionary of nested dictionarys for each driver and team and a dictionary for championship data for each year

    """

    def __init__(self, URL : str, parent_dir : str, headless: bool = False):

        
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        USER = 'postgres'
        DATABASE = 'Formula1'
        

        if headless:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            chrome_options.headless = True
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        else:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())

        #make connection to specified database
        self.engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
        logging.basicConfig(filename="scraperlog.log",format="%(asctime)s - %(levelname)s - %(message)s")

        self.parser = argparse.ArgumentParser(description='Decide what statistics to scrape')
        self.parser.add_argument('-d','--drivers', default=False, action='store_true', help='Scrape Drivers:True/False')
        self.parser.add_argument('-t', '--teams', default=False, action='store_true', help='Scrape Teams:True/False')
        self.parser.add_argument('-c', '--championships', default=False, action='store_true', help='Scrape Championships:True/False')
        self.parser.add_argument('-l', '--circuits', default=False, action='store_true', help='Scrape Circuits:True/False')
        self.args = self.parser.parse_args()
        self.URL = URL
        self.driver_list=[]
        self.teams_list= []
        self.champs_list = []
        self.circuit_list = []
        self.dict_entry = {}
        directory = "."
        path = os.path.join(parent_dir, directory)
        if os.path.exists(path) == False:
            raw_data = os.mkdir(path)
        try:
            self.__load_and_accept_cookies()
        except NoSuchElementException as NSE:
            logging.error(NSE)
            pass
        
    def __load_and_accept_cookies(self) -> None:

        """Opens the site and accepts cookies"""
        
        self.driver.get(self.URL)
        accept_button = self.driver.find_element(by=By.XPATH, value="//*[@class='btn btn-success acceptGdpr']")
        accept_button.click()
        
    def navigate_drivers(self):

        """Navigates to the list of F1 drivers and calls the get_driver_data method to begin scraping the data for each driver"""

        self.driver.get(self.URL) 
        navbar = self.driver.find_element(by=By.XPATH, value="//div[@class='navbar-nav']").find_element(by=By.LINK_TEXT, value = 'Drivers').click()

    def __get_image(self):

        """Method that is called within get_driver_data that locates the element containing the drivers image and calls the function to download the image"""
        if os.path.exists("./driver_images") == False:
            raw_data = os.mkdir("./driver_images")
        img_src = self.driver.find_element(by=By.XPATH, value="//img[@class='col-md-3']").get_attribute('src')
        self.__download_image(img_src, "./driver_images/", self.__get_driver_name())
    
    def get_no_of_pages(self,default_len : int , title : str):

        """Scrapes URL for each driver/team/championship year
        
        Args:
            default_len:   The length of the full_list of drivers if required
            
        Returns:
            no_of_pages: The number of pages requested by the user   
        """
        valid = False
        while not valid:  
            no_of_pages = input(f'Please select how many {title} you wish to collect data for(for all data, please select 0:') 
            try:
                no_of_pages = int(no_of_pages)
                valid = True
            except ValueError:
                print('Please enter an integer value')
                continue

        if no_of_pages == 0:
            no_of_pages = default_len
        elif no_of_pages > default_len:
            no_of_pages = default_len
        return no_of_pages

    def __find_elements(self, element : str):

        column_data = self.driver.find_elements(by=By.XPATH, value= element)
        for i in range(0,len(column_data),2):
                    entry = self.__edit_multiple_occurrences(column_data[i+1].text)
                    if entry.isdigit():
                        entry = int(entry)
                    else:
                        entry = entry
                    self.dict_entry[column_data[i].text] = entry

    def __get_URL_list(self, element : str , title : str):

        """Scrapes URL for each driver
        
        Args:
            element(str):   References the necessary element on the webpage that contains the required data
            
        Returns:
            url_list(list): List of URLS for each driver that can then be looped through to scrape data    
        """
        title = title
        url_list = []
        
        starting_letter_tag = self.driver.find_elements(by=By.XPATH, value=element)
        default_len = len(starting_letter_tag)

        no_of_pages = self.get_no_of_pages(default_len, title)

        for pilot in starting_letter_tag[:no_of_pages]: #collects all the drivers URLS in a list

            link = pilot.find_element(By.TAG_NAME, 'a')
            a_tag = link.get_attribute('href')
            url_list.append(a_tag)

        return url_list
        
    def __download_image(self : str, url : str, file_path : str, file_name : str):

        """Downloads the image located in get_image to the required location
        
        Args:
            url:       Webpage containg the required image
            file_path: Gives the path of where the image is downloaded to
            file_name: Names the file in a Forename_Surname format by calling get_driver_name  
        """

        full_path = file_path + file_name + '.jpg'
        urllib.request.urlretrieve(url, full_path)

    def __stripF1_text(self, tobereplaced : str):

        """Reformats the Name of the Driver/Team without any unneccessary text
        
        Args:
            toberreplaced(str):   Unnecessary text to be reformatted
            
        Returns:
            Name(str): Name in required format
        """
        Name = self.driver.find_element(by=By.XPATH, value="//h1[@class='page-title']").text.replace(tobereplaced, "")
        return Name
    
    def __edit_multiple_occurrences(self, entry: str):
        location_of_X = entry.find("X")
        if location_of_X != -1:
            return entry.replace(entry[(location_of_X)-1:len(entry)],"")
        else:
            return entry

    def __get_driver_name(self) -> str: 

        """Splits Driver Name string into Forename and Surname and store as variables to be able to add to driver dictionary/use for filename for image
        
        """
        
        Name = self.__stripF1_text("Formula 1 Driver")
        driver_forename = Name.split()[0]
        driver_surname = " ".join(Name.split()[1:len(Name.split())-3])

        self.dict_entry["Driver First Name"] = driver_forename
        self.dict_entry["Driver Second Name"] = driver_surname
        return driver_forename + "_" + driver_surname

    def get_driver_data(self):

        """Scrapes data for each driver and stores in a dictionary with a unique reference 
        
        """
        
        #creates directory for driver data
        self.__create_dir("driver_data")

        #find element containing individual driver URLS
        url_list = self.__get_URL_list("//div[@class='col-sm-6 col-md-4']","drivers")
        driver_count = 0

        for link in url_list: #loops through every URL in the list and scrapes the statistics
            
            #resets the dictionary entry to blank at the beginning of each URL
            self.dict_entry={}
            self.dict_entry["ID"] = uuid.uuid3(uuid.NAMESPACE_URL, link).hex
            driver_count = driver_count + 1
            self.dict_entry["driver number"] = driver_count
            #opens each URL in the list
            self.driver.get(link)

            self.__get_driver_name() #gets the Drivers Name and splits it into First name, Surname
            self.__get_image()

            #scrapes the data from the different columns, use try except here
            column1_data = self.__find_elements("//div[@class='col-md-6']//td")
            column23_data = self.__find_elements("//div[@class='col-md-3']//td")

            #add each entry as a nested list
            self.driver_list.append(self.dict_entry)

        #dump to json file
        self.__dumptojson(self.driver_list, "./driver_data.json")

    def navigate_teams(self):

        """Navigates to the list of F1 teams and calls the get_team_data method to begin scraping the data for each team"""

        self.driver.get(self.URL)
        navbar = self.driver.find_element(by=By.XPATH, value="//div[@class='navbar-nav']").find_element(by=By.LINK_TEXT, value = 'Teams').click()

    def __get_team_name(self):

        """Reformats the Name of the Team without any unneccessary text
        
        """
        
        Team_Name = self.__stripF1_text("Formula 1")
        self.dict_entry["Team Name"] = Team_Name
        
    def get_team_data(self):

        """Scrapes data for each driver and stores in a dictionary with a unique reference 
        
        """

        #creates directory for team data
        self.__create_dir("team_data")

        #find element containing individual driver URLS
        url_list = self.__get_URL_list("//div[@class='col-sm-6 col-md-4']", "teams")

        team_count = 0
            
        #loops through every URL in the list and scrapes the statistics
        for link in url_list: 
            
            #resets the dictionary entry to blank at the beginning of each URL
            self.dict_entry={}
            self.dict_entry["ID"] = uuid.uuid3(uuid.NAMESPACE_URL, link).hex
            team_count = team_count + 1
            self.dict_entry["Team number"] = team_count

            #opens each page in the list of URLs
            self.driver.get(link)

            #gets the Drivers Name and strips the "Formula 1" from it
            self.__get_team_name() 

            #scrape the data from the different tables on each page
            team_history_data = self.__find_elements("//div[@class='table-responsive']//tbody[@itemtype='http://schema.org/SportsTeam']//td")
            team_driver_data = self.__find_elements("//div[@class='col-md-6']//td")
            team_data = self.__find_elements("//div[@class='col-md-5']//td")
            
            
            #add each entry as a nested dictionary
            self.teams_list.append(self.dict_entry)

        #dump to json file
        self.__dumptojson(self.teams_list, "./teams_data.json")

    def navigate_champs(self):

        """Navigates to the list of F1 champions and calls the get_champs_data method to begin scraping the data for each championship year"""

        self.driver.get(self.URL)
        navbar = self.driver.find_element(by=By.XPATH, value="//div[@class='navbar-nav']").find_element(by=By.LINK_TEXT, value = 'Champions').click()
        
    def get_champs_data(self):


        """Scrapes data for each championship year and stores in a dictionary with the year as a unique reference 
        
        """

        #creates directory for driver data
        self.__create_dir("champs_data")

        #find elements that contain champion info
        champs_data = self.driver.find_elements(by=By.XPATH, value="//div[@class='table-responsive']//td")

        no_of_pages = self.get_no_of_pages(len(champs_data)//4, "championship years")

        #loop through elements to separate into data by year
        for i in range(0,int(no_of_pages)*4,4):
                self.dict_entry={}
                self.dict_entry["ID"] = uuid.uuid4().hex
                self.dict_entry["Year number"] = i//4 + 1
                self.dict_entry["Year"] = int(champs_data[i].text)
                self.dict_entry["Driver"] = champs_data[i+1].text
                self.dict_entry["Driver's Team"] = champs_data[i+2].text
                self.dict_entry["Winning Team"] = champs_data[i+3].text
                self.champs_list.append(self.dict_entry)
                
        #dump to json file
        self.__dumptojson(self.champs_list, "./champs_data.json")

    def navigate_circuits(self):
        self.driver.get(self.URL)
        self.driver.maximize_window()
        navbar = self.driver.find_element(by=By.XPATH, value="//div[@class='row-2']").find_element(by=By.XPATH, value = "//a[@id='ctl00_HL_CircuitH']").click()

    def get_circuit_data(self):
        self.__create_dir("circuit_data")

        info_table = self.driver.find_elements(by=By.XPATH, value="//table[@class='sortable']//tbody//tr//td")
        

        no_of_pages = self.get_no_of_pages(len(info_table)//5, "circuits")
        j = 1
        for i in range(0,int(no_of_pages)*5,6):
                
                self.dict_entry={}
                self.dict_entry["ID"] = uuid.uuid4().hex
                self.dict_entry["Track Number"] = j
                self.dict_entry["Circuit Location"] = info_table[i].text
                self.dict_entry["Circuit Name"] = info_table[i+1].text
                self.dict_entry["Country"] = info_table[i+3].text
                self.dict_entry["Debut Year"] = info_table[i+4].text
                self.dict_entry["No.of times held"] = info_table[i+5].text
                self.circuit_list.append(self.dict_entry)
                j = j + 1

        #dump to json file
        self.__dumptojson(self.circuit_list, "./circuit_data.json")

    def __create_dir(self,directory: str):
        
        """Checks if the path/folder to be created already exists and if not, creates the directory

        Args:
            directory: name of the file to be created

        """
        parent_dir = "."
        path = os.path.join(parent_dir, directory)
        if os.path.exists(path) == False:
            raw_data = os.mkdir(path)

    def __dumptojson(self, dictionary: str, out_file: str):

        """Dumps the collected information into a named file.json


        Args:
            dictionary: name of the dictionary to be dumped to json file
            out_file: name of the file in which the dictionary is to be placed

        """
        out_file = open(out_file, "w")
        json.dump(dictionary, out_file, indent = 6)
        out_file.close()

    def uploadtos3(self, file):

        """Uploads the json file to s3

        Args:
            file: the file name to be uploaded to the s3 bucket

        """
        BUCKET_NAME= "formula1-aicore"

        s3 = boto3.client("s3")

        def __uploadDirectory(path,bucketname):
                for root,dirs,files in os.walk(path):
                    for file in files:
                        s3.upload_file(os.path.join(root,file),bucketname,file)

        __uploadDirectory("./raw_data/",BUCKET_NAME)
        
    def clean_data(self, data_type : str):
        """Cleans the data using pandas


        Args:
            data_type: selects which set of data is being cleaned 
        Returns:
            df: the clean data drame to be uploaded to RDS


        """
        if data_type == 'driver':
            f = open('./driver_data.json')
            data = json.load(f)
            df = pd.DataFrame(data)
            try:
                #fix other data types
                df["First Race"] = df["First Race"].astype(str)
                #Consistency for Nationalities
                df["Nationality"] = df["Nationality"].str.title()
            except KeyError as K:
                logging.error(K)
                

            #Separate circuits and years for first race and last race
            try:
                first_race_data = df["First Race"].str.rsplit(n=1, expand=True)
                last_race_data = df["Last Race"].str.rsplit(n=1, expand=True)
            except KeyError as K2:
                logging.error(K2)
               
            
            try:
                df["Debut Year"] = first_race_data[1]
                df["Debut Circuit"] = first_race_data[0]
                df["Debut Circuit"] = df["Debut Circuit"].astype(str)
                df["Final Year"] = last_race_data[1]
                df["Final Circuit"] = last_race_data[0]
                df["Final Circuit"] = df["Final Circuit"].astype(str)
            except KeyError as K3:
                df["Debut Year"] = None
                df["Debut Circuit"] = None
                df["Final Year"] = None
                df["Final Circuit"] = None
                logging.error(K3)
            
            try:
                #Separate best position and year
                df["Best championship position"] = df["Best championship position"].astype(str)
                best_champseason_place = df["Best championship position"].str.split(n=1, expand=True)
                df["Best championship position"] = best_champseason_place[0]
                best_champseason_year = best_champseason_place[1].str.split(n=2, expand=True)
                df["Best championship year"] = best_champseason_year[2]
                df["Best championship position"] = df["Best championship position"].astype(str)
                df["Best championship year"] = df["Best championship year"].astype(str)
                df.loc[df["Best championship position"] == "World", "Best championship position"] = "1st"
            except KeyError as K4:
                df["Best championship position"] = None
                df["Best championship year"] = None
                logging.error(K4)
                
            if 'Known as' not in df.columns:
                df["Known as"] = None
            else:
                pass
                
            try:    
                #Convert dates/times
                df["Date of birth"] = pd.to_datetime(df["Date of birth"], infer_datetime_format=True, errors = 'coerce')
                df["Date of death"] = pd.to_datetime(df["Date of death"], infer_datetime_format=True, errors = 'coerce')
            except KeyError as K5:
                df["Date of birth"] = None
                df["Date of death"] = None
                logging.error(K5)
                

            try:
                #fix other data types
                df["Driver First Name"] = df["Driver First Name"].astype(str)
                df["Driver Second Name"] = df["Driver Second Name"].astype(str)
                df["Nationality"] = df["Nationality"].astype(str)
                df["Hometown"] = df["Hometown"].astype(str)
                df["Driver Second Name"] = df["Driver Second Name"].astype(str)
                df = df.replace('-',np.nan)
                df = df.replace('', np.nan)
                df["Points"] = df["Points"].astype(float)

            except KeyError as K6:
                logging.error(K6)
                

            try:    
                cols = df.columns.to_list()
                cols = cols[0:8]+[cols[-7]]+cols[-5:]+cols[8:-5]
                df = df.drop("First Race", axis=1)
                df = df.drop("Last Race", axis=1)
                df = df.drop("Year active", axis=1)
                   
            except KeyError as K7:
                logging.error(K7)

            df.columns = df.columns.str.lower()
            df.columns = df.columns.str.replace(' ','_')
           
            return df
     

        if data_type == 'team':
            f = open('./teams_data.json')
            data = json.load(f)
            df = pd.DataFrame(data)

            try:
                #Separate circuits and years for first race and last race

                first_race_data = df["First Race"].str.rsplit(n=1, expand=True)
                last_race_data = df["Last Race"].str.rsplit(n=1, expand=True)
            except:
                pass
            
            try:
                df["Debut Year"] = first_race_data[1]
                df["Debut Circuit"] = first_race_data[0]
                df["Debut Circuit"] = df["Debut Circuit"].astype(str)
                df["Final Year"] = last_race_data[1]
                df["Final Circuit"] = last_race_data[0]
                df["Final Circuit"] = df["Final Circuit"].astype(str)
            except KeyError as K8:
                logging.error(K8)
                df["Debut Year"] = None
                df["Debut Circuit"] = None
                df["Debut Circuit"] = None
                df["Final Circuit"] = None
                df["Final Circuit"] = None
                

            try:    
                #Separate best position and year
                df["Best championship position (constructor)"] = df["Best championship position (constructor)"].astype(str)
                best_champseason_place = df["Best championship position (constructor)"].str.split(n=1, expand=True)
                df["Best championship position"] = best_champseason_place[0]
                df["Best championship year"] = best_champseason_place[1]
                df["Best championship position"] = df["Best championship position"].astype(str)
                df["Best championship year"] = df["Best championship year"].astype(str)
                df.loc[df["Best championship position"] == "World", "Best championship position"] = "1st"
                best_champseason_year = best_champseason_place[1].str.split(n=2, expand=True)
                df["Best championship year"] = best_champseason_year[1]
                df["Best championship position (driver)"] = df["Best championship position (driver)"].astype(str)
                best_champdriverseason_place = df["Best championship position (driver)"].str.split(n=2, expand=True)
                df["Best championship position (driver)"] = best_champdriverseason_place[0]
                df["Best championship year (driver)"] = best_champdriverseason_place[1]
                df["Best championship driver"] = best_champdriverseason_place[2]
            except KeyError as K9:
                df["Best championship year"] = None
                df["Best championship position"] = None
                df["Best championship position (driver)"] = None
                df["Best championship year (driver)"] = None
                df["Best championship driver"] = None
                logging.error(K9)
                

            try:

                cols = df.columns.to_list()
                df = df.drop("First Race", axis=1)
                df = df.drop("Last Race", axis=1)
                df = df.drop("Best championship position (constructor)", axis=1)
            except KeyError as K10:
                logging.error(K10)
                
            df = df.replace(" ",None)
            df.columns = df.columns.str.lower()
            df.columns = df.columns.str.replace(' ','_')
            return df
            

        if data_type =='champs':
            f = open('./champs_data.json')
            data = json.load(f)
            df = pd.DataFrame(data)
            df.columns = df.columns.str.lower()
            df.columns = df.columns.str.replace(' ','_')
            return df
           

        if data_type == 'circuit':
            f = open('./circuit_data.json')
            data = json.load(f)
            df = pd.DataFrame(data)
            df.columns = df.columns.str.lower()
            df.columns = df.columns.str.replace(' ','_')
            return df
            
    def prevent_rescrape(self, data_table, data_frame):

        """Checks the database to compare to the data scraped
        
        Args:
            data_table: The table to be read from the database (Drivers, Teams, Champions or Circuits
            data_frame: The clean dataframe that is left after the scraped data has been cleaned)
        """

        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        USER = 'postgres'
        DATABASE = 'Formula1'
        

        #make connection to specified database
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
        inspector = inspect(engine)
        
        if data_table == "drivers":
            sql_statement = f'''SELECT * FROM "drivers" LIMIT {len(data_frame)}'''
            subset = 'id'
        elif data_table == "teams":
            sql_statement = f'''SELECT * FROM "teams" LIMIT {len(data_frame)}'''
            subset = 'team_number'
        elif data_table == "champions":
            sql_statement = f'''SELECT * FROM "champions" LIMIT {len(data_frame)}'''
            subset = 'year_number'
        elif data_table == "circuits":
            sql_statement = f'''SELECT * FROM "circuits" LIMIT {len(data_frame)}'''
            subset = 'track_number'
        #compare old data and new data and drop duplicates
        if inspector.has_table(data_table):
            old_data = pd.read_sql_query(sql_statement,con=engine)
            merged_dfs = pd.concat((old_data, data_frame))
            merged_dfs = merged_dfs.drop_duplicates(subset, keep = False)
            
        else:
            merged_dfs = data_frame
        
        #upload what is left to database
        merged_dfs.to_sql(data_table, self.engine, if_exists='append', index = False)
        
        #add primary key if it doesn't already exist
        self.engine.execute(f'''DO $$ 
                            BEGIN
                            IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = '{data_table}_pkey') THEN
                            ALTER TABLE {data_table}
                            ADD PRIMARY KEY ({subset});
                            ELSE
                                RETURN;
                            END IF;
                            END;
                            $$;;''')
        print("hi")
                

if __name__ == "__main__":
    with open('credentials.json') as cred:
        credentials = json.load(cred)
    HOST = credentials['HOST']
    PASSWORD = credentials['PASSWORD']
    PORT = credentials['PORT']

    scraper = Scraper(URL = "https://www.4mula1stats.com/", parent_dir=".", headless = True)
   
    # retrieve all new data
    if scraper.args.drivers:
        scraper.navigate_drivers()
        scraper.get_driver_data()
        df = scraper.clean_data('driver')
        scraper.prevent_rescrape("drivers", df)
        #scraper.uploadtos3('driver_data.json')
    if scraper.args.teams:
        scraper.navigate_teams()
        scraper.get_team_data()
        df = scraper.clean_data('team')
        scraper.prevent_rescrape("teams", df)
        #scraper.uploadtos3('teams_data.json')
        
    if scraper.args.championships:
        scraper.navigate_champs()
        scraper.get_champs_data()
        df = scraper.clean_data('champs')
        scraper.prevent_rescrape("champions", df)
        #scraper.uploadtos3('champs_data.json')
    
    
    if scraper.args.circuits:
        scraper2 = Scraper("https://www.statsf1.com/en/default.aspx", parent_dir=".", headless = True)
        scraper2.navigate_circuits()
        scraper2.get_circuit_data()
        df = scraper2.clean_data('circuit')
        scraper2.prevent_rescrape("circuits", df)
        #scraper2.uploadtos3('circuit_data.json')

