import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time
Api_Key="txz9KG1nA4F6"
PROJECT_TOKEN="tcWdjr-ajhFe"
Run_Token="tXGLtkTBBBXt"

response=requests.get(f"https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data",params={"api_key":Api_Key})
data=json.loads(response.text)

class Data:
	def __init__(self,api_key,PROJECT_TOKEN):
		self.api_key=api_key
		self.PROJECT_TOKEN=PROJECT_TOKEN
		self.params={
		'api_key':self.api_key
		}
		self.data=self.get_data()

	def get_data(self): 
		response=requests.get(f"https://www.parsehub.com/api/v2/projects/{self.PROJECT_TOKEN}/last_ready_run/data",self.params)
		data=json.loads(response.text)
		return data
	def get_total_cases(self):
		data=self.data['total']
		for content in data:
			if content['name']=='Coronavirus Cases:':
				return content['value']
	def get_total_deaths(self):
		data=self.data['total']
		for content in data:
			if content['name']=='Deaths:':
				return content['value']
	def get_country_data(self,country):
		data=self.data['country']
		for content in data:
			if content['name'].lower()==country.lower():
				return content
		return "0"
	def get_country_list(self):
		countries=[]
		for country in self.data['country']:
			countries.append(country['name'].lower())
		return countries
	def update_data(self):
		response=requests.post(f"https://www.parsehub.com/api/v2/projects/{self.PROJECT_TOKEN}/run",self.params)
		old_data=self.data

		def poll():
			time.sleep(0.1)
			old_data=self.data
			while True:
				new_data=self.get_data()
				if new_data != old_data:
					self.data=new_data
					print("Data Updated")
					break
				time.sleep(5)

		t=threading.Thread(target=poll)
		t.start()
def speak(text):
	engine=pyttsx3.init()
	engine.say(text)
	engine.runAndWait()
def get_audio():
	r=sr.Recognizer()
	with sr.Microphone() as source:
		print("speak anything")
		audio=r.listen(source)
		said=""
		try:
			said=r.recognize_google(audio)
		except Exception as e:
			print('Exception :' ,str(e))
	return said.lower()
def main():
	print("started program")
	data=Data(Api_Key,PROJECT_TOKEN)
	END_PHRASE="Stop"
	country_list=data.get_country_list()

	TOTAL_PATTERNS={
		re.compile("[\w\s]+ total[\w\s]"):data.get_total_cases,
		re.compile("[\w\s]+ total"):data.get_total_cases,
		re.compile("[\w\s]+ total [\w\s] + death"):data.get_total_deaths,
		re.compile("[\w\s]+ total death"):data.get_total_deaths,

	}
	COUNTRY_PATTERNS={
			re.compile("[\w\s]+ cases [\w\s]+"):lambda country:data.get_country_data(country)['total_cases'],
			re.compile("[\w\s]+ death [\w\s]+"):lambda country:data.get_country_data(country)['total_deaths'],
	}
	UPDATE_COMMAND="update"

	while True:
		print("Listening...")
		text=get_audio()
		print(text)
		result=None
		for pattern,func in TOTAL_PATTERNS.items():
			if pattern.match(text):
				result=func()
				break
		for pattern,func in COUNTRY_PATTERNS.items():
			if pattern.match(text):
				words=set(text.split(" "))
				for country in country_list:
					if country in words:
						result=func(country)
						break
		if text == UPDATE_COMMAND:
			result="data is being updated please wait"
			data.update_data()

		if result:
			speak(result)
		if text.find(END_PHRASE)!=-1:
			print("Exit")
			break
main()