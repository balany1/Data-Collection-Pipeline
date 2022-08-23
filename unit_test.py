import builtins
import unittest
import time
from unittest import result
from unittest import mock
import urllib
import requests
from selenium import webdriver
from requests import request
from urllib.request import urlopen
from ast import Assert, Pass
from formula1_scrape import Scraper
from unittest.mock import patch, PropertyMock
import sys
import json


class TestScraper(unittest.TestCase):

    def setUp(self) -> None:
        self.scraper = Scraper("https://www.4mula1stats.com/", webdriver.Chrome(), "/home/andrew/AICore_work/Data-Collection-Pipeline")
        return super().setUp()

    def tearDown(self) -> None:
        self.scraper.driver.quit()
        return super().tearDown()

    def test_scrapenavigate_driver(self):
        self.scraper.navigate_drivers()
        response = requests.get(self.scraper.driver.current_url)
        self.assertEqual(response.url, "https://www.4mula1stats.com/driver")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 400)
        

    def test_scrapenavigate_team(self):
        self.scraper.navigate_teams()
        response = requests.get(self.scraper.driver.current_url)
        self.assertEqual(response.url, "https://www.4mula1stats.com/team" )
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 400)
       
        
        
    def test_scrapenavigate_champs(self):
        
        self.scraper.navigate_champs()
        response = requests.get(self.scraper.driver.current_url)
        self.assertEqual(response.url, "https://www.4mula1stats.com/champions")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 400)
        

    @patch('builtins.input', return_value = 7)
    def test_scrape_driver(self,
        mock_input
        ):

        #asserts dictionary length matches input
        self.scraper.navigate_drivers()
        self.scraper.get_driver_data()
        dict_len = len(self.scraper.driver_list)
        self.assertEqual(dict_len, mock_input.return_value)

        #checks mock input has been called
        mock_input.assert_called_once()

        #asserts output type is a list
        output_type = type(self.scraper.driver_list)
        assert output_type is list
        
        #checks certain entrys to see if they are as expected
        f = open('driver_data.json')
        drivers_dictionary = json.load(f)
        driver_atrributes_list  = list(drivers_dictionary[0].values())
        driver_first_name = driver_atrributes_list[1]
        self.assertEqual(driver_first_name,"Adolf")
        assert type(driver_first_name) is str
        f.close()


    @patch('builtins.input', return_value = 4)
    def test_scrape_team(self, 
        mock_input
        ):

        #asserts dictionary length matches input
        self.scraper.navigate_teams()
        self.scraper.get_team_data()
        dict_len = len(self.scraper.teams_list)
        self.assertEqual(dict_len, mock_input.return_value)

        #checks mock input has been called
        mock_input.assert_called_once()
        
        #asserts output type is a list
        output_type = type(self.scraper.teams_list)
        assert output_type is list

        #checks certain entrys to see if they are as expected
        f = open('teams_data.json')
        teams_dictionary = json.load(f)
        teams_attributes_list  = list(teams_dictionary[0].values())
        teams_name = teams_attributes_list[1]
        self.assertEqual(teams_name,"AAW Racing ")
        assert type(teams_name) is str
        f.close()
        
    @patch('builtins.input', return_value = 8)
    def test_scrape_champs(self, 
        mock_input):

        #asserts dictionary length matches input
        self.scraper.navigate_champs()
        self.scraper.get_champs_data()
        dict_len = len(self.scraper.champs_list)
        self.assertEqual(dict_len, mock_input.return_value//4)

        #checks mock input has been called
        mock_input.assert_called_once()

        #asserts output type is a list
        output_type = type(self.scraper.champs_list)
        assert output_type is list


if __name__ == '__main__':
    unittest.main()
    