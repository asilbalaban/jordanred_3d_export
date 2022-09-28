#!/usr/bin/python3
import os
import random
from venv import create
import requests
import datetime
import subprocess
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
EXPORT_PATH = os.path.join(CURRENT_PATH, "folder_export")
UPLOAD_PATH = os.path.join(CURRENT_PATH, "folder_upload")
CURRENT_VERSION = "1.0.0"

load_dotenv(os.path.join(CURRENT_PATH, 'config.env'))

DISCORD_INFO_CHANNEL = os.getenv('DISCORD_INFO_CHANNEL')
DISCORD_BOT_NAME = os.getenv('DISCORD_BOT_NAME')
UPLOAD_SERVER_INFO = os.getenv('UPLOAD_SERVER_INFO')
UPLOAD_SERVER_PATH = os.getenv('UPLOAD_SERVER_PATH')
UPLOAD_SERVER_PORT = os.getenv('UPLOAD_SERVER_PORT')
SSH_KEY = os.getenv('SSH_KEY')
SSH_KEY_PATH = os.path.join(CURRENT_PATH, SSH_KEY)

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

def discord(msg, url=DISCORD_INFO_CHANNEL):
    data = {
        "content": msg,
        "username": DISCORD_BOT_NAME
    }
    result = requests.post(url, json=data)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        # print(err)
        pass
    else:
        # print("Discord mesajı başarıyla gönderildi., code {}.".format(result.status_code))
        pass

def generateRandomString(stringLength=10):
    letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    lettersCapital = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    characters = letters + lettersCapital + numbers
    return ''.join(random.choice(characters) for i in range(stringLength))

def readAllFilesOnDir(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            files.append(os.path.join(r, file))
    return files

def checkIfUploaded(filename):
    if(filename.endswith("__uploaded.jpg")):
        return True
    else:
        return False

def moveFile(filename):
    os.rename(os.path.join(EXPORT_PATH, filename), os.path.join(UPLOAD_PATH, filename))

def getFilename(filepath):
    return os.path.basename(filepath)

def uploadFile(filename):
    print("Uploading file: {}".format(filename))
    imageFilePath = os.path.join(EXPORT_PATH, filename)

    productNumber = filename.split("__")[1]
    productNumber = productNumber.split(".")[0]
    imagePathForDB = "/uploads/studios_auto_upload/"+ filename

    try:
        command = "scp -i {} -P {} {} {}:{}{}".format(SSH_KEY_PATH, UPLOAD_SERVER_PORT, imageFilePath, UPLOAD_SERVER_INFO, UPLOAD_SERVER_PATH, filename)
        subprocess.call([command], shell=True)
    except Exception as e:
        print("Error: {}".format(e))
        return False

    # Dosya yüklendi veritabanı kaydı açılacak
    result = createRecord(productNumber, imagePathForDB)
    if(result == False):
        discord("Veritabanı kaydı oluşturulamadı.")
        return False

    replace = getFilename(filename).replace(".jpg", "__uploaded.jpg")
    newPath = os.path.join(UPLOAD_PATH, replace)
    os.rename(imageFilePath, newPath)

def createRecord(productId, filename):
    salt = generateRandomString(8)
    zipperColor = "0xffffff"
    currentDatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
        cursor = conn.cursor()
        query = "INSERT INTO `studios` (`salt`, `uv_map`, `product_id`, `zipper_color`, `created_at`, `updated_at`) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (salt, filename, productId, zipperColor, currentDatetime, currentDatetime))
        conn.commit()

        cursor.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("MYSQL kullanıcı adı veya parola ile ilgili bir sorun var.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("MYSQL veritabanı mevcut değil.")
        else:
            print(err)

        return False
    else:
        discord("https://jordanred.com/studio/"+ salt)
        conn.close()

    return True

def main():
    files = readAllFilesOnDir(EXPORT_PATH)
    for file in files:
        isUploaded = checkIfUploaded(file)
        if(isUploaded):
            moveFile(getFilename(file))
            continue
        else:
            if(getFilename(file).endswith(".jpg")):
                uploadFile(getFilename(file))

    # discord("Test mesajı")

def checkForUpdates():
    return True

def update():
    print("Updating...")

if __name__ == "__main__":
    if(checkForUpdates() == True):
        update()
    else:
        main()

