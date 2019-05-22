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

    ROUTINE_STATEMENTS = {
        "start": "time to %s.",
        "remind": "please %s.",
        "pause": "you do not have to %s yet.",
        "unpause": "you do have to %s now.",
        "skip": "you do not have to %s.",
        "unskip": "you do have to %s.",
        "complete": "thank you. You did %s",
        "incomplete": "I'm sorry but you did not %s yet."
    }

    def __init__(self):

        self.sleep = float(os.environ['SLEEP'])

        self.redis = redis.StrictRedis(host=os.environ['REDIS_HOST'], port=int(os.environ['REDIS_PORT']))
        self.channel = os.environ['REDIS_CHANNEL']

        self.speech = f"{os.environ['SPEECH_API']}/speak"

        self.pubsub = None

    def subscribe(self):
        """
        Subscribes to the channel on Redis
        """

        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(self.channel) 

    def speak(self, text, speech=None, name=None):

        message = {
            "timestamp": time.time(),
            "text": f"{name}, {text}" if name else text
        }

        if not isinstance(speech, dict):
            speech = {}

        if "node" in speech:
            message["node"] = speech["node"]

        if "language" in speech:
            message["language"] = speech["language"]

        requests.post(self.speech, json=message).raise_for_status()

    def process(self):
        """
        Processes a message from the channel if later than the daemons start time
        """

        message = self.pubsub.get_message()

        if not message or not isinstance(message["data"], str):
            return

        data = json.loads(message['data'])

        if data["kind"] == "routine" and data["routine"]["data"].get("speech"):

            self.speak(
                self.ROUTINE_STATEMENTS[data["action"]] % data["routine"]["data"]["text"],
                data["routine"]["data"]["speech"],
                data["person"]["name"]
            )

        elif data["kind"] == "task" and data["routine"]["data"].get("speech"):

            self.speak(
                self.ROUTINE_STATEMENTS[data["action"]] % data["task"]["text"],
                data["routine"]["data"]["speech"],
                data["person"]["name"]
            )

        elif data["kind"] == "todo" and data.get("speech"):

            self.speak("these are your current todos:", data["speech"], data["person"]["name"])

            for todo in data["todos"]:
                self.speak(todo["data"]["text"], data["speech"])

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
