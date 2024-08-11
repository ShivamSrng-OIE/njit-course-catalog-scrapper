import os
import json
from datetime import datetime


class LoggingHandler:
  def __init__(self) -> None:
    if os.path.exists("logfile.json"):
      with open("logfile.json", "r") as f:
        self.log_data = json.load(f)
    else:
      self.log_data = {}
    
  
  def info(self,
            message: str) -> None:
    if datetime.now().strftime("%Y-%m-%d") not in self.log_data:
      self.log_data[datetime.now().strftime("%Y-%m-%d")] = []

    self.log_data[datetime.now().strftime("%Y-%m-%d")].append(
      {
        "level": "info",
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      }
    )

    with open("logfile.json", "w") as f:
      json.dump(self.log_data, f, indent=2)
  

  def warning(self,
            message: str) -> None:
    if datetime.now().strftime("%Y-%m-%d") not in self.log_data:
      self.log_data[datetime.now().strftime("%Y-%m-%d")] = []

    self.log_data[datetime.now().strftime("%Y-%m-%d")].append(
      {
        "level": "warning",
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      }
    )

    with open("logfile.json", "w") as f:
      json.dump(self.log_data, f, indent=2)


  def debug(self,
            message: str) -> None:
    if datetime.now().strftime("%Y-%m-%d") not in self.log_data:
      self.log_data[datetime.now().strftime("%Y-%m-%d")] = []
    
    self.log_data[datetime.now().strftime("%Y-%m-%d")].append(
      {
        "level": "debug",
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      }
    )

    with open("logfile.json", "w") as f:
      json.dump(self.log_data, f, indent=2)
  

  def error(self,
            message: str) -> None:
    if datetime.now().strftime("%Y-%m-%d") not in self.log_data:
      self.log_data[datetime.now().strftime("%Y-%m-%d")] = []

    self.log_data[datetime.now().strftime("%Y-%m-%d")].append(
      {
        "level": "error",
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      }
    )
    
    with open("logfile.json", "w") as f:
      json.dump(self.log_data, f, indent=2)