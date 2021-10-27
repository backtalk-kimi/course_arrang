import json
import numpy as np
import pandas as pd
from test import generation

def tongji(students):
    #with open(fileroad, 'rb') as f:
    #    content = json.load(f)
    #students = content['students']
    #传入students
    ###生成包含所有课程ID的矩阵
    course = np.zeros((110, 110))
    course = course.astype(int)

    for i in students:
        for j in range(len(i['goalId']) - 1):
            for k in i['goalId'][j:]:
                course[i['goalId'][j]][k] += 1
    p = {}
    for i in range(110):
        for j in range(i, 110):
            if i != j and course[i][j] != 0:
                # 该矩阵中ij项和ji项代表相同的约束条件，应当相加
                p.update({(i, j): course[i][j] + course[j][i]})

    q = sorted(p.items(), key=lambda d: d[1], reverse=True)
    #q1 = dict(q)
    return q


def id2course(courses):
    p={ }
    for i in range(len(courses)):
        if type(courses[i]['goalId'])==list:
            for j in courses[i]['goalId']:
                p.update({j:i})
        else:
            p.update({int(courses[i]['goalId']):i})
    return p

#plan=generation()
#a=tongji(plan.students)
#b=id2course(plan.courses)



