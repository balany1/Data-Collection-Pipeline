import time
import uuid
import os
import json
import urllib.request
import urllib
from selenium.webdriver.common.by import By
from cgitb import text
from numpy import append
from requests import request
from selenium import webdriver

class Scraper:

    """Scrapes driver, team and champions data from the given website.


    Args:
        URL(str): The URL of the F1 statistics website containing the data
        driver: The webdriver used to access the webpage
        parent_dir: The parent directory of where the raw data is to be stored

    Returns:
        A dictionary of nested dictionarys for each driver and team and a dictionary for championship data for each year

    """

    def __init__(self, URL : str, driver : webdriver.Chrome, parent_dir:str):
        
        self.driver = driver
        self.team_list = []
        self.URL = URL
        self.driver_dict={}
        self.teams_dict = {}
        self.champs_dict = {}
        self.dict_entry = {}
        directory = "raw_data"
        path = os.path.join(parent_dir, directory)
        if os.path.exists(path) == False:
            raw_data = os.mkdir(path)
        

    def load_and_accept_cookies(self) -> None:

        """Opens the site and accepts cookies"""
        
        self.driver.get(self.URL)
        accept_button = self.driver.find_element(by=By.XPATH, value="//*[@class='btn btn-success acceptGdpr']")
        accept_button.click()
        
    def navigate_drivers(self):

        """Navigates to the list of F1 drivers and calls the get_driver_data method to begin scraping the data for each driver"""

        self.driver.get(self.URL) 
        navbar = self.driver.find_element(by=By.XPATH, value="//div[@class='navbar-nav']").find_element(by=By.LINK_TEXT, value = 'Drivers').click()
        self.get_driver_data()

    def get_image(self):

        """Method that is called within get_driver_data that locates the element containing the drivers image and calls the function to download the image"""

        img_src = self.driver.find_element(by=By.XPATH, value="//img[@class='col-md-3']").get_attribute('src')
        self.download_image(img_src, "/home/andrew/AICore_work/Data-Collection-Pipeline/driver_images/", self.get_driver_name())
    
    def get_URL_list(self,element):

        """Scrapes URL for each driver
        
        Args:
            element(str):   References the necessary element on the webpage that contains the required data
            
        Returns:
            url_list(list): List of URLS for each driver that can then be looped through to scrape data    
        """

        url_list = []
        
        starting_letter_tag = self.driver.find_elements(by=By.XPATH, value=element)

        for pilot in starting_letter_tag: #collects all the drivers URLS in a list

            link = pilot.find_element(By.TAG_NAME, 'a').get_attribute('href')
            url_list.append(link)

        return url_list
        
    def download_image(self, url, file_path, file_name):

        """Downloads the image located in get_image to the required location
        
        Args:
            url:       Webpage containg the required image
            file_path: Gives the path of where the image is downloaded to
            file_name: Names the file in a Forename_Surname format by calling get_driver_name  
        """

        full_path = file_path + file_name + '.jpg'
        urllib.request.urlretrieve(url, full_path)

    def stripF1_text(self, tobereplaced):

        """Reformats the Name of the Driver/Team without any unneccessary text
        
        Args:
            toberreplaced(str):   Unnecessary text to be reformatted
            
        Returns:
            Name(str): Name in required format
        """
        Name = self.driver.find_element(by=By.XPATH, value="//h1[@class='page-title']").text.replace(tobereplaced, "")
        return Name
    
    def get_driver_name(self) -> str: 

        """Splits Driver Name string into Forename and Surname and store as variables to be able to add to driver dictionary/use for filename for image
        
        """
        
        Name = self.stripF1_text("Formula 1 Driver")
        driver_forename = Name.split()[0]
        driver_surname = " ".join(Name.split()[1:len(Name.split())-3])

        self.dict_entry["Driver First Name"] = driver_forename
        self.dict_entry["Driver Second Name"] = driver_surname
        return driver_forename + "_" + driver_surname

    def get_driver_data(self):

        """Scrapes data for each driver and stores in a dictionary with a unique reference 
        
        """
        
        #creates directory for driver data
        self.create_dir("driver_data")

        #find element containing individual driver URLS
        url_list = self.get_URL_list("//div[@class='col-sm-6 col-md-4']")

        
        for link in url_list: #loops through every URL in the list and scrapes the statistics
            
            #resets the dictionary entry to blank at the beginning of each URL
            self.dict_entry={}

            #opens each URL in the list
            self.driver.get(link)

            self.get_driver_name() #gets the Drivers Name and splits it into First name, Surname
            self.get_image()

            #scrapes the data from the different columns
            column1_data = self.driver.find_elements(by=By.XPATH, value="//div[@class='col-md-6']//td")
            for i in range(0,len(column1_data),2):
                    self.dict_entry[column1_data[i].text] = column1_data[i+1].text
            column23_data = self.driver.find_elements(by=By.XPATH, value="//div[@class='col-md-3']//td")
            for i in range(0,len(column23_data),2):
                    self.dict_entry[column23_data[i].text] = column23_data[i+1].text

            #add each entry as a nested dictionary
            self.driver_dict[uuid.uuid4().hex] = self.dict_entry

        #dump to json file
        self.dumptojson(self.driver_dict, "driver_data.json")

    def navigate_teams(self):

        """Navigates to the list of F1 teams and calls the get_team_data method to begin scraping the data for each team"""

        self.driver.get(self.URL)
        navbar = self.driver.find_element(by=By.XPATH, value="//div[@class='navbar-nav']").find_element(by=By.LINK_TEXT, value = 'Teams').click()
        self.get_team_data()

    def get_team_name(self):

        """Reformats the Name of the Team without any unneccessary text
        
        """
        
        Team_Name = self.stripF1_text("Formula 1")
        self.dict_entry["Team Name"] = Team_Name
        
    def get_team_data(self):

        """Scrapes data for each driver and stores in a dictionary with a unique reference 
        
        """
        
        #creates directory for team data
        self.create_dir("team_data")

        #find element containing individual driver URLS
        url_list = self.get_URL_list("//div[@class='col-sm-6 col-md-4']")
            
        #loops through every URL in the list and scrapes the statistics
        for link in url_list[:5]: 
            
            #resets the dictionary entry to blank at the beginning of each URL
            self.dict_entry={}

            #opens each page in the list of URLs
            self.driver.get(link)

            #gets the Drivers Name and strips the "Formula 1" from it
            self.get_team_name() 

            #scrape the data from the different tables on each page
            team_history_data = self.driver.find_elements(by=By.XPATH, value="//div[@class='table-responsive']//tbody[@itemtype='http://schema.org/SportsTeam']//td")
            for i in range(0,len(team_history_data),2):
                self.dict_entry[team_history_data[i].text] = team_history_data[i+1].text

            team_driver_data = self.driver.find_elements(by=By.XPATH, value="//div[@class='col-md-6']//td")
            for i in range(0,len(team_driver_data),2):
                self.dict_entry[team_driver_data[i].text] = team_driver_data[i+1].text

            team_data = self.driver.find_elements(by=By.XPATH, value="//div[@class='col-md-5']//td")
            for i in range(0,len(team_data),2):
                self.dict_entry[team_data[i].text] = team_data[i+1].text
            
            #add each entry as a nested dictionary
            self.teams_dict[uuid.uuid4().hex] = self.dict_entry

        #dump to json file
        self.dumptojson(self.teams_dict, "teams_data.json")

    def navigate_champs(self):

        """Navigates to the list of F1 champions and calls the get_champs_data method to begin scraping the data for each championship year"""

        self.driver.get(self.URL)
        navbar = self.driver.find_element(by=By.XPATH, value="//div[@class='navbar-nav']").find_element(by=By.LINK_TEXT, value = 'Champions').click()
        self.get_champs_data()

    def get_champs_data(self):

        """Scrapes data for each championship year and stores in a dictionary with the year as a unique reference 
        
        """

        #creates directory for driver data
        self.create_dir("champs_data")

        #find elements that contain champion info
        champs_data = self.driver.find_elements(by=By.XPATH, value="//div[@class='table-responsive']//td")

        #loop through elements to separate into data by year
        for i in range(0,len(champs_data),4):
                self.dict_entry={}
                self.dict_entry["Year"] = champs_data[i].text
                self.dict_entry["Driver"] = champs_data[i+1].text
                self.dict_entry["Driver's Team"] = champs_data[i+2].text
                self.dict_entry["Winning Team"] = champs_data[i+3].text
                self.champs_dict[uuid.uuid4().hex] = self.dict_entry
                
        #dump to json file
        self.dumptojson(self.champs_dict, "champs_data.json")

    def create_dir(self,directory):
        
        """Checks if the path/folder to be created already exists and if not, creates the directory

        Args:
            directory: name of the file to be created

        """
        parent_dir = "/home/andrew/AICore_work/Data-Collection-Pipeline/raw_data"
        path = os.path.join(parent_dir, directory)
        if os.path.exists(path) == False:
            raw_data = os.mkdir(path)

    def dumptojson(self, dictionary, out_file):

        """Dumps the collected information into a named file.json


        Args:
            dictionary: name of the dictionary to be dumped to json file
            out_file: name of the file in which the dictionary is to be placed

        """
        out_file = open(out_file, "w")
        json.dump(dictionary, out_file, indent = 6)

if __name__ == "__main__":
    scraper = Scraper("https://www.4mula1stats.com/", webdriver.Chrome(), "/home/andrew/AICore_work/Data-Collection-Pipeline")
    scraper.load_and_accept_cookies()
    scraper.navigate_drivers()
    scraper.navigate_teams()
    scraper.navigate_champs()
