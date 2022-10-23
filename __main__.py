from utils.formula1_scrape import Scraper
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

if __name__ == "__main__":
    
    scraper = Scraper(URL = "https://www.4mula1stats.com/", parent_dir="/home/andrew/AICore_work/Data-Collection-Pipeline", headless = True)
   
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
        scraper2 = Scraper("https://www.statsf1.com/en/default.aspx", parent_dir="/home/andrew/AICore_work/Data-Collection-Pipeline", headless = True)
        scraper2.navigate_circuits()
        scraper2.get_circuit_data()
        df = scraper2.clean_data('circuit')
        scraper2.prevent_rescrape("circuits", df)
        #scraper2.uploadtos3('circuit_data.json')
