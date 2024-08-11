# GemInCourse-NJIT Course Catalog Scraper

**NJIT Course Catalog Scraper** is a part of **GemInCourse** project whose main aim is to scrape the data from the New Jersey Institute of Technology's course catalog website and convert it into a structured JSON format to upload it onto the MongoDB database.

## Installation and Usage
```bash
# Cloning a specific branch of the repository:
git clone git@github.com:ShivamSrng-OIE/njit-course-catalog-scrapper.git

# Changing the current directory:
cd .\njit-course-catalog-scrapper\

# In the directory download and add the configuration file 'config.ini' in 'For NJIT Course Catalog Scraper' directory from the shared Google Drive link in the submitted competition form.

# Using package manager install the required libraries:
pip install -r .\requirements.txt

# After successful installation of all the packages, run the codebase using:
python main.py
```
FastAPI provides an intuitive dashboard also knwon as **Swagger UI** for making the API calls. In order to open the **Swagger UI**, follow the steps given below:
- For example, after executing if your output is: 
  > INFO:     Started server process [24136]<br/>
  > INFO:     Waiting for application startup.<br />
  > INFO:     Application startup complete.<br />
  > INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
  
- The append "/docs" as: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- In the NJIT Course Catalog Scraper Section expand the API and provide the input as:
  > course_catalog_name: Cyberpsychology<br />
  > course_catalog_url: [https://catalog.njit.edu/undergraduate/science-liberal-arts/humanities-and-social-sciences/cyberpsychology-bs/](https://catalog.njit.edu/undergraduate/science-liberal-arts/humanities-and-social-sciences/cyberpsychology-bs/)
- This will initiate the process of scraping for Cyberpsychology and progress of scrapping will be visible in the bash window.
- Once, completed you can check the data in the database using MongoDB Atlas

## Contributors
* **Shivam Manish Sarang**
  - Graduate Student Research Assistant, for Office of Institutional Effectiveness.
  -  Currently pursuing Master's in Computer Science, Ying Wu College of Computing at New Jersey Institute of Technology.
  - Contact: [Shivam NJIT Email ID: sms323@njit.edu](mailto:sms323@njit.edu)
* **Yi Meng**
  - Associate Director for Survey Research, for Office of Institutional Effectiveness.
  - Contact: [Yi Meng NJIT Email ID: yi.meng@njit.edu](mailto:yi.meng@njit.edu)
* **Office of Institutional Effectiveness** - New Jersey Institute of Technology