from src.utils.logging_handler import LoggingHandler
from src.utils.database_handler import DatabaseHandler
from src.scrape_data.website_scrapper import WebsiteScrapper
from src.scrape_data.improvise_scrapped_data import ImproviseScrappedData
from src.user_interaction.process_user_responses import ProcessUserResponses


class Engine:
  def __init__(self) -> None:
    self.logger = LoggingHandler()
    self.database_handler = DatabaseHandler(
      logger=self.logger
    )
    self.website_scrapper = WebsiteScrapper(
      logger=self.logger,
      database_handler=self.database_handler,
    )
    self.improvise_scrapped_data = ImproviseScrappedData(
      logger=self.logger,
      database_handler=self.database_handler,
    )


  def scrape_course_catalog_website(self,
                                    course_catalog_url: str,
                                    course_catalog_name: str) -> dict:
    """
    Scrapes the course catalog website
    
    Args:
      - course_catalog_url (str): The URL of the course catalog website
      - course_catalog_name (str): The name of the course catalog website
    
    Returns:
      - bool: True if the course catalog website was scraped successfully, False otherwise
    """
    
    self.logger.info(
      message=f"Scraping the {course_catalog_name}'s course catalog website with URL: {course_catalog_url}"
    )

    course_catalog_name = course_catalog_name.replace(" ", "_").lower()

    self.database_handler.create_collection_for_course_catalog(
      course_name=course_catalog_name,
    )
    self.database_handler.create_collection_for_track_information(
      course_name=course_catalog_name,
    )

    structured_complete_scrapped_data = self.website_scrapper.scrape_course_catalog(
      url_to_course_catalog=course_catalog_url,
    )
    
    if structured_complete_scrapped_data == False:
      return {
        "message": f"Failed to scrape the course catalog website of {course_catalog_name}, with URL: {course_catalog_url}",
      }
    
    all_tracks_information = self.improvise_scrapped_data.run(
      course_name=course_catalog_name,
      course_catalog=structured_complete_scrapped_data,
    )
    
    if all_tracks_information == False:
      return {
        "message": f"Failed to improvise the scrapped data of the course catalog website of {course_catalog_name}, with URL: {course_catalog_url}",
      }
    
    return {
      "message": f"Successfully scraped the course catalog website of {course_catalog_name}, with URL: {course_catalog_url}",
    }
  
  def process_user_responses(self,
                             degree_program: str,
                             year_and_semester_for_recommendation: str,
                             track_academically_focused: str) -> dict:
      """
      Processes the user responses
      
      Args:
        - degree_program (str): The degree program of the user
        - semester_for_recommendation (str): The semester for which the user wants the course recommendations
        - track_academically_focused (str): The track the user is academically focused on
      
      Returns:
        - dict: The status of the user responses processing
      """
      
      self.logger.info(
        message=f"Processing the user responses for the degree program: {degree_program}, semester for recommendation: {year_and_semester_for_recommendation}, and track academically focused: {track_academically_focused}"
      )
      recommended_courses = ProcessUserResponses()
      return {
        "message": f"Successfully processed the user responses for the degree program: {degree_program}, semester for recommendation: {year_and_semester_for_recommendation}, and track academically focused: {track_academically_focused}"
      }
  

  def run(self) -> None:
    pass