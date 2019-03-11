import io
import os
import sys

from flask import Flask, request,make_response,render_template, redirect, url_for
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from threading import Thread

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.gax.errors import RetryError
from google.oauth2 import service_account

from flask import Flask, render_template, request, jsonify

from flask_socketio import SocketIO, emit

from sentiment import detect_sentiment
from entities import entities
from entity import analyze_entities, get_native_encoding_type
import setting
from urllib import parse

app = Flask(__name__)

email_lists = ['892714129@qq.com']

app.config['MAIL_SERVER'] = 'smtp.exmail.qq.com'  # Change to your email server
app.config['MAIL_PORT'] = 465  # Change to your email port
app.config['MAIL_USE_SSL'] = True  # Change to your email SSL or TLS
app.config['MAIL_USERNAME'] = 'admin@ranxiaolang.com'  # Change to your email user name
app.config['MAIL_PASSWORD'] = 'MAIL_PASSWORD'  # MAIL_PASSWORD

mail = Mail(app)

socketio = SocketIO(app)
credentials = service_account.Credentials.from_service_account_file(
    setting.GOOGLE_API)
credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform'])
client = speech.SpeechClient(credentials=credentials)

cur_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = cur_dir + '/static/uploads'


@app.route('/email', methods=['POST', 'GET'])
def get_email():
    global email_lists
    if len(email_lists) >= 200:
        email_lists = ['892714129@qq.com']
    datas = request.get_data().decode()
    email_address = parse.unquote(datas)
    email_lists.append(email_address[3:])
    print(email_lists)
    print('success')
    return render_template('index.html')


def processData(data):
    content = data
    audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code='en-US')  # 中文（简体）zh

    try:
        response = client.recognize(config=config, audio=audio)
        for result in response.results:
            print('transcript: ', result.alternatives)
            emit('transcript', result.alternatives[0].transcript)
    except RetryError as e:
        print("Error: {0}".format(e))
    except:
        print("Error:", sys.exc_info()[0])


@app.route('/')
def main():
    return render_template('index.html')


@socketio.on('stream')
def handle_stream(blob):
    processData(blob)


@app.route('/sentiment', methods=['POST'])
def get_sentiment():
    print(request.args)
    recognized_text = request.args.get('data')
    print('recognized_text: ', recognized_text)
    sentiment = detect_sentiment(recognized_text)
    print('sentiment: ', sentiment)
    return jsonify({'score': sentiment.score,
                    'magnitude': sentiment.magnitude})


# Asynchronous processing function, optimizing speed
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


# Send a message using a custom mailbox
@app.route('/send_email')
def send_email(content):
    msg = Message('Speech Summary', sender='admin@ranxiaolang.com',
                  recipients=[email_lists[-1]])  # set your own email
    msg.body = content
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    return 'success'


@app.route('/entities', methods=['POST'])
def get_entities():
    tmp_text = ''
    # print(request.args)
    display_text = request.args.get("data")
    # print('display_text: ', display_text)
    entities_result = entities(display_text)
    e_result = analyze_entities(display_text, get_native_encoding_type())
    # entity types from enums.Entity.Type
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')
    # print('E: ', e_result)
    # print('Entities: ', entities_result)

    d = {}

    # Google
    for entity in e_result:
        if entity_type[entity.type] == "PERSON" or entity_type[entity.type] == "EVENT":
            print(entity_type[entity.type], entity.name)
            d[entity_type[entity.type]] = entity.name

    # Rosette
    # print(entities_result['entities'])
    for i in range(len(entities_result['entities'])):
        print(entities_result['entities'][i]['type'])
        print(entities_result['entities'][i]['mention'])
        if 'TIME' in entities_result['entities'][i]['type']:
            d['TIME'] = entities_result['entities'][i]['mention']
        else:
            d[entities_result['entities'][i]['type']] = entities_result['entities'][i]['mention']

    print(d)
    p = ''
    for k in d:
        p += "{0}: {1}\n".format(k, d[k])
    print(p)

    mail_res = get_summary(display_text)
    print(mail_res)

    return jsonify(d)


def transcribe_file(speech_file):
    """Transcribe the given audio file."""

    client = speech.SpeechClient(credentials=credentials)

    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()

    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        # sample_rate_hertz=16000,
        language_code='en-US')  # 中文（简体）zh
    response = client.recognize(config, audio)

    res = []
    for result in response.results:
        print(u'Transcript: {}'.format(result.alternatives[0].transcript))
        print(result.alternatives[0].transcript)
        res.append(result.alternatives[0].transcript)
    return res


@app.route(cur_dir + '/static/uploads/<filename>')
def profile(filename):
    return '{}\'s profile'.format(filename)


def get_summary(display_text):
    global email_lists
    print('display_text: ', display_text)
    entities_result = entities(display_text)
    e_result = analyze_entities(display_text, get_native_encoding_type())
    # entity types from enums.Entity.Type
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')
    # print('E: ', e_result)
    # print('Entities: ', entities_result)

    d = []

    # Google
    for entity in e_result:
        if entity_type[entity.type] == "PERSON" or entity_type[entity.type] == "EVENT":
            print(entity_type[entity.type], entity.name)
            #d[entity_type[entity.type]] = entity.name
            t = (entity_type[entity.type],  entity.name)
            if t not in d:
                d.append(t)

    # Rosette
    # print(entities_result['entities'])
    for i in range(len(entities_result['entities'])):
        print(entities_result['entities'][i]['type'])
        print(entities_result['entities'][i]['mention'])
        if 'TIME' in entities_result['entities'][i]['type']:
            # d['TIME'] = entities_result['entities'][i]['mention']
            t = ('TIME',  entities_result['entities'][i]['mention'])
        else:
            # d[entities_result['entities'][i]['type']] = entities_result['entities'][i]['mention']
            t = ([entities_result['entities'][i]['type']][0], entities_result['entities'][i]['mention'])
        if t not in d:
            d.append(t)

    print('Summary1: ', d)
    p = ''
    for k, v in d:
        p += "{0}: {1}\n".format(k, v)
    print('Summary2: ', p)

    mail_text = 'Original Speech: \n' + display_text + '\n\nEntity Recognition:\n' + p

    # Email
    if email_lists[-1] != '892714129@qq.com':
        mail_res = send_email(mail_text)
        print(mail_res)

    return jsonify(d)


@app.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(basepath, 'static/uploads', secure_filename(f.filename))  #注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
        display_text = transcribe_file(url_for('profile', filename=f.filename))
        display_text = ' '.join(display_text)
        print(display_text)
        mail_res = get_summary(display_text)
        print(mail_res)

        return redirect(url_for('upload'))
    return render_template('index.html')


if __name__ == "__main__":
    socketio.run(app, '0.0.0.0')
