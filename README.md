# Data-Collection-Pipeline

In this project, I aiming to scrape data from "4mula1stats.com", a formula one statistics website as I am an avid Formula1 fan and have great interest in the history of the sport

I have installed and used Selenium to begin this and learned how to navigate elements in a webpage

Milestone 2:

The code at this stage currently opens the webpage and accepts cookies with the code:

        accept_button = self.driver.find_element(by=By.XPATH, value="//*[@class='btn btn-success acceptGdpr']")
        accept_button.click()

There are then functions to navigate through the data pages, using the code(for instance for drivers):

        navbar = self.driver.find_element(by=By.XPATH, value="//div[@class='navbar-nav']")
        drivers_button= navbar.find_element(by=By.LINK_TEXT, value = 'Drivers')
        drivers_button.click()

There are equivalent functions for teams and champions

The next milestone will begin to scrape the data from these pages:

Milestone 3:

I have written code to loop through each driver's data page and scrape the basic data first by collecting the URLS:

for pilot in starting_letter_tag:

            a_tag = pilot.find_element(By.TAG_NAME, 'a')
            link = a_tag.get_attribute('href')
            self.driver_list.append(link)

And then printing the data from each URL while allowing for some potential errors while loading the page

            my_element_id = "//*div[@class='col-md-6']"

            self.driver.get(link)
            time.sleep(2) #to avoid being seen as a bot
            ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
            WebDriverWait(driver,20,0.5,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, my_element_id)))
            column1_data = self.driver.find_elements(by=By.XPATH, value="//div[@class='col-md-6']//td")
            for i in range(1,len(column1_data),2):
                print(column1_data[i].text)
            column23_data = self.driver.find_elements(by=By.XPATH, value="//div[@class='col-md-3']//td")
            for i in range(1,len(column23_data),2):
                print(column23_data[i].text)

I have replicated these methods to get the data for the constructors and champions

Due to the formatting of the page I have created a method that reformats the name of a driver/Team in order to be able to store it in a format I can use later

 def get_driver_name(self) -> str: #gets the Drivers Name and splits it into First name, Surname and adds it to dictionary
        
        Page_Title = self.driver.find_element(by=By.XPATH, value="//h1[@class='page-title']")
        Name = Page_Title.text
        Name.replace("Formula 1 Driver", "")
        Driver_Forename = Name.split()[0]
        Driver_Surname = " ".join(Name.split()[1:len(Name.split())-3])

At this point, once it was shown the print statements were giving me the data I wanted, I decided to start saving this data to a dictionary. I have needed to use nested dictionaries to achieve this. My drivers dictionary contains the UUID I have created for that driver as a tag and the dictionary of that drivers statistics as the entry.

            column1_data = self.driver.find_elements(by=By.XPATH, value="//div[@class='col-md-6']//td")
            for i in range(0,len(column1_data),2):
                    self.dict_entry[column1_data[i].text] = column1_data[i+1].text
            column23_data = self.driver.find_elements(by=By.XPATH, value="//div[@class='col-md-3']//td")
            for i in range(0,len(column23_data),2):
                    self.dict_entry[column23_data[i].text] = column23_data[i+1].text

            #add each entry as a nested dictionary
            self.driver_dict[uuid.uuid4().hex] = self.dict_entry

I have replicated this approach for the teams and champions

Once these dictionaries were created, I have saved them to JSON files. The code I used to do this was by creating the directory for the dictionaries to be stored in the if __name__ == "__main__": method

        if __name__ == "__main__":
        
        # directory = "raw_data"
        # parent_dir = "/home/andrew/AICore_work/Data-Collection-Pipeline"
        # path = os.path.join(parent_dir, directory)
        # raw_data = os.mkdir(path)

And within the get_drivers_data and get_teams_data

        out_file = open("driver_data.json", "w")
        json.dump(self.driver_dict, out_file, indent = 6)

Lastly, I have created a method to download images from the website using urllib package

        def download_image(self, url, file_path, file_name):
                full_path = file_path + file_name + '.jpg'
                urllib.request.urlretrieve(url, full_path)

And called it within the get_driver_data method

            self.driver.get(link)
            img_src = self.driver.find_element(by=By.XPATH, value="//img[@class='col-md-3']")
            img = img_src.get_attribute('src')
            self.download_image(img, "/home/andrew/AICore_work/Data-Collection-Pipeline/driver_images/", self.get_driver_name())

Milestone 5: 

During this milestone, I have undergone an extensive refactoring of my code with a focus on ensuring that every method does one thing and this has resulted in my code containing many more methods than it had previously. For instance, previously I had this code to collect URLs in each of the get_driver_data, get_team_data and get_champs_data 

#collects all the drivers URLS in a list
           for team in starting_letter_tag: 
    
               a_tag = team.find_element(By.TAG_NAME, 'a')
               link = a_tag.get_attribute('href')
               self.team_list.append(link)
               
           #loops through every URL in the list and scrapes the statistics
           for link in self.team_list:
               
               #resets the dictionary entry to blank at the beginning of each URL
               self.dict_entry={}

               #opens each page in the list of URLs

I created a method for lines 107 to 111 on its own that is called within each of the three previous methods mentioned. This has simplified my code and doing this has furthered my understanding of using arguments

        url_list = self.__get_URL_list("//div[@class='col-sm-6 col-md-4']","drivers")

The arguments in the above line of code represent the div container containing the required URLS to be collected and the "drivers" references which method that the get_URL-list has been called from. This understanding has made my code more robust as to be used in other applications with as little change as possible.

In addition to this, I refactored the code to include argument parsing to give the user choice over how much data and what type of data to scrape. It also included error handling to enforce an integer input. An example of this is:

	self.parser = argparse.ArgumentParser(description='Decide what statistics to scrape')
        self.parser.add_argument('-d','--drivers', default=False, action='store_true', 			 help='Scrape Drivers:True/False')

I have learned the protocol and etiquette for adding docstrings to my code to enable tthe user to understand the code more effectively. An example of this is:

def __stripF1_text(self, tobereplaced : str):

        """Reformats the Name of the Driver/Team without any unneccessary text
        
        Args:
            toberreplaced(str):   Unnecessary text to be reformatted
            
        Returns:
            Name(str): Name in required format
        """
        
At this point in my code I have also learned about function type expressions and have added types to all of my methods.

Unit testing was the next thing to add to my code. Firstly, this required me to make some of my methods private as they were called within other methods and by testing the public methods i was implicitly testing the private methods as well. This required some refactoring of my code: def navigate_driver() had previously called def get_driver_data. I had to change the if __name__ = '__main__' to separate these two methods so that I could test them separately. 

I tested my navigation methods with the following code:

def test_scrapenavigate_driver(self):
        self.scraper.navigate_drivers()
        response = requests.get(self.scraper.driver.current_url)
        self.assertEqual(response.url, "https://www.4mula1stats.com/driver")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 400)
        
which only needed to check that the correct URL was reached and that the URL was reached correctly with no error codes. The get_*_data methods required more testing. For these I needed the mock library and had to patch in a user input

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


This checked the length of dictionary produced was correct and that the type of output was in fact a dictionary. The unit test further checked that the types of the key pairs were as they should be. These tests were applied to both the teams and champions data as such testing all the public methods.

Milestone 6:

This part of the code looks at the json files that have been created and cleans the data using pandas. try/except statements are used to deal with key errors that can come up when cleaning data that is inconsistent.

if data_type == 'Driver':
            f = open('driver_data.json')
            data = json.load(f)
            df = pd.DataFrame(data)
            try:
                #fix other data types
                df["First Race"] = df["First Race"].astype(str)
                #Consistency for Nationalities
                df["Nationality"] = df["Nationality"].str.title()
            except KeyError:
                pass

            #Separate circuits and years for first race and last race
            try:
                first_race_data = df["First Race"].str.rsplit(n=1, expand=True)
                last_race_data = df["Last Race"].str.rsplit(n=1, expand=True)
            except KeyError:
                pass
            
            try:
                df["Debut Year"] = first_race_data[1]
                df["Debut Circuit"] = first_race_data[0]
                df["Debut Circuit"] = df["Debut Circuit"].astype(str)
                df["Final Year"] = last_race_data[1]
                df["Final Circuit"] = last_race_data[0]
                df["Final Circuit"] = df["Final Circuit"].astype(str)
            except KeyError:
                pass


At this point, AWS is used to set up RDS database and S3 bucket to scalably store data. boto3 is used to upload to s3 and a method is created to complete the upload as well as a method to upload to the Postgresql database. 


 def uploadtos3(self, file):

        """Uploads the json file to s3


        Args:
            file: the file name to be uploaded to the s3 bucket

        """
        BUCKET_NAME= "formula1-aicore"

        s3 = boto3.client("s3")

        def uploadDirectory(path,bucketname):
                for root,dirs,files in os.walk(path):
                    for file in files:
                        s3.upload_file(os.path.join(root,file),bucketname,file)

        uploadDirectory("/home/andrew/AICore_work/Data-Collection-Pipeline/back_up",BUCKET_NAME)

The method that uploads to the database is below and has provision to check for exisitng data. It does this by reading the existing data and comparing to the new table that has been scraped and using pandas to drop duplicates. sqlalchemy and psycopg2 are used to create a connection to the RDS database and execute the sql queries

    def prevent_rescrape(self, data_table, data_frame):

        """Checks the database to compare to the data scraped
        
        Args:
            data_table: The table to be read from the database (Drivers, Teams, Champions or Circuits
            data_frame: The clean dataframe that is left after the scraped data has been cleaned)
        """

        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        HOST = 'formula1.c0ptp1rfwhvx.eu-west-2.rds.amazonaws.com'
        USER = 'postgres'
        PASSWORD = 'T00narmyf1s'
        DATABASE = 'Formula1'
        PORT = 5432

        #make connection to specified database
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

        if data_table == "Drivers":
            sql_statement = '''SELECT * FROM "Drivers"'''
            subset = 'Driver number'
        elif data_table == "Teams":
            sql_statement = '''SELECT * FROM "Teams"'''
            subset = 'Team number'
        elif data_table == "Champions":
            sql_statement = '''SELECT * FROM "Champions"'''
            subset = 'Year number'
        elif data_table == "Circuits":
            sql_statement = '''SELECT * FROM "Circuits"'''
            subset = 'Track Number'

        #compare old data and new data and drop duplicates
        old_data = pd.read_sql_query(sql_statement,con=engine)
        merged_dfs = pd.concat((old_data, data_frame))
        merged_dfs = merged_dfs.drop_duplicates(subset=subset)

        #upload what is left to database
        merged_dfs.to_sql(data_table, self.engine, if_exists='replace', index = False)
        self.engine.execute(f'ALTER TABLE "{data_table}" ADD PRIMARY KEY ("{subset}");')




