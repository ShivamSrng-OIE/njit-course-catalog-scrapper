import google.generativeai as genai
from consts import GoogleGeminiConsts


class ProcessUserResponses:
  def __init__(self) -> None:
    pass
  

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
    generative_model = google_gemini_consts["generative_model"]

    genai.configure(
      api_key=api_key,
    )

    
  def get_recommendations(self,
                          degree_program: str,
                          semester_for_recommendation: str,
                          track_academically_focused: str) -> dict:
    """
    Gets the course recommendations for the user based on the user responses
    
    Args:
      - degree_program (str): The degree program of the user
      - semester_for_recommendation (str): The semester for which the user wants the course recommendations
      - track_academically_focused (str): The track the user is academically focused on
    
    Returns:
      - dict: The course recommendations for the user including a proper description and reasoning for the recommendations
    """
    
    pass