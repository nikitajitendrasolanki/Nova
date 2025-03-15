import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import wikipedia
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import pyowm 
import pickle 

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']  # Define SCOPES

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to speak the given text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen to user input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()  # Convert speech to text
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        speak("Sorry, there is an issue with the speech service.")
        return None

# Function to process commands
def process_command(command):
    if 'open google' in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif 'open youtube' in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    elif 'open linkedin' in command:
        speak("Opening linkedln ")
        webbrowser.open("https://www.linkedin.com/in/nikita-datadriven20")

    elif 'what is the time' in command:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        speak(f"The time is {current_time}")

    elif 'play music' in command:
        speak("Playing music")
        # Specify path to a music file
        os.system("start path_to_your_music_file.mp3")  # Update with the correct file path

    elif 'hello' in command:
        speak("Hello! How can I assist you today?")

    elif 'exit' in command or 'goodbye' in command:
        speak("Goodbye! Have a nice day!")
        exit()

    elif 'weather' in command:
        speak("Checking the weather...")
        get_weather()

    elif 'news' in command:
        speak("Fetching the latest news...")
        get_news()

    elif 'send email' in command:
        speak("Whom would you like to send an email to?")
        recipient = listen()
        speak("What is the subject of the email?")
        subject = listen()
        speak("What would you like to say in the email?")
        body = listen()
        send_email(recipient, subject, body)

    elif 'wikipedia' in command:
        speak("Searching Wikipedia...")
        query = command.replace('wikipedia', '')
        results = wikipedia.summary(query, sentences=2)
        speak(f"According to Wikipedia, {results}")

    elif 'calendar' in command:
        speak("Checking your calendar for upcoming events...")
        get_calendar_events()

    else:
        speak("Sorry, I didn't catch that. Please try again.")

# Get weather info using pyowm API
def get_weather():
    API_KEY = 'e7e41cc7987dbadff1da62851d609a12'
    owm = pyowm.OWM(API_KEY)  # Replace with your OpenWeatherMap API key
    mgr = owm.weather_manager()  # Correct way to access weather data
    location = "Mumbai,IN"  # Correct format for city and country code
    observation = mgr.weather_at_place(location)   
    weather = observation.weather
    temp = weather.temperature('celsius')["temp"] 
    status = weather.detailed_status  # Get weather description
    speak(f"The temperature is {temp}°C and the weather is {status}.")
    

# Get the latest news (using NewsAPI)
def get_news():
    url = 'https://newsapi.org/v2/top-headlines?country=us&apiKey=bd66fecb9aef492bb8cb3c6b010c476f'  # Replace with your API key
    response = requests.get(url)
    news = response.json()

    for article in news['articles'][:3]:  # Show top 3 articles
        speak(f"Headline: {article['title']}")
        speak(f"Source: {article['source']['name']}")
        speak(f"Description: {article['description']}")

# Send email
def send_email(recipient, subject, body):
    sender_email = "nikita.232773201@vcet.edu.in"  # Replace with your email address
    sender_password = "Nikita@20"  # Replace with your email password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 465)  # Gmail SMTP server
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient, text)
        server.quit()
        speak(f"Email sent to {recipient}")
    except Exception as e:
        speak(f"Sorry, I couldn't send the email. Error: {str(e)}")

# Function to authenticate Google Calendar API
def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

# Fetch the next event from Google Calendar
def get_calendar_events():
    service = authenticate_google_calendar()
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now, maxResults=1, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        event = events[0]
        speak(f"Upcoming event: {event['summary']} at {event['start']['dateTime']}")

# Main function to start the assistant
def main():
    speak("Initializing Nova... How can I help you?")
    
    while True:
        command = listen()
        if command:
            process_command(command)

# Run the assistant
if __name__ == '__main__':
    main()
