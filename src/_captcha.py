import twocaptcha
import httpx
from ._utility import Utility, MPrint
console = MPrint()


class Captcha:
    def __init__(self):
        self._client = httpx.AsyncClient()
        self._utils = Utility()
        self.api = self._utils.config["captcha"]["api"]
        self.key = self._utils.config["captcha"]["key"]
    def getBalance(self):
        if self.api == "2captcha.com":
            captcha = twocaptcha.TwoCaptcha(self.key)
            return captcha.balance()
        elif self.api == "anti-captcha.com" or self.api == "capmonster.cloud":
            resp = httpx.post(f"https://api.{self.api}/getBalance", json={"clientKey": self.key}).json()
            if resp.get("errorId") > 0:
                console.f_print(f"Error while getting captcha balance: {resp.get('errorDescription')}")
                return 0.0
            return resp.get("balance")
    async def getCaptcha(self, sitekey: str, rqdata):
        if self.api == "2captcha.com":
            captcha = twocaptcha.TwoCaptcha(self.key)
            return captcha.hcaptcha(sitekey, "https://discord.com", {
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
                "data": rqdata
            })["code"]
        elif self.api == "anti-captcha.com" or self.api == "capmonster.cloud":
            taskId = await self._client.post(f"https://api.{self.api}/createTask", json={"clientKey": self.key, "task": {"type": "HCaptchaTaskProxyless", "websiteURL": "https://discord.com/",
                                                                                                                   "websiteKey": sitekey, "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15", "enterprisePayload": {
                                                                                                                       "rqdata": rqdata,
                                                                                                                       "sentry": True
                                                                                                                   }}}, timeout=30)
            taskId = taskId.json()
            if taskId.get("errorId") > 0:
                print(
                    f"Captcha(createTask) - {taskId.get('errorDescription')}")
                return None
            taskId = taskId.get("taskId")
            solvedCaptcha = None
            while not solvedCaptcha:
                captchaData = await self._client.post(f"https://api.{self.api}/getTaskResult", json={
                    "clientKey": self.key, "taskId": taskId}, timeout=30)
                captchaData = captchaData.json()
                if captchaData["errorId"] > 0:
                    print(
                        f"Captcha(getTaskResult) - {captchaData['errorDescription']}")
                    return None
                if captchaData.get("status") == "ready":
                    solvedCaptcha = captchaData.get(
                        "solution").get("gRecaptchaResponse")
                    return solvedCaptcha
