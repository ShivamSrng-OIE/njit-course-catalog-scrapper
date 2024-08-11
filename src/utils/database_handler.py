import pymongo
import pymongo.collection
from consts import MondoDBConsts


class DatabaseHandler:
  def __init__(self,
               logger) -> None:
    
    self.logger = logger
    mongo_db_consts = MondoDBConsts().get_constants()
    pymongo_client = pymongo.MongoClient(
      host=mongo_db_consts["host"],
    )
    self.courses_catalog_db = pymongo_client["courses_catalog"]
    self.courses_track_db = pymongo_client["courses_track_information"]
  

  def create_collection_for_course_catalog(self,
                                           course_name: str) -> None:
    """
    Create a collection for the course in the database
    
    Args:
      - course_name (str): The name of the course for which the collection is to be created
    
    Returns:
      - None
    """
    try:
      self.course_catalog_collection = self.courses_catalog_db[course_name]
      return None
    
    except Exception as e:
      self.logger.error(
        message=f"An error '{e}' occurred while creating the collection for the course: {course_name}. At line {e.__traceback__.tb_lineno} in {__file__}.",
      )
      return None


  def create_collection_for_track_information(self,
                                              course_name: str) -> None:
    """
    Create a collection for the track information in the database

    Args:
      - course_name (str): The name of the course for which the collection is to be created
    
    Returns:
      - None
    """

    try:
      self.track_information_collection = self.courses_track_db[course_name]
      return None
  
    except Exception as e:
      self.logger.error(
        message=f"An error '{e}' occurred while creating the collection for the track information of the course: {course_name}. At line {e.__traceback__.tb_lineno} in {__file__}.",
      )
      return None


  def add_course_catalog_information(self,
                                     course_catalog_information: dict) -> None:
    """
    Add the track related information to the course collection
    
    Args:
      - course_collection (pymongo.collection.Collection): The collection for the course
      - track_related_information (dict): The track related information to be added
    
    Returns:
      - None
    """

    try:
      self.course_catalog_collection.insert_one(
        document=course_catalog_information,
      )
      return None

    except Exception as e:
      self.logger.error(
        message=f"An error '{e}' occurred while adding the course catalog information to the MongoDB. At line {e.__traceback__.tb_lineno} in {__file__}.",
      )
      return None
  

  def add_track_information(self,
                            track_information: dict) -> None:
    """
    Add the complete track related information to the track collection

    Args:
      - track_collection (pymongo.collection.Collection): The collection for the track information
      - track_information (dict): The complete track information to be added
    
    Returns:
      - None
    """

    try:
      self.track_information_collection.insert_one(
        document=track_information,
      )
      return None
    
    except Exception as e:
      self.logger.error(
        message=f"An error '{e}' occurred while adding the track information to the MongoDB. At line {e.__traceback__.tb_lineno} in {__file__}.",
      )
      return None
