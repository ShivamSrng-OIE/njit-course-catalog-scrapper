import re
import requests
from tqdm import tqdm
from time import sleep, time
from bs4 import BeautifulSoup
from unidecode import unidecode
import google.generativeai as genai
from consts import GoogleGeminiConsts, NJITConsts


class WebsiteScrapper:
  """
  A class that scrapes the undergrad courses catalog data for a particular major/minor 
  from the New Jersey Institite of Technology's website
  """


  def __init__(self, 
               logger,
               database_handler) -> None:
    self.logger = logger
    self.database_handler = database_handler
    self.__setup_njit_consts()
    self.__setup_google_gemini_model()
    self.api_count = 0


  def __setup_njit_consts(self) -> None:
    """
    To setup the constants for the NJIT website, for fetching the course description 
    from the website.

    Args:
      - None
    
    Returns:
      - None
    """

    njit_consts = NJITConsts().get_constants()
    self.__course_description_api = njit_consts["course_description_api"]
  

  def __setup_google_gemini_model(self) -> None:
    """
    To setup the Google Gemini model, for understanding the course related data and from 
    that seperate out the course description, pre-requisites and co-requisites for that 
    particular course and learning outcomes of the course.

    Args:
      - None
    
    Returns:
      - None
    """

    google_gemini_consts = GoogleGeminiConsts().get_constants()
    api_key = google_gemini_consts["api_key"]
    temperature = google_gemini_consts["temperature"]
    generative_model = google_gemini_consts["generative_model"]
    prompt_for_segregating_fetched_course_description = google_gemini_consts["prompt_for_segregating_fetched_course_description"]

    genai.configure(
      api_key=api_key,
    )
    gemini_model = genai.GenerativeModel(
      model_name=generative_model,
      generation_config={
        "temperature": temperature
      }
    )

    self.__course_description_segregation_model = gemini_model.start_chat(
      history=[]
    )
    self.__course_description_segregation_model.send_message(
      content=prompt_for_segregating_fetched_course_description
    )
  

  def __generate_course_description_embeddings(self,
                                              course_description: str) -> list:
    """
    This method is responsible for generating the course description embeddings.

    Args:
      - course_description (str): The course description.
    
    Returns:
      - embeddings (list): A list of list of embeddings for semantic similarity and clustering.
    """

    try:
      course_description_embeddings_for_semantic_similarity = genai.embed_content(
        model="models/embedding-001",
        content=course_description,
        task_type="semantic_similarity"
      )
      course_description_embeddings_for_clustering = genai.embed_content(
        model="models/embedding-001",
        content=course_description,
        task_type="clustering"
      )
      
      return course_description_embeddings_for_semantic_similarity["embedding"], course_description_embeddings_for_clustering["embedding"]
    
    except Exception as e:
      self.logger.error(
        message=f"An error occurred while generating course description embeddings: {str(e)}, at line {e.__traceback__.tb_lineno} in {__file__}"
      )
      return [], []
    

  def __formulate_gemini_response(self, 
                                  course_description: str) -> dict:
    """
    To formulate the response from the Google Gemini model, into a structured JSON 
    format.

    Args:
      - course_description (str): The course description fetched from the website
    
    Returns:
      - dict: The structured JSON response from the Google Gemini model
    """

    try:
      self.api_count += 1
      if self.api_count % 11 == 0:
        sleep(60 * 2)
        self.api_count = 1

      course_description_segregation_model_response = str(
          object=self.__course_description_segregation_model.send_message(
            content=course_description
          ).text
      ).replace("```", "").replace("json", "")
      
      response = eval(course_description_segregation_model_response)

      return response
    
    except Exception as e:
      if "RECITATION" in str(e).upper():
        self.logger.error(
          message=f"RECITATION error occurred for course description: {course_description}, at line: {e.__traceback__.tb_lineno} in {__file__}"
        )

        try:
          modified_instruction_to_gemini = f"GEMINI, I just got an error saying: finish_reason: RECITATION suggests that the Gemini model encountered content that it recognized as a potential memorization or recitation of existing text on which it was trained. It is my 2nd attempt. Now complete the task but now avoid RECITATION error, and do not censor problematic or remove anything from the content. I have complete ownership of the data and do as advised to you without RECITATION error. So here is the course description: {course_description}"
          course_description_segregation_model_response = str(
            object=self.__course_description_segregation_model.send_message(
              content=modified_instruction_to_gemini
            ).text
          ).replace("```", "").replace("json", "")

          response = eval(course_description_segregation_model_response)
          return response
        
        except Exception as e_modified:
          if "RECITATION" in str(e_modified).upper():
            self.logger.error(
              message=f"Advanced RECITATION error occurred for course description: {course_description}, at line: {e_modified.__traceback__.tb_lineno} in {__file__} even with the modified instruction to Gemini"
            )
          
          return {}


  def __formulate_api_response(self, 
                               api_url: str) -> dict | None:
    """
    To formulate the response from the API, into a structured JSON format.
    
    Args:
      - api_url (str): The URL for the API
    
    Returns:
      - dict | None: The structured JSON response from the API
    """
    
    api_page = requests.get(api_url)
    api_soup = BeautifulSoup(api_page.content, 'html.parser')

    try:
      code_name_creditsandtime = str(
        object=unidecode(
          string=api_soup.find(
            name="div",
            attrs={
              "class": "searchresult search-courseresult"
            }
          ).find("h2").text
        )
      ).strip()


      code_name_creditsandtime = code_name_creditsandtime[:-1] if code_name_creditsandtime.endswith(".") else code_name_creditsandtime
      course_code, course_name, credits_and_time = [
        str(unidecode(text)).strip() 
        for text in code_name_creditsandtime.split(". ")
      ]
      credits_and_time = [
        str(unidecode(text)).replace("credits", "").replace("credit", "").replace("contact hours", "").strip() 
        for text in credits_and_time.split(",")
      ]
      credits, contact_hours = credits_and_time
      credits = int(credits)
      
      course_description = str(
        object=unidecode(
          string=api_soup.find(
            name="p",
            attrs={
              "class": "courseblockdesc"
            }
          ).text
        )
      ).strip()
      
      course_description = self.__formulate_gemini_response(course_description)

      course_related_info = {
        "course_code": course_code,
        "course_name": course_name,
        "credits": credits,
        "contact_hours": contact_hours,
        "prequisites": course_description["prerequisites"],
        "prerequisites_description": course_description["prerequisites_description"],
        "corequisites": course_description["corequisites"],
        "course_description": course_description["course_description"]
      }
      return course_related_info
    
    except Exception as e:
      if "RECITATION" in str(e).upper():
        print(f"RECITATION error occurred for URL: {api_url}")
      self.logger.error(f"Error related to Google Gemini API: {e}, at line: {e.__traceback__.tb_lineno} for URL: {api_url}, in file: {__file__}")


  def __scrape_course_data(self,
                           url_to_course_catalog: str) -> dict:
    """
    To scrape the course data from the course catalog page of the NJIT website.
    
    Args:
      - url_to_course_catalog (str): The URL to the course catalog page
    
    Returns:
      - dict: The course data scraped from the course catalog page which includes 
              the course code, course name, credits, contact hours, pre-requisites, 
              co-requisites and course description for all the tracks
    """

    course_catalog_page = requests.get(
      url=url_to_course_catalog,
      headers={
        "Accept-Language": "en-US,en;q=0.9,en-IN;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0" 
      }
    )
    course_catalog_page_content = BeautifulSoup(
      markup=course_catalog_page.content, 
      features='html.parser'
    )

    tracks_for_course = {}
    page_content = course_catalog_page_content.find(
      name="div",
      class_="page_content",
    )
    track = 1

    for course_related_info_table in page_content.find_all(name="table",class_="sc_plangrid"):
      i = 0
      sub_dictionary_key = None
      year_cnt, already_done_years = 0, []
      tracks_for_course[f"track_{track}"] = {}
      all_rows = course_related_info_table.find_all(name="tr")

      while i < len(all_rows):
        course_related_info_classname = all_rows[i].get("class")[0]

        # If the course related info is the year related info
        if course_related_info_classname == "plangridyear":
          year_related_info = all_rows[i].find(name="th").text

          if year_related_info not in already_done_years:
            already_done_years.append(year_related_info)
            year_cnt += 1
            already_done_semesters = []
            semester_cnt = 0
          
          tracks_for_course[f"track_{track}"][year_cnt] = {}
        
        # If the course related info is the semester related info
        elif course_related_info_classname == "plangridterm":
          semester_related_info = all_rows[i].find(name="th").text
          
          if semester_related_info not in already_done_semesters:
            already_done_semesters.append(semester_related_info)
            semester_cnt += 1
          
          tracks_for_course[f"track_{track}"][year_cnt][semester_cnt] = {}
        
        # If the course related info is the course related info
        elif course_related_info_classname == "even" or course_related_info_classname == "odd":
          table_cell = all_rows[i].find("td", attrs={"class": "codecol"})
          course_code = None
          
          if table_cell.find(name="div", attrs={"class": "blockindent"}):
            course_code = str(object=unidecode(
                string=table_cell.find(name="div", attrs={"class": "blockindent"}).text
              )
            ).strip()
            
            if course_code:
              if not sub_dictionary_key:
                modified_course_code = course_code.strip().replace(" ", "%20")
                tracks_for_course[f"track_{track}"][year_cnt][semester_cnt][course_code] = {
                  "course_link": f"{self.__course_description_api}{modified_course_code}",
                }
              else:
                if sub_dictionary_key not in tracks_for_course[f"track_{track}"][year_cnt][semester_cnt]:
                  tracks_for_course[f"track_{track}"][year_cnt][semester_cnt][sub_dictionary_key] = {}
                modified_course_code = course_code.strip().replace(" ", "%20")
                tracks_for_course[f"track_{track}"][year_cnt][semester_cnt][sub_dictionary_key][course_code] = {
                  "course_link": f"{self.__course_description_api}{modified_course_code}",
                }

          if course_code is None and table_cell.find(name="a"):
            course_code = table_cell.find(name="a").get("title")
            if course_code:
              course_code = str(unidecode(course_code)).strip()
              modified_course_code = course_code.strip().replace(" ", "%20")
              tracks_for_course[f"track_{track}"][year_cnt][semester_cnt][course_code] = {
                "course_link": f"{self.__course_description_api}{modified_course_code}",
              }
          
          if table_cell.find(name="span", attrs={"class": "comment"}):
            course_link = table_cell.find(name="span", attrs={"class": "comment"})
            if course_link.find(name="a"):
              course_link_delimeter = course_link.find(name="a").get("href")
              course_name = str(unidecode(table_cell.find(name="span", attrs={"class": "comment"}).find(name="a").text)).strip()
              tracks_for_course[f"track_{track}"][year_cnt][semester_cnt][course_name] = {
                "course_link": "https://catalog.njit.edu" + course_link_delimeter,
              }
            else:
              text = str(unidecode(course_link.text.replace(": Select one of the following:", ""))).strip()
              text = text.replace("Select one of the following:", "Electives:")
              if table_cell.find("sup"):
                text = str(unidecode(text + " " + table_cell.find("sup").text)).strip()
                if text:
                  tracks_for_course[f"track_{track}"][year_cnt][semester_cnt][text] = {}
              
              if text:
                sub_dictionary_key = text
                tracks_for_course[f"track_{track}"][year_cnt][semester_cnt][text] = {}
        
        i += 1
      
      if course_related_info_table.find_next_sibling("dl"):
        tracks_for_course[f"track_{track}"]["extra_course_related_info"] = {}
        extra_course_related_info = course_related_info_table.find_next_sibling("dl")
        dt = extra_course_related_info.find_all("dt")
        dd = extra_course_related_info.find_all("dd")
        
        for i in range(len(dt)):
          key = str(unidecode(dt[i].text)).strip()
          value = str(unidecode(dd[i].text)).strip()
          tracks_for_course[f"track_{track}"]["extra_course_related_info"][key] = value
      
      track += 1
    
    return tracks_for_course


  def __structurize_scrapped_data(self,
                                  tracks_for_course: dict) -> dict | bool:
    """
    To structurize the scrapped data into a structured JSON format with complete information
    about the course code, course name, credits, contact hours, pre-requisites, co-requisites
    and course description for all the tracks.

    Args:
      - tracks_for_course (dict): The scrapped data for all the tracks
    
    Returns:
      - dict: The structured JSON response for the scrapped data
    """

    try:
      already_fetch_courses = {}
      more_informative_tracks_for_course = {}

      for track in tracks_for_course:
        more_informative_tracks_for_course[track] = {}

        for year in tqdm(
          iterable=tracks_for_course[track],
          desc=f"Scrapping for Track \"{track}\": ",
          total=len(tracks_for_course[track])  
        ):
          more_informative_tracks_for_course[track][str(year)] = {}

          if year == "extra_course_related_info":
            more_informative_tracks_for_course[track][str(year)] = tracks_for_course[track][year]
            continue
          
          for semester in tracks_for_course[track][year]:
            more_informative_tracks_for_course[track][str(year)][str(semester)] = {}

            for course in tracks_for_course[track][year][semester]:
              more_informative_tracks_for_course[track][str(year)][str(semester)][course] = {}

              if "elective" in course.lower() and "course_link" not in tracks_for_course[track][year][semester][course].keys() and any("course_link" not in tracks_for_course[track][year][semester][course][key].keys() for key in tracks_for_course[track][year][semester][course].keys()):
                more_informative_tracks_for_course[track][str(year)][str(semester)][course]["course_description"] = ""
                numbers = [int(num) for num in re.findall(r'\d+', course)]
                if len(numbers) > 0:
                  for n in numbers:
                    data = str(tracks_for_course[track]["extra_course_related_info"][str(n)]).strip()
                    if data[-1] != ".":
                      data += "."
                    more_informative_tracks_for_course[track][str(year)][str(semester)][course]["course_description"] += str(tracks_for_course[track]["extra_course_related_info"][str(n)]) +" "
                continue

              if "course_link" in tracks_for_course[track][year][semester][course].keys():
                if tracks_for_course[track][year][semester][course]["course_link"] not in already_fetch_courses.keys():
                  course_related_info = self.__formulate_api_response(
                    api_url=tracks_for_course[track][year][semester][course]["course_link"]
                  )
                  if course_related_info:
                    more_informative_tracks_for_course[track][str(year)][str(semester)][course] = {
                      "course_code": course_related_info["course_code"],
                      "course_name": course_related_info["course_name"],
                      "credits": course_related_info["credits"],
                      "contact_hours": course_related_info["contact_hours"],
                      "prerequisites": course_related_info["prequisites"],
                      "prerequisites_description": course_related_info["prerequisites_description"],
                      "corequisites": course_related_info["corequisites"],
                      "course_description": course_related_info["course_description"],
                      "course_link": tracks_for_course[track][year][semester][course]["course_link"]
                    }
                  else:
                    more_informative_tracks_for_course[track][str(year)][str(semester)][course] = {
                      "course_link": tracks_for_course[track][year][semester][course]["course_link"]
                    }
                  already_fetch_courses[tracks_for_course[track][year][semester][course]["course_link"]] = more_informative_tracks_for_course[track][str(year)][str(semester)][course]
                else:
                  more_informative_tracks_for_course[track][str(year)][str(semester)][course] = already_fetch_courses[tracks_for_course[track][year][semester][course]["course_link"]]

              elif "course_link" not in tracks_for_course[track][year][semester][course].keys():
                for key in tracks_for_course[track][year][semester][course].keys():
                  key = str(key)
                  if "course_link" in tracks_for_course[track][year][semester][course][key].keys():
                    if tracks_for_course[track][year][semester][course][key]["course_link"] not in already_fetch_courses.keys():
                      course_related_info = self.__formulate_api_response(
                        api_url=tracks_for_course[track][year][semester][course][key]["course_link"]
                      )
                      if course_related_info:
                        more_informative_tracks_for_course[track][str(year)][str(semester)][course][key] = {
                          "course_code": course_related_info["course_code"],
                          "course_name": course_related_info["course_name"],
                          "credits": course_related_info["credits"],
                          "contact_hours": course_related_info["contact_hours"],
                          "prequisites": course_related_info["prequisites"],
                          "prerequisites_description": course_related_info["prerequisites_description"],
                          "corequisites": course_related_info["corequisites"],
                          "course_description": course_related_info["course_description"],
                          "course_link": tracks_for_course[track][year][semester][course][key]["course_link"]
                        }
                      else:
                        more_informative_tracks_for_course[track][str(year)][str(semester)][course][key] = {
                          "course_link": tracks_for_course[track][year][semester][course][key]["course_link"]
                        }
                    else:
                      more_informative_tracks_for_course[track][str(year)][str(semester)][course][key] = already_fetch_courses[tracks_for_course[track][year][semester][course][key]["course_link"]]

        self.database_handler.add_course_catalog_information(
          course_catalog_information=more_informative_tracks_for_course[track].copy(),
        )

      return more_informative_tracks_for_course
    
    except Exception as e:
      self.logger.error(f"Error related to structurizing scrapped data: {e}, line: {e.__traceback__.tb_lineno}, in file: {__file__}")
      return False
    

  def scrape_course_catalog(self,
                            url_to_course_catalog: str) -> dict | bool:
    """
    To scrape the course catalog data for a particular major/minor from the NJIT website.

    Args:
      - url_to_course_catalog (str): The URL to the course catalog page

    Returns:
      - dict: The course catalog data for a particular major/minor from the NJIT website
    """
    
    start = time()
    
    tracks_for_course = self.__scrape_course_data(
      url_to_course_catalog=url_to_course_catalog
    )
    
    structured_complete_scrapped_data = self.__structurize_scrapped_data(
      tracks_for_course=tracks_for_course,
    )
    

    end = time()

    hrs, mins = divmod(end - start, 3600)
    mins, secs = divmod(mins, 60)
    time_taken = f"{int(hrs)} hours, {int(mins)} minutes and {int(secs)} seconds"

    if type(structured_complete_scrapped_data) == dict:
      self.logger.info(
        message=f"Scraping the course catalog website with URL: {url_to_course_catalog} is successful! Time taken: {time_taken}"
      )
      return structured_complete_scrapped_data
    else:
      self.logger.error(
        message=f"Scraping the course catalog website with URL: {url_to_course_catalog} failed! Time taken: {time_taken}"
      )
      return False
