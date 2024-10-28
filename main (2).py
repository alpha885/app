import speech_recognition as sr
from gtts import gTTS
import os
import threading
from playsound import playsound
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window

# Set window size for desktop testing
Window.size = (400, 600)

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks = []
        self.reminders = {}

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # AI Greeting
        self.speak("Hello! I am your task manager. Please input your task below.")

        self.input_task = TextInput(hint_text='Enter your task here', multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.input_task)

        self.add_task_button = Button(text='Add Task', size_hint_y=None, height=50)
        self.add_task_button.bind(on_press=self.add_task)
        layout.add_widget(self.add_task_button)

        self.scroll_view = ScrollView(size_hint=(1, None), size=(400, 300))
        self.task_list = Label(text='Tasks will appear here', size_hint_y=None)
        self.task_list.bind(size=self.task_list.setter('text_size'))
        self.scroll_view.add_widget(self.task_list)
        layout.add_widget(self.scroll_view)

        self.ai_suggestion = Label(text='AI Suggestions will appear here', size_hint_y=None, height=40)
        layout.add_widget(self.ai_suggestion)

        self.voice_command_button = Button(text='Voice Command', size_hint_y=None, height=50)
        self.voice_command_button.bind(on_press=self.voice_command)
        layout.add_widget(self.voice_command_button)

        return layout

    def add_task(self, instance):
        task = self.input_task.text.strip()
        if task:
            self.tasks.append(task)
            self.update_task_list()
            self.input_task.text = ''
            self.suggest_task()
            self.speak(f'Task "{task}" added.')
            Clock.schedule_once(lambda dt: self.set_reminder(task), 3600)  # Set reminder for 1 hour
            Clock.schedule_once(lambda dt: self.follow_up(task), 10)  # Follow up after 10 seconds

    def update_task_list(self):
        self.task_list.text = '\n'.join(self.tasks)

    def suggest_task(self):
        if self.tasks:
            suggestion = f"Consider prioritizing: {self.tasks[0]}"
            self.ai_suggestion.text = suggestion
        else:
            self.ai_suggestion.text = 'No tasks added yet.'

    def speak(self, text):
        tts = gTTS(text=text, lang='en')
        tts.save("speech.mp3")
        threading.Thread(target=lambda: playsound("speech.mp3")).start()

    def voice_command(self, instance):
        threading.Thread(target=self.listen_for_command).start()

    def listen_for_command(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening for voice command...")
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print(f"Command received: {command}")
            self.process_command(command)
        except sr.UnknownValueError:
            self.speak("Sorry, I did not understand that.")
        except sr.RequestError:
            self.speak("Could not request results; check your network connection.")

    def process_command(self, command):
        command = command.lower()
        if 'add task' in command:
            task = command.replace('add task', '').strip()
            if task:
                self.tasks.append(task)
                self.update_task_list()
                self.suggest_task()
                self.speak(f'Task "{task}" added.')
                Clock.schedule_once(lambda dt: self.set_reminder(task), 3600)  # Set reminder for 1 hour
                Clock.schedule_once(lambda dt: self.follow_up(task), 10)  # Follow up after 10 seconds
            else:
                self.speak("I didn't hear a task. Please tell me the task you want to add.")
        else:
            self.speak("I can only add tasks. Please say 'add task' followed by the task description.")

    def set_reminder(self, task):
        self.speak(f"Reminder: You have a task to do: '{task}'")

    def follow_up(self, task):
        self.speak(f"Follow-up: Have you completed your task '{task}'?")

if __name__ == '__main__':
    MainApp().run()
