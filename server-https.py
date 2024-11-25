# Windowsのコマンドプロンプトで set GOOGLE_API_KEY=自分のAPIキーを実行しておく

###########################################################
## 以下、Geminiを使うための前処理          ################
###########################################################

import google.generativeai as genai
import os

GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY') #または、GOOGLE_API_KEY="自分のAPIキー"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

import base64
import PIL.Image

###########################################################
## 以下、Webサーバーとして動かすための処理 ################
###########################################################

from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
import socket
import urllib
from urllib.parse import unquote

class MyHandler(SimpleHTTPRequestHandler):

    def htmlheader(self): #httpヘッダーを出力
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        length=self.headers.get('content-length')
        try:
            nbytes=int(length)
        except (TypeError, ValueError):
            nbytes=0
        data=self.rfile.read(nbytes)
        post=urllib.parse.parse_qs(data)

        if (self.path == "/upload"):
             imgurl=post[b'imgurl'][0].decode() #パラメタの取り出し。bが必要！
             imgBin=base64.b64decode(imgurl)
             open("uploaded.png", mode="wb").write(imgBin) #PNGファイルに保存
             
             prompt=post[b'prompt'][0].decode() #パラメタの取り出し。bが必要！
             prompt=unquote(prompt)#日本語文字化け対策
             print(prompt)
                         
             img=PIL.Image.open('./uploaded.png')
             response=model.generate_content([prompt, img])#geminiに質問して回答を得る
             answer = "<b>" + response.text + "</b>" #webブラウザに返信するHTML文を作成する
             print(prompt)
            
             self.htmlheader()
             self.wfile.write(answer.encode("utf-8"))#webブラウザに返信する
             

#openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes

host = socket.gethostbyname(socket.gethostname()) #'localhost'
port = 8000
httpd = HTTPServer((host, port), MyHandler)
httpd.socket = ssl.wrap_socket (httpd.socket, certfile='server.pem', server_side=True)
print('Ready! Now you can access to https://%s:%s' % (host, port))
httpd.serve_forever()


