import time
from tracemalloc import start
import uuid
import os
import json
import urllib.request
import urllib
import argparse
import boto3 
from selenium.webdriver.common.by import By
from cgitb import text
from numpy import append
from requests import request
from selenium import webdriver
from traitlets import Bool


client = boto3.client('s3')
class Scraper:

    """Scrapes driver, team and champions data from the given website.

    Args:
        URL(str): The URL of the F1 statistics website containing the data
        driver: The webdriver used to access the webpage
        parent_dir: The parent directory of where the raw data is to be stored

    Returns:
        A dictionary of nested dictionarys for each driver and team and a dictionary for championship data for each year

    """

    def __init__(self, URL : str, driver : webdriver.Chrome, parent_dir : str):

        self.parser = argparse.ArgumentParser(description='Decide what statistics to scrape')
        self.parser.add_argument('-d','--drivers', default=False, action='store_true', help='Scrape Drivers:True/False')
        self.parser.add_argument('-t', '--teams', default=False, action='store_true', help='Scrape Teams:True/False')
        self.parser.add_argument('-c', '--championships', default=False, action='store_true', help='Scrape Championships:True/False')
        self.args = self.parser.parse_args()
        self.driver = driver
        self.URL = URL
        self.driver_list=[]
        self.teams_list= []
        self.champs_list = []
        self.dict_entry = {}
        directory = "raw_data"
        path = os.path.join(parent_dir, directory)
        if os.path.exists(path) == False:
            raw_data = os.mkdir(path)
        self.__load_and_accept_cookies()
        
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

        img_src = self.driver.find_element(by=By.XPATH, value="//img[@class='col-md-3']").get_attribute('src')
        self.__download_image(img_src, "/home/andrew/AICore_work/Data-Collection-Pipeline/raw_data/driver_images/", self.__get_driver_name())
    
    def get_no_of_pages(self,default_len : int ,title : str):

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

    def __get_URL_list(self,element : str ,title : str):

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
            self.dict_entry["ID"] = uuid.uuid4().hex
            driver_count = driver_count + 1
            self.dict_entry["Driver number"] = driver_count
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
        self.__dumptojson(self.driver_list, "driver_data.json")

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
            self.dict_entry["ID"] = uuid.uuid4().hex
            team_count = team_count + 1
            self.dict_entry["Driver number"] = team_count

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
        self.__dumptojson(self.teams_list, "teams_data.json")

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
        self.__dumptojson(self.champs_list, "champs_data.json")

    def __create_dir(self,directory : str):
        
        """Checks if the path/folder to be created already exists and if not, creates the directory

        Args:
            directory: name of the file to be created

        """
        parent_dir = "/home/andrew/AICore_work/Data-Collection-Pipeline/raw_data"
        path = os.path.join(parent_dir, directory)
        if os.path.exists(path) == False:
            raw_data = os.mkdir(path)

    def __dumptojson(self, dictionary : str, out_file : str):

        """Dumps the collected information into a named file.json


        Args:
            dictionary: name of the dictionary to be dumped to json file
            out_file: name of the file in which the dictionary is to be placed

        """
        out_file = open(out_file, "w")
        json.dump(dictionary, out_file, indent = 6)
        out_file.close()

if __name__ == "__main__":
    scraper = Scraper("https://www.4mula1stats.com/", webdriver.Chrome(), "/home/andrew/AICore_work/Data-Collection-Pipeline")
    if scraper.args.drivers:
        scraper.navigate_drivers()
        scraper.get_driver_data()
    if scraper.args.teams:
        scraper.navigate_teams()
        scraper.get_team_data()
    if scraper.args.championships:
        scraper.navigate_champs()
        scraper.get_champs_data()

