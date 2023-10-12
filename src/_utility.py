import random, json, re
from httpx import Client
from colorama import Fore, Style
from base64 import b64encode as b
import httpx
class Utility:
    def __init__(self):
        self.config = self.getConfig()
        self.proxy = self.getProxy()
    def getConfig(self):
        return json.loads(open("config.json").read())
    def getProxy(self):
        if self.config["proxy"]["proxyless"]:
            return None
        return f"{self.config['proxy']['protocol']}://{random.choice(open('input/proxies.txt').read().splitlines())}"
    def getBuildNum(self):
        """Gets the build number that discord is currently on, makes the x-super-properties header more realistic."""
        #client = Client()
        #asset = re.compile(r'([a-zA-z0-9]+)\.js', re.I).findall(client.get(f'https://discord.com/app', headers={'User-Agent': 'Mozilla/5.0'}).read().decode('utf-8'))[-1]
        #fr = client.get(f'https://discord.com/assets/{asset}.js', headers={'User-Agent': 'Mozilla/5.0'}).read().decode('utf-8')
        #return str(re.compile('Build Number: [0-9]+, Version Hash: [A-Za-z0-9]+').findall(fr)[0].replace(' ', '').split(',')[0].split(':')[-1]).replace(' ', '')
        return "133852"
    def getContextProperties(self, guildId: str, channelId: str) -> str:
        return b(json.dumps({"location":"Join Guild","location_guild_id":guildId,"location_channel_id":channelId,"location_channel_type":0}, separators=(',', ':')).encode()).decode()
    def getInviteInfo(self, rawInvite):
        res = httpx.get(f'https://discord.com/api/v10/invites/{rawInvite}?with_counts=true', headers={
                             "Authorization": "undefined"}, timeout=30).json()
        return res

class MPrint:
    def w_print(self, message: str):
        """Print warning"""
        print(f"{Fore.WHITE}[{Fore.YELLOW}WARN{Fore.WHITE}] {message}")
    def s_print(self, message: str):
        """Print SUCCESS"""
        print(f"{Fore.WHITE}[{Fore.GREEN}SUCCESS{Fore.WHITE}] {message}")
    def f_print(self, message: str):
        """Print FAIL"""
        print(f"{Fore.WHITE}[{Fore.RED}FAILURE{Fore.WHITE}] {message}")
console = MPrint()