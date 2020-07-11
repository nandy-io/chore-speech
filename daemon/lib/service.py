"""
Main module for daemon
"""

import os
import time
import json
import redis
import requests
import traceback

class Daemon(object):
    """
    Main class for daemon
    """

    AREA_STATEMENTS = {
        "create": "you are now responsibile for %s.",
        "wrong": "%s is not up to snuff.",
        "right": "%s is now up to snuff."
    }

    ACT_STATEMENTS = {
        "negative": "you should have %s.",
        "positive": "it is good you %s."
    }

    ACTION_STATEMENTS = {
        "pause": "you do not have to %s yet.",
        "unpause": "you do have to %s now.",
        "skip": "you do not have to %s.",
        "unskip": "you do have to %s.",
        "expire": "your time to %s has expired.",
        "unexpire": "your time to %s has not expired."
    }

    TODO_STATEMENTS = {
        "create": "'%s' has been added to your ToDo list.",
        "complete": "'%s' has beed crossed off your ToDo list.",
        "uncomplete": "'%s' is back on your ToDo list."
    }

    TODO_STATEMENTS.update(ACTION_STATEMENTS)

    ROUTINE_STATEMENTS = {
        "create": "time to %s.",
        "start": "time to %s.",
        "remind": "please %s.",
        "complete": "thank you. You did %s",
        "uncomplete": "I'm sorry but you did not %s yet."
    }

    ROUTINE_STATEMENTS.update(ACTION_STATEMENTS)

    def __init__(self):

        self.sleep = float(os.environ['SLEEP'])

        self.redis = redis.StrictRedis(host=os.environ['REDIS_HOST'], port=int(os.environ['REDIS_PORT']))
        self.channel = os.environ['REDIS_CHANNEL']

        self.speech_api = f"{os.environ['SPEECH_API']}/speak"

        self.pubsub = None

    def subscribe(self):
        """
        Subscribes to the channel on Redis
        """

        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(self.channel)

    @staticmethod
    def text(model):
        return model["data"].get("text", model["name"])

    @staticmethod
    def speech(data, person):
        return data.get("speech", person["data"].get("speech"))

    def speak(self, text, speech, name=None):

        speak = {
            "text": f"{name}, {text}" if name else text
        }

        if not isinstance(speech, dict):
            return

        if "node" in speech:
            speak["node"] = speech["node"]

        if "language" in speech:
            speak["language"] = speech["language"]

        requests.post(self.speech_api, json={"speak": speak}).raise_for_status()

    def process(self):
        """
        Processes a message from the channel if later than the daemons start time
        """

        message = self.pubsub.get_message()

        if not message or isinstance(message["data"], int):
            return

        data = json.loads(message['data'])

        if data["kind"] == "area":

            self.speak(
                self.AREA_STATEMENTS[data["action"]] % self.text(data["area"]),
                self.speech(data["area"]["data"], data["person"]),
                data["person"]["name"]
            )

        elif data["kind"] == "act":

            self.speak(
                self.ACT_STATEMENTS[data["act"]["status"]] % self.text(data["act"]),
                self.speech(data["act"]["data"], data["person"]),
                data["person"]["name"]
            )

        elif data["kind"] == "todo":

            self.speak(
                self.TODO_STATEMENTS[data["action"]] % self.text(data["todo"]),
                self.speech(data["todo"]["data"], data["person"]),
                data["person"]["name"]
            )

        elif data["kind"] == "todos":

            self.speak(
                "these are your current todos:",
                self.speech(data, data["person"]),
                data["person"]["name"]
            )

            for todo in data["todos"]:
                self.speak(self.text(todo), self.speech(data, data["person"]))

        elif data["kind"] == "routine":

            self.speak(
                self.ROUTINE_STATEMENTS[data["action"]] % self.text(data["routine"]),
                self.speech(data["routine"]["data"], data["person"]),
                data["person"]["name"]
            )

        elif data["kind"] == "task":

            self.speak(
                self.ROUTINE_STATEMENTS[data["action"]] % data["task"]["text"],
                self.speech(data["routine"]["data"], data["person"]),
                data["person"]["name"]
            )

    def run(self):
        """
        Runs the daemon
        """

        self.subscribe()

        while True:
            try:
                self.process()
                time.sleep(self.sleep)
            except Exception as exception:
                print(str(exception))
                print(traceback.format_exc())
