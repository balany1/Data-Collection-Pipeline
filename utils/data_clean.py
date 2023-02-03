import json
import logging
import pandas as pd
import numpy as np

class Data_Clean:

    def clean_driver(self):
        
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

    def clean_team(self):
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
    
    def clean_champs(self):

        f = open('./champs_data.json')
        data = json.load(f)
        df = pd.DataFrame(data)
        df.columns = df.columns.str.lower()
        df.columns = df.columns.str.replace(' ','_')
        return df

    def clean_circuits(self):
        f = open('./circuit_data.json')
        data = json.load(f)
        df = pd.DataFrame(data)
        df.columns = df.columns.str.lower()
        df.columns = df.columns.str.replace(' ','_')
        return df
    
    def clean_data(self, data_type : str):
        """Cleans the data using pandas


        Args:
            data_type: selects which set of data is being cleaned 
        Returns:
            df: the clean data drame to be uploaded to RDS


        """