import asyncio
from playwright.async_api import async_playwright
import time
from playsound import playsound
import os
import subprocess
from threading import Thread
import shutil
import requests

currentFileIndex = 0

queueStarted = False

currentPlayingIndex = 0

duration = (4.70588235294 * 60) * 30

def startAudioQueue():
    time.sleep(10)
    global currentPlayingIndex, duration
    originalLength = 4
    clipLength = 4.70588235294 #4.21052631579 #95% #4.70588235294 #85%
    tempo =  originalLength / clipLength
    for i in range(int(duration / clipLength)):
        if currentPlayingIndex > 3:
            os.remove("queuedAudio/" + str(currentPlayingIndex - 4).rjust(5, "0") + ".ts")
            os.remove('queuedAudio/' + str(currentPlayingIndex - 4).rjust(5, "0") + '-slow.wav')

        os.startfile(os.getcwd().replace("\\", "/") + "/queuedAudio/" + str(currentPlayingIndex).rjust(5, "0") + "-slow.wav")

        time.sleep(clipLength)

        currentPlayingIndex = currentPlayingIndex + 1
    
    time.sleep(1)
    shutil.rmtree("queuedAudio")
    os.mkdir("queuedAudio")

def onRequest(request):
    return
    #print(request.method + " Request: " + request.url)

async def onResponse(response):
    global currentFileIndex
    global queueStarted
    originalLength = 4
    clipLength = 4.70588235294
    tempo =  originalLength / clipLength
    if response.request.method == "GET" and "msl4" in  response.request.url:
        with open("queuedAudio/" + str(currentFileIndex).rjust(5, "0") + ".ts", "wb+") as t:
            t.write(await response.body())
            os.system('ffmpeg -y -i queuedAudio/' + str(currentFileIndex).rjust(5, "0") + '.ts -filter:a "atempo=' + str(tempo) + '" -vn queuedAudio/' + str(currentFileIndex).rjust(5, "0") + '-slow.wav -loglevel quiet')

            currentFileIndex = currentFileIndex + 1
            if queueStarted == False:
                queueStarted = True
                thread = Thread(target = startAudioQueue)
                thread.start()
        

async def run(playwright):
    global duration
    firefox = playwright.firefox
    browser = await firefox.launch(headless=False)
    page = await browser.new_page()
    await page.goto("https://www.francetvinfo.fr/en-direct/radio.html")

    await page.mouse.click(340, 450)
    time.sleep(1)
    await page.mouse.click(870, 560)

    time.sleep(0.1)
    await page.mouse.click(963, 472)
    time.sleep(0.1)
    await page.mouse.click(963, 472)

    page.on("request", onRequest)
    page.on("response", onResponse)

    await page.wait_for_timeout(duration * 1000)

    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())