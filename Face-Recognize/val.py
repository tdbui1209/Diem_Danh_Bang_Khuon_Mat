import argparse
import numpy as np
import pickle
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def local_confident(class_, y_test, y_prob, conf):
    class_idx = []
    local_conf = []
    for i, j in enumerate(y_test):
        if j == class_:
            class_idx.append(i)
    for c in conf:
        a = []
        for i in range(len(y_prob)):
            if i not in class_idx:
                continue
            if max(y_prob[i]) > c:
                if labels[np.argmax(y_prob[i])] == class_:
                    a.append(1)
                else:
                    a.append(0)
            else:
                a.append(0)
        local_conf.append(accuracy_score([1 for _ in range(len(class_idx))], a))
    return local_conf


def best_confident(local_conf, conf):
    temp = []
    for i, j in enumerate(local_conf):
        if j == max(local_conf):
            temp.append(i)
    return conf[max(temp)]

ap = argparse.ArgumentParser()
ap.add_argument('--features', default='./model/X_val.npy',
                help='Path to matrix features')
ap.add_argument('--targets', default='./model/y_val.npy',
                help='Path to vector targets')
ap.add_argument('--model', default='./model/my_model.sav',
                help='Path to classifier model')
ap.add_argument('--steps', default=0.001,
                help='Confident steps')

args = ap.parse_args()

X_test = np.load(args.features)
y_test = np.load(args.targets)

loaded_model = pickle.load(open(args.model, 'rb'))
labels = loaded_model.classes_

conf = np.arange(0, 1, float(args.steps))

global_conf = []

y_prob = loaded_model.predict_proba(X_test)


for c in conf:
    y_pred = []
    for i in y_prob:
        if max(i) > c:
            class_ = labels[np.argmax(i)]
            y_pred.append(class_)
        else:
            y_pred.append(0)
    global_conf.append(accuracy_score(y_test, y_pred))


plt.xlabel('Confident Threshold')
plt.ylabel('Accuracy')
sns.lineplot(y=global_conf, x=conf, color='blue', label='Global')
local_confidents = []
best_confidents = [[], []]

for i in set(y_test):
    local_conf = local_confident(i, y_test, y_prob, conf)
    sns.lineplot(y=local_conf, x=conf, label=i)
    best_confidents[0].append(i)
    best_confidents[1].append(best_confident(local_conf, conf))

best_confidents[0].insert(0, 'Global')
best_confidents[1].insert(0, best_confident(global_conf, conf))
for i in range(len(best_confidents[0])):
    print(f'{best_confidents[0][i]}: {best_confidents[1][i]}')
plt.legend()
plt.show()

df = pd.DataFrame({'class': best_confidents[0], 'Best Confident': best_confidents[1]})
df.to_csv('best_confident_99.csv', index=False)
