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