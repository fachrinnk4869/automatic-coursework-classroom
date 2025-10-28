import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses",
    "https://www.googleapis.com/auth/classroom.coursework.students"
]


def main():
  """Shows basic usage of the Classroom API.
  Creates a course and then creates an assignment for that course.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token1.json"):
    creds = Credentials.from_authorized_user_file("token1.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token1.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("classroom", "v1", credentials=creds)

    # === 1. CREATE A COURSE ===
    print("Creating course...")
    course = {
        'name': 'Go To Google',
        'section': 'Minimal bisa Hard LeetCode tanpa GPT',
        'descriptionHeading': 'Welcome to mode barbar',
        'description': 'Ini course dibuat untuk mode barbar selama 2 bulan masuk Google',
        'ownerId': 'me',  # 'me' indicates the authenticated user
        'courseState': 'PROVISIONED' # Use 'PROVISIONED' then change to 'ACTIVE'
    }
    
    new_course = service.courses().create(body=course).execute()
    new_course_id = new_course.get('id')
    print(f"Course created: {new_course.get('name')} (ID: {new_course_id})")

  except HttpError as error:
    print(f"An error occurred: {error}")
    if error.resp.status == 403:
        print("Error 403: Permission denied. ")
        print("- Did you delete token.json after changing scopes?")
        print("- Does the user have permission to create courses (e.g., is a teacher)?")


if __name__ == "__main__":
  main()