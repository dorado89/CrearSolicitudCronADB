from time import sleep
import datetime
import Settings
import json
import subprocess
from SQSConnection import SQSConnection


def execute_test(script,urlapk):
    txt = script
    subprocess.Popen([format(Settings.ANDROID_HOME) + "/emulator/emulator", '-avd', 'Pixel_2_API_28'])
    subprocess.run(['wget','-N',urlapk])
    sleep(500)
    subprocess.run([format(Settings.ANDROID_HOME) + "/platform-tools/adb", 'install',urlapk.rsplit('/',1)[-1]])
    output = subprocess.call([format(Settings.ANDROID_HOME) + "/platform-tools/adb",'shell','monkey',txt])
    subprocess.run([format(Settings.ANDROID_HOME) + "/platform-tools/adb", 'shell', 'reboot','-p'])
    sleep(500)
    subprocess.run([format(Settings.ANDROID_HOME) + "/emulator/emulator", '-avd', 'Pixel_2_API_28','-wipe-data'])
    if output < 0:
        print('error en ejecución de prueba')

def process():
    try:
        sqs_connection = SQSConnection(Settings.AWS_QUEUE_URL_OUT_ADB)

        with sqs_connection:
            sqs_connection.receive()
            if sqs_connection.message is not '':
                message_body = sqs_connection.message.get('Body')
                msg = json.loads(message_body)
                #Aqui va la conversion del json
                listapruebas = msg[0]["fields"]["pruebas"]
                script=""
                urlapk=""
                for prueba in listapruebas:
                    script=prueba["script"]
                    urlapk=prueba["url_apk"]
                # sqs_connection.delete()
                execute_test(script,urlapk)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    while True:
        process()
        st = str(datetime.datetime.now())
        print(st + ' : alive')
        sleep(Settings.SLEEP_TIME)
