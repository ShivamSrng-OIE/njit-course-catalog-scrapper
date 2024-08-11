from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')


class GoogleGeminiConsts:
  """
  A class to store the constants for the Google Gemini API
  """
  
  def __init__(self) -> None:
    self.config = config["GOOGLE_GEMINI_CONSTS"]


  def get_constants(self) -> dict:
    """
    Returns the constants for the Google Gemini API
    
    Args:
      - None
    
    Returns:
      - dict: The constants for the Google Gemini API
    """
    
    return {
      "api_key": self.config.get("api_key"),
      "temperature": self.config.getint("temperature"),
      "generative_model": self.config.get("generative_model"),
      "prompt_for_segregating_fetched_course_description": self.config.get("prompt_for_segregating_fetched_course_description"),
    }


class NJITConsts:
  """
  A class to store the constants for the NJIT website
  """
  
  def __init__(self) -> None:
    self.config = config["NJIT_CONSTS"]


  def get_constants(self) -> dict:
    """
    Returns the constants for the NJIT website
    
    Args:
      - None
    
    Returns:
      - dict: The constants for the NJIT website
    """
    
    return {
      "course_description_api": self.config.get("course_description_api"),
    }


class MondoDBConsts:
  """
  A class to store the constants for the MongoDB database
  """
  
  def __init__(self) -> None:
    self.config = config["MONGODB_CONSTS"]


  def get_constants(self) -> dict:
    """
    Returns the constants for the MongoDB database
    
    Args:
      - None
    
    Returns:
      - dict: The constants for the MongoDB database
    """
    
    username = self.config.get("username")
    password = self.config.get("password")
    cluster = self.config.get("cluster")
    host = f"mongodb+srv://{username}:{password}@{cluster}.e00xjor.mongodb.net/"

    return {
      "host": host,
    }