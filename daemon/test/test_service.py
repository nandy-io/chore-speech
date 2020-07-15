import unittest
import unittest.mock

import os
import json

import service


class MockRedis(object):

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.channel = None
        self.messages = []

    def pubsub(self):

        return self

    def subscribe(self, channel):

        self.channel = channel

    def get_message(self):

        return self.messages.pop(0)


class TestService(unittest.TestCase):

    @unittest.mock.patch.dict(os.environ, {
        "REDIS_HOST": "most.com",
        "REDIS_PORT": "667",
        "REDIS_CHANNEL": "stuff",
        "SPEECH_API": "http://boast.com",
        "SLEEP": "0.7"
    })
    @unittest.mock.patch("redis.StrictRedis", MockRedis)
    def setUp(self):

        self.daemon = service.Daemon()

    @unittest.mock.patch.dict(os.environ, {
        "REDIS_HOST": "most.com",
        "REDIS_PORT": "667",
        "REDIS_CHANNEL": "stuff",
        "SPEECH_API": "http://boast.com",
        "SLEEP": "0.7"
    })
    @unittest.mock.patch("redis.StrictRedis", MockRedis)
    def test___init___(self):

        daemon = service.Daemon()

        self.assertEqual(daemon.redis.host, "most.com")
        self.assertEqual(daemon.redis.port, 667)
        self.assertEqual(daemon.channel, "stuff")
        self.assertEqual(daemon.speech_api, "http://boast.com/speak")
        self.assertEqual(daemon.sleep, 0.7)

    def test_subscribe(self):

        self.daemon.subscribe()

        self.assertEqual(self.daemon.redis, self.daemon.pubsub)
        self.assertEqual(self.daemon.redis.channel, "stuff")

    def test_text(self):

        self.assertEqual("ya", self.daemon.text(
            {
                "name": "hey",
                "data": {
                    "text": "ya"
                }
            }
        ))

        self.assertEqual("hey", self.daemon.text(
            {
                "name": "hey",
                "data": {}
            }
        ))

    def test_speech(self):

        self.assertEqual("hey", self.daemon.speech(
            {
                "chore-speech.nandy.io": "hey"
            },
            {
                "data": {
                    "chore-speech.nandy.io": "ya"
                }
            }
        ))

        self.assertEqual("ya", self.daemon.speech(
            {},
            {
                "data": {
                    "chore-speech.nandy.io": "ya"
                }
            }
        ))

    @unittest.mock.patch("requests.post")
    def test_speak(self, mock_post):

        self.daemon.speak("hey", {"node": "unittest"})

        mock_post.assert_has_calls([
            unittest.mock.call("http://boast.com/speak", json={
                "speak": {
                    "text": "hey",
                    "node": "unittest"
                }
            }),
            unittest.mock.call().raise_for_status()
        ])

        mock_post.reset_mock()

        self.daemon.speak(
            "hey",
            {"node": "bump", "language": "cursing"},
            "dude"
        )

        mock_post.assert_has_calls([
            unittest.mock.call("http://boast.com/speak", json={
                "speak": {
                    "text": "dude, hey",
                    "node": "bump",
                    "language": "cursing"
                }
            }),
            unittest.mock.call().raise_for_status()
        ])

    @unittest.mock.patch("requests.post")
    def test_process(self, mock_post):

        self.daemon.subscribe()

        self.daemon.redis.messages = [
            None,
            {"data": 1},
            {
                "data": json.dumps({
                    "kind": "area",
                    "action": "create",
                    "area": {
                        "name": "ya",
                        "data": {
                            "text": "nope"
                        }
                    },
                    "person": {
                        "name": "dude",
                        "data": {}
                    }
                })
            },
            {
                "data": json.dumps({
                    "kind": "area",
                    "action": "create",
                    "area": {
                        "name": "ya",
                        "data": {
                            "text": "the living room"
                        }
                    },
                    "person": {
                        "name": "dude",
                        "data": {
                            "chore-speech.nandy.io": {
                                "node": "unittest"
                            }
                        }
                    }
                })
            },
            {
                "data": json.dumps({
                    "kind": "act",
                    "action": "create",
                    "act": {
                        "name": "ya",
                        "status": "positive",
                        "data": {
                            "text": "put away your towel"
                        }
                    },
                    "person": {
                        "name": "dude",
                        "data": {
                            "chore-speech.nandy.io": {
                                "node": "unittest"
                            }
                        }
                    }
                })
            },
            {
                "data": json.dumps({
                    "kind": "todo",
                    "action": "create",
                    "todo": {
                        "name": "ya",
                        "data": {
                            "text": "mow the lawn"
                        }
                    },
                    "person": {
                        "name": "dude",
                        "data": {
                            "chore-speech.nandy.io": {
                                "node": "unittest"
                            }
                        }
                    }
                })
            },
            {
                "data": json.dumps({
                    "kind": "todos",
                    "chore-speech.nandy.io": {
                        "node": "bump",
                        "language": "cursing"
                    },
                    "todos": [
                        {
                            "name": "hey",
                            "data": {
                                "text": "guys"
                            }
                        }
                    ],
                    "person": {
                        "name": "dude",
                        "data": {
                            "chore-speech.nandy.io": {
                                "node": "unittest"
                            }
                        }
                    }
                })
            },
            {
                "data": json.dumps({
                    "kind": "routine",
                    "action": "create",
                    "routine": {
                        "name": "ya",
                        "data": {
                            "text": "hey"
                        }
                    },
                    "person": {
                        "name": "dude",
                        "data": {
                            "chore-speech.nandy.io": {
                                "node": "unittest"
                            }
                        }
                    }
                })
            },
            {
                "data": json.dumps({
                    "kind": "task",
                    "action": "create",
                    "routine": {
                        "data": {
                            "chore-speech.nandy.io": {
                                "node": "bump",
                                "language": "cursing"
                            }
                        }
                    },
                    "task": {
                        "text": "you"
                    },
                    "person": {
                        "name": "dude",
                        "data": {
                            "chore-speech.nandy.io": {
                                "node": "unittest"
                            }
                        }
                    }
                })
            }
        ]

        self.daemon.process()
        self.daemon.process()
        self.daemon.process()

        mock_post.reset_mock()
        self.daemon.process()
        mock_post.assert_has_calls([
            unittest.mock.call("http://boast.com/speak", json={
                "speak": {
                    "text": "dude, you are now responsibile for the living room.",
                    "node": "unittest"
                }
            }),
            unittest.mock.call().raise_for_status()
        ])

        mock_post.reset_mock()
        self.daemon.process()
        mock_post.assert_has_calls([
            unittest.mock.call("http://boast.com/speak", json={
                "speak": {
                    "text": "dude, it is good you put away your towel.",
                    "node": "unittest"
                }
            }),
            unittest.mock.call().raise_for_status()
        ])

        mock_post.reset_mock()
        self.daemon.process()
        mock_post.assert_has_calls([
            unittest.mock.call("http://boast.com/speak", json={
                "speak": {
                    "text": "dude, 'mow the lawn' has been added to your ToDo list.",
                    "node": "unittest"
                }
            }),
            unittest.mock.call().raise_for_status()
        ])

        mock_post.reset_mock()
        self.daemon.process()
        mock_post.assert_has_calls([
            unittest.mock.call("http://boast.com/speak", json={
                "speak": {
                    "text": "dude, these are your current todos:",
                    "node": "bump",
                    "language": "cursing"
                }
            }),
            unittest.mock.call().raise_for_status(),
            unittest.mock.call("http://boast.com/speak", json={
                "speak": {
                    "text": "guys",
                    "node": "bump",
                    "language": "cursing"
                }
            }),
            unittest.mock.call().raise_for_status()
        ])

        mock_post.reset_mock()
        self.daemon.process()
        mock_post.assert_has_calls([
            unittest.mock.call("http://boast.com/speak", json={
                "speak": {
                    "text": "dude, time to hey.",
                    "node": "unittest"
                }
            }),
            unittest.mock.call().raise_for_status()
        ])

        mock_post.reset_mock()
        self.daemon.process()
        mock_post.assert_has_calls([
            unittest.mock.call("http://boast.com/speak", json={
                "speak": {
                    "text": "dude, time to you.",
                    "node": "bump",
                    "language": "cursing"
                }
            }),
            unittest.mock.call().raise_for_status()
        ])

    @unittest.mock.patch("requests.post")
    @unittest.mock.patch("service.time.sleep")
    @unittest.mock.patch("traceback.format_exc")
    @unittest.mock.patch('builtins.print')
    def test_run(self, mock_print, mock_traceback, mock_sleep, mock_post):

        self.daemon.redis.messages = [
            {
                "data": json.dumps({
                    "kind": "routine",
                    "action": "create",
                    "routine": {
                        "name": "ya",
                        "data": {
                            "text": "hey"
                        }
                    },
                    "person": {
                        "name": "dude",
                        "data": {
                            "chore-speech.nandy.io": {
                                "node": "unittest"
                            }
                        }
                    }
                })
            },
            None
        ]

        mock_sleep.side_effect = [Exception("whoops"), Exception("adaisy")]
        mock_traceback.side_effect = ["spirograph", Exception("doh")]

        self.assertRaisesRegex(Exception, "doh", self.daemon.run)

        self.assertEqual(self.daemon.redis, self.daemon.pubsub)
        self.assertEqual(self.daemon.redis.channel, "stuff")

        mock_post.assert_has_calls([
            unittest.mock.call("http://boast.com/speak", json={
                "speak": {
                    "text": "dude, time to hey.",
                    "node": "unittest"
                }
            }),
            unittest.mock.call().raise_for_status()
        ])

        mock_sleep.assert_called_with(0.7)

        mock_print.assert_has_calls([
            unittest.mock.call("whoops"),
            unittest.mock.call("spirograph"),
            unittest.mock.call("adaisy")
        ])