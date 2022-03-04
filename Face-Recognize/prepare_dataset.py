import os
import argparse
import cv2
import numpy as np
from insightface.app import FaceAnalysis
import time


def prepare(name, data_path, output_path, name_features='X', name_targets='y'):
    start = time.time()
    app = FaceAnalysis(name=name, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'], )
    app.prepare(ctx_id=0, det_size=(640, 640), det_thresh=0.5)
    end_1 = time.time()
    print('Khởi động: ', end_1-start, '(s)', sep='')

    file_names = [i for i in os.listdir(data_path)]

    X = []
    y = []
    count = 0

    ext_names = ['.jpg', '.png', '.jpeg']
    for file_name in file_names:
        images = ['.'.join(i.split('.')[:-1]) for i in os.listdir(os.path.join(data_path, file_name))]
        for image in images:

            for ext_name in ext_names:
                image_file = os.path.join(data_path, file_name, image + ext_name)
                if os.path.exists(image_file):
                    img = cv2.imread(image_file)
                    if img is None:  # Khong phat hien khuon mat trong buc anh
                        count += 1
                        continue
                    faces = app.get(img)
                    if len(faces) != 1:  # Co nhieu hon 1 khuong mat trong buc anh
                        count += 1
                        continue

                    face = faces[0]
                    X.append(face.embedding)
                    y.append(file_name)
                    break

    X = np.array(X)
    y = np.array(y)

    np.save(os.path.join(output_path, name_features), X)
    np.save(os.path.join(output_path, name_targets), y)
    cv2.destroyAllWindows()
    print('Done in ', time.time()-end_1, '(s)', sep='')

    print('Số lượng ảnh bị bỏ qua:', count)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', default='buffalo_l',
                    help='Name of your model zoo')
    ap.add_argument('--data-path', default='valset',
                    help='Path to training dataset')
    ap.add_argument('--output-path', default='./model',
                    help='Path to output features, targets')
    ap.add_argument('--name-features', default='X_val',
                    help='Name output features')
    ap.add_argument('--name-targets', default='y_val',
                    help='Name output targets')
    args = ap.parse_args()

    prepare(args.name, args.data_path, args.output_path, args.name_features, args.name_targets)
