from flask import Flask, request, render_template, send_from_directory
import cv2
import numpy as np
from insightface.app import FaceAnalysis
import re
import base64
import pyodbc
import pickle
import pandas as pd


def convertImage(imgData):
    imgstr = re.search(r'base64,(.*)', str(imgData)).group(1)
    with open('output.png', 'wb') as output:
        output.write(base64.b64decode(imgstr))

def convertImage_android(c):
    with open('output.png', 'wb') as output:
        output.write(base64.b64decode(c))



app = Flask(__name__, static_url_path='')

# Load mo hinh du doan
face_app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0, det_size=(640, 640))
model = pickle.load(open('my_model.sav', 'rb'))

# Ket noi databse
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=LAPTOP-3TD3ILE0\SQLEXPRESS;'
                      'Database=test_database;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

# Thiet lap constrain
labels = model.classes_
cursor.execute(
    '''
    select confident from confident_table
    where id=0
    '''
)
global_conf = cursor.fetchall()[0][0]

under_threshold = 'Unknown'
font_size = 1
bbox_thickness = 1


# Index page
@app.route('/')
def index():
    return render_template('index.html')


# Danh cho Web app
@app.route('/predict/', methods=['GET', 'POST'])
def predict():
    global face_app, model, cursor, labels, under_threshold

    imgData = request.get_data()
    convertImage(imgData)
    # try:
    #     convertImage(imgData)
    # except:
    #     f = request.files['img']
    #     f.save('output.png')

    img = cv2.imread('output.png')
    faces = face_app.get(img)

    idx = []
    names = []
    class__ = []
    dob = []

    for i in range(len(faces)):
        X = []
        face = faces[i]

        box = face.bbox.astype(np.int32)
        cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)

        y_prob = model.predict_proba(face.embedding.reshape(1, -1))[0]

        label = under_threshold
        id_, name, class_, dob_ = [under_threshold for _ in range(4)]

        # Ki???m tra ????? ch???c ch???n d??? ??o??n so v???i ng?????ng ch???c ch???n global
        if max(y_prob) >= float(global_conf):
            pred_label = labels[np.argmax(y_prob)]
            cursor.execute(
                '''
                select confident from confident_table
                where id='{}'
                '''.format(int(pred_label))
            )
            class_conf = cursor.fetchall()[0][0]
            # Ki???m tra ????? ch???c ch???n d??? ??o??n v???i ng?????ng ch???c ch???n class
            if max(y_prob) >= float(class_conf):

                # N???u th???a m??n c??? 2 ??i???u ki???n, label s??? ???????c d??? ??o??n l?? class c?? max confident
                # Ng?????c l???i s??? cho k???t qu??? l?? 'Unknown'
                label = pred_label

                # Truy v???n th??ng tin c???a ng?????i v???a ???????c d??? ??o??n
                cursor.execute(
                    '''
                    select * from member
                    where id='{}'
                    '''.format(int(pred_label))
                )
                id_, name, class_, dob_ = cursor.fetchall()[0]

        idx.append(id_)
        names.append(name)
        class__.append(class_)
        dob.append(dob_)


        cv2.putText(
            img, str(i),
            (box[0] - 1, box[1] - 4),
            cv2.FONT_HERSHEY_COMPLEX, font_size, (0, 255, 0), bbox_thickness
        )

    # Ghi k???t qu??? v??o file .csv
    pd.DataFrame({'ID': idx, 'Ten': names, 'Don vi': class__, 'Ngay sinh': dob}).to_csv('static/result.csv')
    cv2.imwrite('static/output.png', img)

    return label


# Danh cho android app
@app.route('/android/', methods=['GET', 'POST'])
def android():
    global face_app, model, cursor, labels, under_threshold

    imgData = request.get_data()
    convertImage_android(imgData)
    # try:
    #     # Android app test
    #     convertImage_android(imgData)
    # except:
    #     f = request.files['img']
    #     f.save('output.png')

    img = cv2.imread('output.png')
    faces = face_app.get(img)

    for i in range(len(faces)):
        X = []
        face = faces[i]

        box = face.bbox.astype(np.int32)
        cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)

        y_prob = model.predict_proba(face.embedding.reshape(1, -1))[0]

        label = under_threshold
        id_, name, class_, dob_ = ['Unknown' for _ in range(4)]
        if max(y_prob) >= float(global_conf):
            pred_label = labels[np.argmax(y_prob)]
            cursor.execute(
                '''
                select confident from confident_table
                where id='{}'
                '''.format(int(pred_label))
            )
            class_conf = cursor.fetchall()[0][0]
            if max(y_prob) >= float(class_conf):
                label = pred_label

                cursor.execute(
                    '''
                    select * from member
                    where id='{}'
                    '''.format(int(pred_label))
                )

                id_, name, class_, dob = cursor.fetchall()[0]

    output_message = 'ID: {}\nT??n: {}\nL???p: {}\nNg??y sinh: {}'.format(id_, name, class_, dob)
    return output_message

@app.route('/<path:path>')
def send_image(path):
    return send_from_directory('.', path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
