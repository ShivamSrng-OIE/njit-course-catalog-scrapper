import uvicorn
import fastapi
from src.engine import Engine


gemin_course_server = fastapi.FastAPI(
  title="Gemin Course Server",
  description="API for Gemin Course Server",
)

@gemin_course_server.get(
  path='/',
  tags=["Root"],
  description="Welcome to Gemin Course Server",
)
async def hello_world():
  return {
    "message": "Hello, World!"
  }


@gemin_course_server.post(
  path='/scrape_course',
  tags=["NJIT Course Catalog Scraper"],
  description="Scrape NJIT Course Catalog",
)
async def scrape_course(
  course_catalog_name: str,
  course_catalog_url: str
):
  engine = Engine()
  status = engine.scrape_course_catalog_website(
    course_catalog_url=course_catalog_url,
    course_catalog_name=course_catalog_name
  )

  return status


@gemin_course_server.post(
  path='/user_responses',
  tags=["User Responses"],
  description="Get the user responses for the course recommendation",
)
async def user_responses(
    degree_program: str,
    year_and_semester_for_recommendation: str,
    track_academically_focused: str,
):
  engine = Engine()
  status = engine.process_user_responses(
    degree_program=degree_program,
    year_and_semester_for_recommendation=year_and_semester_for_recommendation,
    track_academically_focused=track_academically_focused
  )

  return status

if __name__ == "__main__":
  uvicorn.run(
    app='main:gemin_course_server',
    host="127.0.0.1",
    port=8000
  )