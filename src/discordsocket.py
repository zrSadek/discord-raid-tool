import websocket, threading, json, time
class DiscordSocket(threading.Thread):
    def __init__(self, token: str) -> None:
        self.token = token
        threading.Thread.__init__(self)
        self.ws = websocket.WebSocket()
        self.running = True
    def login(self):
        self.ws.connect("wss://gateway.discord.gg/?encoding=json&v=9")
        interval = self.recieve()["d"]["heartbeat_interval"] / 1000
        threading.Thread(target=self.heartbeat, args=(interval,)).start()
    def heartbeat(self, interval: float):
        while self.running:
            time.sleep(interval)
            self.send_payload({"op": 1, "d": None})
    def recieve(self):
        data = self.ws.recv()
        if data:
            return json.loads(data)
    def send_payload(self, data: dict):
        self.ws.send(json.dumps(data))
    
    def online(self):
        self.send_payload(
            {
                "op": 2,
                "d": {
                    "token": self.token,
                    "capabilities": 125,
                    "properties": {
                        "os": "iOS",
                        "browser": "Safari",
                        "device": "iPhone",
                        "system_locale": "en-US",
                        "browser_user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Mobile/15E148 Safari/604.1",
                        "browser_version": "15.1",
                        "os_version": "15.1",
                        "referrer": "",
                        "referring_domain": "",
                        "referrer_current": "",
                        "referring_domain_current": "",
                        "release_channel": "stable",
                        "client_build_number": 140268,
                        "client_event_source": None,
                    },
                    "presence": {
                        "status": "online",
                        "since": 0,
                        "activities": [
                            {
                                "name": "Custom Status",
                                "type": 4,
                                "state": "VC Spammer",
                                "emoji": None,
                            }
                        ],
                        "afk": False,
                    },
                    "compress": False,
                    "client_state": {
                        "guild_hashes": {},
                        "highest_last_message_id": "0",
                        "read_state_version": 0,
                        "user_guild_settings_version": -1,
                        "user_settings_version": -1,
                    },
                },
            }
        )
    def join_vc(self, channel_id: str, guild_id: str):
        self.send_payload({"op": 4,"d": {"guild_id": guild_id,"channel_id": channel_id,"self_mute": True,"self_deaf": True, "self_stream?": True, "self_video": False}})
        self.send_payload({"op": 18,"d": {"type": "guild","guild_id": guild_id,"channel_id": channel_id,"preferred_region": "singapore"}})
        time.sleep(3)
        self.running = False
        self.ws.close()

    def run(self, channel_id: str, guild_id: str):
        self.login()
        self.online()
        self.join_vc(channel_id, guild_id)
        