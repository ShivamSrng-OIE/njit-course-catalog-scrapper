from time import time


class ImproviseScrappedData:
  """
  This class is responsible for improvising the scrapped course data by generating the
  path required to complete the course, dependencies, and dependency count.
  """
  
  
  def __init__(self,
               logger,
               database_handler) -> None:
    """
    This method is responsible for initializing the class.
    
    Args:
      - logger: The logger object.
    
    Returns:
      - None
    """
    
    self.logger = logger
    self.databse_handler = database_handler
  

  def __all_track_seperate_information_generation(self) -> dict:
    """
    This method is responsible for generating all track seperate information.
    
    Args:
      - None
    
    Returns:
      - all_tracks_information (dict): A dictionary containing all track's course information.
    """

    try:
      all_tracks_information = {}
      for track in self.course_catalog.keys():
        track_specific_info = {}
        for year in self.course_catalog[track].keys():
          if year == "extra_course_related_info":
            continue
          for semester in self.course_catalog[track][year].keys():
            for course in self.course_catalog[track][year][semester].keys():
              if course not in track_specific_info and "course_link" in self.course_catalog[track][year][semester][course]:
                track_specific_info[course] = self.course_catalog[track][year][semester][course].copy()
                track_specific_info[course]["track"] = track
                track_specific_info[course]["year"] = year
                track_specific_info[course]["semester"] = semester

              elif course not in track_specific_info and "course_link" not in self.course_catalog[track][year][semester][course] and "course_description" not in self.course_catalog[track][year][semester][course]:
                for sub_course in self.course_catalog[track][year][semester][course].keys():
                  track_specific_info[sub_course] = self.course_catalog[track][year][semester][course][sub_course].copy()
                  track_specific_info[sub_course]["track"] = track
                  track_specific_info[sub_course]["year"] = year
                  track_specific_info[sub_course]["semester"] = semester
              
              elif course not in track_specific_info and "course_link" not in self.course_catalog[track][year][semester][course] and "course_description" in self.course_catalog[track][year][semester][course]:
                track_specific_info[course] = self.course_catalog[track][year][semester][course].copy()
                track_specific_info[course]["track"] = track
                track_specific_info[course]["year"] = year
                track_specific_info[course]["semester"] = semester

        all_tracks_information[track] = track_specific_info.copy()
      return all_tracks_information
    
    except Exception as e:
      self.logger.error(
        message=f"An error occurred while generating all track seperate information: {str(e)}, at line {e.__traceback__.tb_lineno} in {__file__}"
      )
      return {}


  def __generate_course_path(self, course_dict, target_course) -> list:
    """
    Generates the path to a target course including all prerequisites and corequisites, and
    also includes information about which courses are prerequisites and corequisites.

    Args:
      - course_dict (dict): Dictionary containing course information.
      - target_course (str): Course code for which the path is to be generated.

    Returns:
      - list: List of lists where each sublist contains [course_code, type]. Type can be 'target course', 'prerequisite', or 'corequisite'.
    """

    def traverse_dependencies(
        course_code: str, 
        visited = None) -> list:
      """
      Traverse the dependencies of a course recursively.

      Args:
        - course_code (str): Course code for which dependencies are to be traversed.
        - visited (set): Set of visited course codes.

      Returns:
        - list: List of lists where each sublist contains [source, destination, relation]. Relation can be 'prerequisite' or 'corequisite'.
      """
      if visited is None:
        visited = set()

      visited.add(course_code)

      course_info = course_dict.get(course_code)
      if not course_info:
        return []

      prerequisites = course_info.get("prerequisites", [])
      corequisites = course_info.get("corequisites", [])
      path = []

      for prerequisite in prerequisites:
        if isinstance(prerequisite, list):
          for item in prerequisite:
            if isinstance(item, str):
              if item not in visited:
                path += traverse_dependencies(item, visited)
                path.append(
                  {
                    "source": item, 
                    "destination": course_code, 
                    "relation": "prerequisite"
                  }
                )
            elif isinstance(item, list):
              sublist_path = traverse_dependencies(item[0], visited)
              path += sublist_path
              path.append(
                {
                  "source": item[0], 
                  "destination": course_code, 
                  "relation": "prerequisite"
                }
              )
        elif isinstance(prerequisite, str):
          if prerequisite not in visited:
            path += traverse_dependencies(prerequisite, visited)
            path.append(
              {
                "source": prerequisite, 
                "destination": course_code, 
                "relation": "prerequisite"
              }
            )
      
      for corequisite in corequisites:
        if isinstance(corequisite, list):
          for item in corequisite:
            if isinstance(item, str):
              if item not in visited:
                path += traverse_dependencies(item, visited)
                path.append(
                  {
                    "source": item, 
                    "destination": course_code, 
                    "relation": "corequisite"
                  }
                )
            elif isinstance(item, list):
              sublist_path = traverse_dependencies(item[0], visited)
              path += sublist_path
              path.append(
                {
                  "source": item[0], 
                  "destination": course_code, 
                  "relation": "corequisite"
                }
              )
        elif isinstance(corequisite, str):
          if corequisite not in visited:
            path += traverse_dependencies(corequisite, visited)
            path.append(
              {
                  "source": corequisite, 
                  "destination": course_code, 
                  "relation": "corequisite"
              }
            )
      return path
    
    path_to_course = traverse_dependencies(target_course)
    return path_to_course
  

  def __generate_path_for_courses_in_all_path(self,
                                              all_tracks_information: dict) -> dict:
    """
    This method is responsible for generating the path for all courses in all tracks.
    
    Args:
      - all_tracks_information (dict): A dictionary containing all track's course information.
    
    Returns:
      - all_tracks_information (dict): A dictionary containing all track's course information along with the path required to complete the course.
    """

    for track in all_tracks_information.keys():
      for course in all_tracks_information[track].keys():
        path_to_course = self.__generate_course_path(
          course_dict=all_tracks_information[track],
          target_course=course
        )
        all_tracks_information[track][course]["complete_path"] = path_to_course
        all_tracks_information[track][course]["on_dependant_courses_count"] = len(path_to_course)

    return all_tracks_information


  def __count_course_dependencies(self, 
                                  course_dict: dict) -> dict:
    """
    This method is responsible for counting the dependencies of a course.

    Args:
      - course_dict (dict): Dictionary containing course information.

    Returns:
      - dependency_counts (dict): Dictionary containing dependency counts.
    """

    dependency_counts = {}

    def count_dependencies(course_list: list):
      """
      This method is responsible for counting the dependencies of a course.
      
      Args:
        - course_list (list): List containing course information.
      
      Returns:
        - None
      """
      
      for course in course_list:
        if isinstance(course, list):
          count_dependencies(course)
        elif isinstance(course, str):
          dependency_counts[course] = dependency_counts.get(course, 0) + 1

    for course_code, course_info in course_dict.items():
      prerequisites = course_info.get("prerequisites", [])
      corequisites = course_info.get("corequisites", [])

      count_dependencies(prerequisites)
      count_dependencies(corequisites)

    return dependency_counts


  def __compute_dependencies(self, 
                             all_tracks_information: dict) -> dict:
    """
    This method is responsible for computing the dependencies.
    
    Args:
      - all_tracks_information (dict): A dictionary containing all track's course information.
    
    Returns:
      - all_tracks_information (dict): A dictionary containing all track's course information along with the dependencies and dependency count.
    """

    for track in all_tracks_information.keys():
      for course in all_tracks_information[track].keys():
        course_dependencies = self.__count_course_dependencies(
          course_dict=all_tracks_information[track]
        ).get(course, 0)
        all_tracks_information[track][course]["dependency_count"] = course_dependencies
      
      all_tracks_information[track] = {
        k: v 
        for k, v in sorted(
          all_tracks_information[track].items(), 
          key=lambda item: item[1]["dependency_count"], 
          reverse=True
        )
      }
      
      self.databse_handler.add_track_information(
        track_information=all_tracks_information[track].copy(),
      )
    return all_tracks_information
  

  def run(self,
          course_name: str,
          course_catalog: dict) -> dict | bool:
    """
    This method is responsible for running the prepare course data process.
    
    Args:
      - course_name (str): The name of the course.
      - course_catalog (dict): The course catalog data.
    
    Returns:
      - all_tracks_information (dict): A dictionary containing all track's course information along with the dependencies and dependency count.
    """

    start = time()
    self.course_name = course_name
    self.course_catalog = course_catalog

    all_tracks_information = self.__all_track_seperate_information_generation()
    all_tracks_information = self.__generate_path_for_courses_in_all_path(
      all_tracks_information=all_tracks_information
    )
    all_tracks_information = self.__compute_dependencies(
      all_tracks_information=all_tracks_information
    )
    end = time()

    hrs, mins = divmod(end - start, 3600)
    mins, secs = divmod(mins, 60)
    time_taken = f"{int(hrs)} hours, {int(mins)} minutes and {int(secs)} seconds"

    if all_tracks_information:
      self.logger.info(
        message=f"Successfully improvised the scrapped course data for {self.course_name}, total time taken: {time_taken}"
      )
      
      return all_tracks_information
    else:
      self.logger.error(
        message=f"Failed to improvise the scrapped course data for {self.course_name}"
      )
      return False