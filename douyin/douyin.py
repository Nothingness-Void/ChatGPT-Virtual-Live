# -*- coding: utf-8 -*-
import asyncio
import random
from tkinter import *
import pygame
import openai
from gtts import gTTS
import subprocess
from collections import deque
import asyncio
import websockets
import json
import requests

# ChatGPT API的URL和密钥
bot_api_url = "https://openaiapi.elecho.top/v1/chat/completions" # openai的api链接
bot_api_key = "api_key" # 填写你的api-key

# ChatGPT参数
chatgpt_params = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "system", "content": "现在你正在哔哩哔哩直播，你的名字叫XX，你是由XXX制造的AI模型，后面的聊天将会是b站用户和你的互动，且每一条消息与上一条都没有联系，你的回答要尽量简短。"}],# 设置ai预设
    "max_tokens": 1000,# 设置单次回复量（最大）
    "temperature": 0.7,
    "n": 1,
    "stop": "\n"
}

async def get_data():
    async with websockets.connect('ws://127.0.0.1:8888',ping_interval =None) as websocket:
        while True:
        # 接收消息
            message = await websocket.recv()
            message =  json.loads(message,strict=False)

            if(message['Type']==1):
                msg =  json.loads(message['Data'],strict=False)
                nickname = msg['User']['Nickname']
                print(nickname+":"+msg['Content'])
                question = msg['Content']

                # 使用ChatGPT与观众进行对话
                chatgpt_params["messages"].append({"role": "user", "content": question})
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {bot_api_key}"
                }
                response = requests.post(bot_api_url, headers=headers, json=chatgpt_params)
                response_data = response.json()
                answer = response_data["choices"][0]["message"]["content"]
                print(f"[AI回复{nickname}]: {answer}")  # 打印AI回复信息

                putvoice(answer)

            if(message['Type']==5):
                msg =  json.loads(message['Data'],strict=False)
                nickname = msg['User']['Nickname']
                answer = "感谢"+nickname+"送的礼物"
                putvoice(answer)
        await asyncio.Future()  # run forever
def putvoice(answer):
# 设置要合成的文本
        text = answer
        #生成TTS语音
        command = f'edge-tts --voice zh-CN-XiaoyiNeural --text "{answer}" --write-media output.mp3'  # 将 AI 生成的文本传递给 edge-tts 命令
        subprocess.run(command, shell=True)  # 执行命令行指令

        # 初始化 Pygame
        pygame.mixer.init()

        # 加载语音文件
        pygame.mixer.music.load("output.mp3")

        # 播放语音
        pygame.mixer.music.play()

        # 等待语音播放结束
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # 退出临时语音文件
        pygame.mixer.quit()
if __name__ == '__main__': #如果不被调用则并发执行
    asyncio.get_event_loop().run_until_complete(get_data())


	
