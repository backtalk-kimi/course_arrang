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
        if type(i['goalId'])==list:
         for j in range(len(i['goalId'])):
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

def students_num(students,courses):
    #id2course是一个字典，key是goalID，vaule是courses对应的在队列中的位置，{41:17}
    id2cour=id2course(courses)
    for a in courses:
        a.update({'students_num':0})
    for i in students:
        #j是goalId
        if (type(i['goalId'])==list):
            for j in i['goalId']:
                if (j in id2cour):
                    courses[id2cour[j]].update({'students_num':courses[id2cour[j]]['students_num']+1})
        #另一种情况，goalId是一个int
        elif(type(i['goalId'])==int):
            if (i['goalId'] in id2cour):
                courses[id2cour[i['goalId']]].\
                    update({'students_num': courses[id2cour[i['goalId']]]['students_num'] + 1})
    return courses


'''=========统计subjects间的约束==========='''
def course_ys(students,subject,courses):
    goalId_ys   = tongji(students)
    #建立goalId间的约束的字典，该字典键是两个goalId的有序元组，值是约束出现的次数
    goalId_ys   = dict(goalId_ys)
    #cour_in_sub是字典，键是subject，值是courses的列表
    cour_in_sub = subject['course']
    #sub_Id是所有subject的列表
    sub_Id      = list(cour_in_sub.keys())
    course_ys   = []
    for i in range(len(sub_Id)-1):
        for j in sub_Id[i+1:]:
            for k in cour_in_sub[sub_Id[i]]:
                for l in cour_in_sub[j]:
                    a  = courses[k]['goalId']
                    b  = courses[l]['goalId']
                    ys = 0

                    if( a < b ):
                        if ((a,b) in goalId_ys):
                            ys = ys + goalId_ys[(a,b)]
                            course_ys.append([(k, l), ys])
                    elif(a > b):
                        if((b,a) in goalId_ys):
                            ys = ys + goalId_ys[(b,a)]
                            course_ys.append([(l,k),ys])
    course_ys=sorted(course_ys,key=lambda x:x[1],reverse=True)
    return course_ys












#plan=generation()
#a=tongji(plan.students)
#b=id2course(plan.courses)
#f=students_num(plan.students,plan.courses)
#e=course_ys(plan.students,plan.subject,plan.courses)

