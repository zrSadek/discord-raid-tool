import os
from httpx import AsyncClient
from ._utility import Utility, MPrint
from ._captcha import Captcha
from base64 import b64encode as encoder
from colorama import Back, Fore, Style
from .discordsocket import DiscordSocket
import websocket
import random
import time
import json as jsonLib
import string
console = MPrint()
BUILD_NUM = Utility().getBuildNum()

#Colors
w = Fore.WHITE
b = Fore.BLACK
g = Fore.GREEN
y = Fore.YELLOW
m = Fore.MAGENTA
c = Fore.CYAN
r = Fore.RED
b = Fore.BLUE
lb = Fore.LIGHTBLUE_EX

class MultiTool:
    """
    # Multitool main class
    """
    async def _init(self, token: str):
        self._utility = Utility()
        self.client = AsyncClient(proxies=self._utility.proxy, cookies={"locale": "en-US"}, headers={
            "Accept": "*/*",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Accept-Language": "en-us",
            "Host": "discord.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
            "Referer": "https://discord.com/",
            "Accept-Encoding": "br, gzip, deflate",
            "Connection": "keep-alive"
        }, timeout=self._utility.config["requestTimeout"])
        self.token = token
        self.client.headers["X-Track"] = self._build_trackers(
            trackerType="x-track")
        res = await self.client.get(
            "https://discord.com/api/v10/experiments")
        try:
            self.client.headers["X-Fingerprint"] = res.json().get("fingerprint")
        except:
            #self.client.headers["X-Fingerprint"] = "992405718051344425.40u0H3W3P2iOxVPP-50_HbyxbcI"
            None # do nothing if fingerprint aint found, cuz fingerprint isn't needed anyways just improves your success rate
        self.client.headers["Origin"] = "https://discord.com/"
        self.client.headers["Authorization"] = token
        self.client.headers["X-Debug-Options"] = "bugReporterEnabled"
        self.client.headers["X-Discord-Locale"] = "en-US"
        self.client.headers["Referer"] = "https://discord.com/channels/@me"
        del self.client.headers["X-Track"]
        self.client.headers["X-Super-Properties"] = self._build_trackers(
            trackerType="x-super-properties")
        self._captcha = Captcha()

    def _build_trackers(self, trackerType: str) -> str:
        """Builds the x-track/x-super-properties header"""
        if trackerType == "x-track":
            return encoder(jsonLib.dumps({"os": "Mac OS X", "browser": "Safari", "device": "", "system_locale": "en-us", "browser_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15", "browser_version": "13.1.2", "os_version": "10.13.6", "referrer": "", "referring_domain": "", "referrer_current": "", "referring_domain_current": "", "release_channel": "stable", "client_build_number": 9999, "client_event_source": None}, separators=(',', ':')).encode()).decode()
        elif trackerType == "x-super-properties":
            return encoder(jsonLib.dumps({"os": "Mac OS X", "browser": "Safari", "device": "", "system_locale": "en-us", "browser_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15", "browser_version": "13.1.2", "os_version": "10.13.6", "referrer": "", "referring_domain": "", "referrer_current": "", "referring_domain_current": "", "release_channel": "stable", "client_build_number": BUILD_NUM, "client_event_source": None}, separators=(',', ':')).encode()).decode()
        else:
            raise Exception(
                "Invalid tracker type. Currently support types('x-track', 'x-super-properties')")

    async def join(self, rawInvite: str, ctxProperties: str):
        self.client.headers["X-Context-Properties"] = ctxProperties
        req = await self.client.post(
            f"https://discord.com/api/v10/invites/{rawInvite}", json={})
        if "captcha_key" not in req.json():
            if req.json().get("message") == "The user is banned from this guild.":
                print(f"{w}[{r}BANNED{w}] Token is banned from this server")
                return False, req
            print(
                f"{w}[{lb}JOINER{w}] Joined ({lb}discord.gg/{rawInvite}{w})")
            return True, req
        print(f"{w}[{g}CAPTCHA{w}] Captcha detected, solving thru {self._utility.config.get('captcha').get('api')}")
        captcha_sitekey = req.json()["captcha_sitekey"]
        captcha_rqtoken = req.json()["captcha_rqtoken"]
        captcha_rqdata = req.json()["captcha_rqdata"]
        captcha_key = await self._captcha.getCaptcha(captcha_sitekey, captcha_rqdata)
        req = await self.client.post(f"https://discord.com/api/v10/invites/{rawInvite}", json={
            "captcha_key": captcha_key,
            "captcha_rqtoken": captcha_rqtoken
        })
        if req.status_code == 200:
            print(
                f"{w}[{lb}JOINER{w}] Joined ({lb}discord.gg/{rawInvite}{w})")
            return True, req
        else:
            print(
                f"{w}[{r}JOINER{w}] Failed to join ({lb}discord.gg/{rawInvite}{w})")
            return False, req

    async def bypassScreening(self, guildId: str, rawInvite: str):
        req = await self.client.get(
            f"https://discord.com/api/v10/guilds/{guildId}/member-verification?with_guild=false&invite_code={rawInvite}")
        if req.status_code != 200:
            print(
                f"{w}[{r}BYPASS{w}] Failed to bypass member screen")
            return False
        req = await self.client.put(
            f"https://discord.com/api/v10/guilds/{guildId}/requests/@me", json=req.json())
        print(
            f"{w}[{lb}BYPASS{w}] Successfully bypassed member screen")
        return True

    async def checkToken(self):
        req = await self.client.get(
            "https://discord.com/api/v10/users/@me/affinities/guilds")
        if req.status_code == 403:
            print(f" {w}[{lb}{self.token}{w}] is [{y}LOCKED{w}]")
            return False, "LOCKED"
        elif req.status_code == 401:
            print(f" {w}[{lb}{self.token}{w}] is [{r}INVALID{w}]")
            return False, "INVALID"
        else:
            print(f" {w}[{lb}{self.token}{w}] is [{g}VALID{w}]")
            return True, "VALID"

    async def sendDirectMessage(self, userId: str, message: str):
        """Sends a direct message to <@userId>"""
        channelId, req = await self.__open_dm(userId)
        if channelId == None:
            return None, req  # do nothing if it failed to open dms with <@userId>
        payload = {
            "content": message,
            "tts": False,
            "nonce": self.__random_nonce()
        }
        res = await self.__send_message(payload, channelId)
        if res.status_code == 200:
            return True, res
        else:
            return False, res

    def __random_nonce(self):
        """Returns a random str with numbers only, len=18, this is required for sending messages"""
        return "".join(random.choice(string.digits) for _ in range(18))

    async def __send_message(self, payload: dict, channelId: str):
        return await self.client.post(f'https://discord.com/api/v10/channels/{channelId}/messages', json=payload)

    async def __open_dm(self, userId: str):
        req = await self.client.post(
            "https://discord.com/api/v10/users/@me/channels", json={"recipients": [userId]})
        if req.status_code != 200:
            console.f_print(f"{w}[{r}FAILURE{w}] Users dms are not open")
            return None, req
        else:
            return req.json()['id'], req

    async def sendMessageInChannel(self, message: str, channelId: str, massMention: bool = False, massMentionSize: int = 6):
        scrappedMembers = open("scraped/massmention.txt").read().splitlines()
        if len(scrappedMembers) < 1 and massMention:
            print(
                f"Server has 0 members, mass mention will not work")
            return False
        payload = {
            "content": None,
            "tts": False,
            "nonce": self.__random_nonce()
        }
        if massMention:
            mentions = "".join(
                f'<@{random.choice(scrappedMembers)}> ' for _ in range(massMentionSize))

            payload["content"] = f"{mentions}\n{message}"
        else:
            payload["content"] = message
        req = await self.__send_message(payload, channelId)
        if req.status_code == 200:
            print(
                f"{w}[{lb}SENT{w}] {message}")
            return True
        else:
            print(
                f"{w}[{r}FAILURE{w}] {message}")
            return False

    async def getGuild(self, guildId: str):
        req = await self.client.get(f"https://discord.com/api/v10//guilds/{guildId}")
        if "name" not in req.json():
            print(f"{w}[{r}FAILURE{w}] Probably not in {w}[{lb}{guildId}{w}]")
            return req.json()
        return req.json()

    async def getChannel(self, channelId):
        """Returns id of the server the channel is in"""
        req = await self.client.get(
            f"https://discord.com/api/v10/channels/{channelId}")
        if 'guild_id' not in req.json():
            print(f"{w}[{r}FAILURE{w}] Server ID was not found")
            guildId = input(
                f"{w}[{lb}>{w}] Channel ID: ")
            return guildId
        guildId = req.json()["guild_id"]
        if not guildId:
            return None
        return guildId

    async def usernameChange(self, username: str, password: str):
        req = await self.client.patch("https://discord.com/api/v10/users/@me", json={
            "password": password,
            "username": username
        })
        if req.status_code == 200:
            print(f"{w}[{lb}DONE{w}] Username changed to {username}")
        else:
            print(f"{w}[{r}FAILURE{w}] Failed to change username")
        print(f"{w}")
        os.system('pause')

    async def leave(self, guildId: str):
        req = await self.client.delete(
            f"https://discord.com/api/v10/users/@me/guilds/{guildId}")
        if req.status_code != 204:
            print(f"{w}[{r}LEAVER{w}] Failed to leave {w}[{lb}{guildId}{w}]")
            return False
        else:
            print(f"{w}[{lb}LEAVER{w}] Left {w}[{lb}{guildId}{w}]")
            return True
    async def getMessage(self, messageId, channelId):
        """Gets the message, returns a message object 😃"""
        req = await self.client.get(
            f"https://discord.com/api/v10/channels/{channelId}/messages?limit=1&around={messageId}")
        return req.json() 
    async def getReactions(self, messageId, channelId):
        try:
            mesasgeObject = await self.getMessage(messageId, channelId)
            mesasgeObject = mesasgeObject[0]
            reactions = list(mesasgeObject["reactions"])
            if len(reactions) == 0:
                print(f"{w}[{r}FAILURE{w}] No reactions were found")
                return None
            firstEmoji = reactions[0]["emoji"]
            return firstEmoji
        except Exception as e:
            print(e)
            return None
    async def addReaction(self, messageId, channelId, emojiObj):
        try:
            req = await self.client.put(
                f"https://discord.com/api/v10/channels/{channelId}/messages/{messageId}/reactions/{emojiObj}/%40me")
            if req.status_code != 204:
                print(f"{w}[{r}BYPASS{w}] Failed to bypass reaction verification")
                return req.json()
            else:
                print(f"{w}[{lb}BYPASS{w}] Successfully bypassed reaction verification")
                return req.json()
        except Exception as e:
            return None
            
    async def sendFriendRequest(self, username, discrim):
        req = await self.client.post("https://discord.com/api/v10/users/@me/relationships", json={
            "username": username,
            "discriminator": discrim
        })
        if req.status_code != 204:
            print(f"{w}[{r}FAILURE{w}] Failed to send friend request to {username}#{discrim}")
            return req
        else:
            print(f"{w}[{lb}SENT{w}] Sent friend request to {username}#{discrim}")
            return req