# speech-box

<div align="center">
    <a href=""><img src="https://i.loli.net/2019/02/25/5c72f38e2e4d0.png" width="200" hegiht="200"/></a>
</div>
<br>

## Introduction  
This Flask web app can provide speech to text, sentiment analysis and words summary.

## Features  
- [x] Real time speech to text recording.
- [X] Sentiment detection
- [X] Words or conversation summary.
- [x] Set your email for summary copy

## Run the code local:  
1. Clone this repository:
```
git clone https://github.com/angryducks/speech-box
```
2. Enter into `speech-box`  folder, set up virtual environment with **python 3.6** and install packages.
```
 cd speech-box
 pip3 install -r requirements.txt
```
3. Update API key

Create Google Cloud Platform API key: https://console.cloud.google.com  
Location: create `./speech-box/<your project ID>.json`  
Change the json file name to `google-api.json`  

Create rosette api key: https://www.rosette.com  
Location: `./speech-box/entity.py`  
key = 'Your rosette api key'    

Email key:    
Location: `./speech-box/main.py`  
EMAIL_HOST_PASSWORD  

4. Run server on your own computer:
```
export FLASK_APP=main.py
flask run --host=0.0.0.0
```
5. Access though browser
```
http://127.0.0.1:5000
or
http://0.0.0.0:5000
```

## Author  
1. [nature1995](https://github.com/nature1995) | Ziran Gong
2. [zfz](https://github.com/zfz) | Fangzhou Zhang
3. [zzdqqqq](https://github.com/zzdqqqq) | Zidong Zhang

