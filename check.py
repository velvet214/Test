import requests
import re
import time
from email import policy
from email.parser import Parser
from email.iterators import _structure
from html2text import html2text
from openai import AzureOpenAI

def main():
    extractEmail("uploadedEmail.eml")



def extractEmail(filename):
    with open(filename) as file:
        message = Parser(policy=policy.default).parse(file)

    text = ""
    urls = files = []

    for part in message.walk():
        if part.is_attachment():
            filename = part.get_filename()
            files.append(filename)
            with open(filename, "wb") as target:
                target.write(part.get_payload(decode=True))
        else:
            text += str(part.get_payload(decode=True))

    regex = re.compile("<a[^>]+href=[\"\'](.+?)[\"\'][^>]*>.*?</a>")
    urls = regex.findall(text)

    regex2 = re.compile("https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")
    urls.extend(regex2.findall(text))

    plainText = html2text(text)

    return urls, files, plainText



def chatbotResponse(userInput):
    client = AzureOpenAI(
        azure_endpoint = "https://leon-test.openai.azure.com/",
        api_key = "c34e12bb4d9a4fb9a9dc5e813f6608d5",
        api_version = "2024-04-01-preview"
    )
    response = client.chat.completions.create(
        model = "leon01",
        messages = [
            {"role" : "system", "content" : "You are an assistant responsible for checking emails."},
            {"role" : "user", "content" : userInput}
        ]
    )
    return response.choices[0].message.content



def decodeUrls(inputUrls):
    url = "https://tap-api-v2.proofpoint.com/v2/url/decode"
    json = {"urls" : inputUrls}
    response = requests.post(url, json=json)

    if response.status_code == 200:
        data = response.json()
        urls = []
        for result in data["urls"]:
            if(result["success"]):
                urls.append(result["decodedUrl"])
            else:
                urls.append(result["encodedUrl"])
        return urls
    else:
        return None



def obfuscateApiKey():
    seed = ""
    now = int(time.time() * 1000)
    n = str(now)[-6:]
    r = str(int(n) >> 1).zfill(6)
    key = ""
    for i in range(0, len(str(n)), 1):
        key += seed[int(str(n)[i])]
    for j in range(0, len(str(r)), 1):
        key += seed[int(str(r)[j])+2]

    print("Timestamp:", now, "\tKey", key)
    return key



def authenticateZscaler():
    url = "https://zsapi.zscalertwo.net/api/v1/authenticatedSession"
    headers = {
        "Content-Type" : "application/json",
        "Cache-Control" : "no-cache"
    }
    json = {
        "apiKey" : obfuscateApiKey(),
        "username" : "",
        "password" : "",
        "timestamp" : time.time()
    }
    response = requests.post(url, json=json, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None



def verifyUrls(inputUrls):
    url = "https://zsapi.zscalertwo.net/api/v1/urlLookup"
    headers = {"Content-Type" : "application/json",
               "Authorization" : "Bearer ",
               "Cache-Control" : "no-cache"}
    json = {"urls" : inputUrls}
    response = requests.post(url, json=json, headers=headers)

    if response.status_code == 200:
        data = response.json()
        urls = []
        for result in data:
            if result["urlClassificationsWithSecurityAlert"]:
                urls.append(result["url"])
        return urls
    else:
        return None



def verifyFiles(file):
    url = "https://www.virustotal.com/api/v3/files"
    headers = {
        "accept": "application/json",
        "content-type": "multipart/form-data",
        "x-apikey" : ""
    }
    response = requests.post(url, headers=headers, file=file)
    print(response.text)



if __name__ == "__main__":
    main()