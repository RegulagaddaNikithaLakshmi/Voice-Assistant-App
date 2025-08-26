from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import requests
import datetime
import json
import threading
import os
import webbrowser
from werkzeug.serving import make_server
import time # Add this import for sleep

app = Flask(__name__)

# NOTE: We will initialize the TTS engine inside the speak method to avoid thread conflicts.
# The global 'tts_engine' variable is no longer needed in this approach.

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def speak(self, text):
        """Convert text to speech"""
        
        # This is the most reliable way to handle pyttsx3 in a web server.
        # Initialize and run the engine for each speaking request.
        # This prevents the blocking and thread-related issues.
        
        # Run TTS in a separate thread to avoid blocking the Flask server
        def run_tts():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 0.9)
                
                print(f"Speaking: {text}")
                engine.say(text)
                engine.runAndWait()
                engine.stop() # Explicitly stop the engine after speaking
            except Exception as e:
                print(f"Error during TTS speak: {e}")

        tts_thread = threading.Thread(target=run_tts, daemon=True)
        tts_thread.start()

    # The rest of your class methods (get_weather, get_news, etc.) remain the same.
    # ... (Keep all your existing methods here) ...
    def get_weather(self, city="Visakhapatnam"):
        """Get weather information"""
        try:
            api_key = "7c19d30d65cb576f4b9b08f7cda19b31"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                return f"The weather in {city} is {temp}°C with {description}"
            else:
                return "Sorry, I couldn't get the weather information"
        except:
            return f"Weather service is currently unavailable. It's a beautiful day in {city}!"

    def get_news(self):
        """Get latest news headlines"""
        try:
            api_key = "2772c391d6e948d0a518235688830fc5"
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                headlines = []
                for article in data['articles'][:3]:
                    headlines.append(article['title'])
                return "Here are the top news headlines: " + ". ".join(headlines)
            else:
                return "Sorry, I couldn't get the news"
        except:
            return "News service is currently unavailable. Stay informed with your favorite news sources!"

    def set_reminder(self, reminder_text, time_str=None):
        """Set a reminder"""
        reminder = {
            'id': len(reminders) + 1,
            'text': reminder_text,
            'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'time': time_str
        }
        reminders.append(reminder)
        return f"Reminder set: {reminder_text}"

    def get_reminders(self):
        """Get all reminders"""
        if not reminders:
            return "You have no reminders"
        
        reminder_list = "Your reminders: "
        for reminder in reminders:
            reminder_list += f"{reminder['text']} (set on {reminder['created_at']}). "
        return reminder_list

    def get_time(self):
        """Get current time"""
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%H:%M %p')}"

    def get_date(self):
        """Get current date"""
        now = datetime.datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}"

    def open_youtube(self, search_query=None):
        """Open YouTube or search for a video"""
        try:
            if search_query:
                search_query = search_query.replace("search for", "").replace("find", "").replace("on youtube", "").strip()
                url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                webbrowser.open(url)
                return f"Opening YouTube and searching for {search_query}"
            else:
                webbrowser.open("https://www.youtube.com")
                return "Opening YouTube"
        except:
            return "Sorry, I couldn't open YouTube"

    def open_google(self, search_query=None):
        """Open Google or search for something"""
        try:
            if search_query:
                search_query = search_query.replace("search for", "").replace("google", "").replace("find", "").strip()
                url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                webbrowser.open(url)
                return f"Opening Google and searching for {search_query}"
            else:
                webbrowser.open("https://www.google.com")
                return "Opening Google"
        except:
            return "Sorry, I couldn't open Google"

    def open_website(self, website_name):
        """Open popular websites"""
        websites = {
            'facebook': 'https://www.facebook.com',
            'twitter': 'https://www.twitter.com',
            'instagram': 'https://www.instagram.com',
            'linkedin': 'https://www.linkedin.com',
            'gmail': 'https://www.gmail.com',
            'whatsapp': 'https://web.whatsapp.com',
            'amazon': 'https://www.amazon.com',
            'netflix': 'https://www.netflix.com',
            'github': 'https://www.github.com',
            'stackoverflow': 'https://stackoverflow.com',
            'wikipedia': 'https://www.wikipedia.org'
        }
        
        website_name = website_name.lower()
        if website_name in websites:
            webbrowser.open(websites[website_name])
            return f"Opening {website_name.title()}"
        else:
            if not website_name.startswith('http'):
                website_name = 'https://www.' + website_name + '.com'
            try:
                webbrowser.open(website_name)
                return f"Opening website: {website_name}"
            except:
                return f"Sorry, I couldn't open {website_name}"

    def process_command(self, command):
        """Process voice command and return response"""
        command = command.lower().strip()
        
        if "hello" in command or "hi" in command or "hey" in command:
            return "Hello! I'm your voice assistant. How can I help you today?"
        
        elif "weather" in command:
            words = command.split()
            city = "Visakhapatnam"
            if "in" in words:
                try:
                    city_index = words.index("in") + 1
                    if city_index < len(words):
                        city = words[city_index]
                except:
                    pass
            return self.get_weather(city)
        
        elif "news" in command:
            return self.get_news()
        
        elif "reminder" in command:
            if "set" in command or "add" in command or "create" in command:
                reminder_text = command.replace("set reminder", "").replace("add reminder", "").replace("create reminder", "").strip()
                reminder_text = reminder_text.replace("to", "", 1).strip()
                if reminder_text:
                    return self.set_reminder(reminder_text)
                else:
                    return "What would you like me to remind you about?"
            else:
                return self.get_reminders()
        
        elif "time" in command:
            return self.get_time()
        
        elif "date" in command or "today" in command:
            return self.get_date()
        
        elif "youtube" in command:
            if "search" in command or "find" in command or "play" in command:
                search_terms = command.replace("youtube", "").replace("search", "").replace("find", "").replace("play", "").replace("on", "").replace("for", "").strip()
                if search_terms:
                    return self.open_youtube(search_terms)
                else:
                    return self.open_youtube()
            else:
                return self.open_youtube()
        
        elif "google" in command:
            if "search" in command or "find" in command:
                search_terms = command.replace("google", "").replace("search", "").replace("find", "").replace("on", "").replace("for", "").strip()
                if search_terms:
                    return self.open_google(search_terms)
                else:
                    return self.open_google()
            else:
                return self.open_google()
        
        elif "open" in command:
            words = command.split()
            if "open" in words:
                open_index = words.index("open")
                if open_index + 1 < len(words):
                    website = words[open_index + 1]
                    return self.open_website(website)
            return "Please specify which website to open"
        
        elif any(site in command for site in ['facebook', 'twitter', 'instagram', 'linkedin', 'gmail', 'whatsapp', 'amazon', 'netflix', 'github', 'stackoverflow', 'wikipedia']):
            for site in ['facebook', 'twitter', 'instagram', 'linkedin', 'gmail', 'whatsapp', 'amazon', 'netflix', 'github', 'stackoverflow', 'wikipedia']:
                if site in command:
                    return self.open_website(site)
        
        elif "stop" in command or "exit" in command or "quit" in command or "bye" in command:
            return "Goodbye! Have a great day!"
        
        elif "what can you do" in command or "help" in command:
            return ("I can help you with: checking weather in Visakhapatnam, getting news, setting reminders, "
                    "telling time and date, opening websites like YouTube and Google, "
                    "searching the web, and much more! Just ask me naturally.")
        
        else:
            return ("I'm sorry, I didn't understand that command. Try asking about weather, news, time, date, "
                    "setting reminders, or ask me to open YouTube, Google, or other websites. "
                    "You can also say 'what can you do' to learn more!")

# Initialize the voice assistant
assistant = VoiceAssistant()
reminders = [] # Reminders are part of the main application state

@app.route('/')
def index():
    greeting = "Hello Nikitha, I am your personal assistant. How can I help you?"
    assistant.speak(greeting)
    return render_template('index.html')

@app.route('/listen', methods=['POST'])
def listen_endpoint():
    try:
        command = assistant.listen()
        if command == "timeout":
            return jsonify({'success': False, 'message': 'No voice input detected'})
        elif command == "could not understand":
            return jsonify({'success': False, 'message': 'Could not understand the audio'})
        elif command.startswith("error"):
            return jsonify({'success': False, 'message': command})
        else:
            return jsonify({'success': True, 'command': command})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/process', methods=['POST'])
def process_endpoint():
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({'success': False, 'message': 'No command provided'})
        
        response = assistant.process_command(command)
        
        # Speak the response
        assistant.speak(response)
        
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/speak', methods=['POST'])
def speak_endpoint():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if text:
            assistant.speak(text)
            return jsonify({'success': True, 'message': 'Speaking...'})
        else:
            return jsonify({'success': False, 'message': 'No text provided'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/reminders')
def get_reminders_endpoint():
    return jsonify({'reminders': reminders})

@app.route('/reminders', methods=['DELETE'])
def clear_reminders():
    global reminders
    reminders = []
    return jsonify({'success': True, 'message': 'All reminders cleared'})

if __name__ == '__main__':
    print("Starting Voice Assistant...")
    print("Make sure you have a microphone connected!")
    # Use threaded=True to ensure Flask can handle multiple requests concurrently
    app.run(debug=True, host='0.0.0.0', port=5000)