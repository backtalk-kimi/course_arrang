"""
aimfunc.py - 目标函数文件
描述:
    目标：max f = 21.5 + x1 * np.sin(4 * np.pi * x1) + x2 * np.sin(20 * np.pi * x2)
    约束条件：
        x1 != 10
        x2 != 5
        x1 ∈ [-3, 12.1] # 变量范围是写在遗传算法的参数设置里面
        x2 ∈ [4.1, 5.8]
"""

import numpy as np

def teacher_condition(teacher, matrix, population, course_teacher):
    course_list = course_teacher[teacher]
    count = len(course_list)
    total_score = [0] * population
    total_score = np.array(total_score)
    for i in range(count):
        time1 = matrix[2*course_list[i] + 1]
        for j in range(i + 1 , count):
            time2 = matrix[2*course_list[j] + 1]
            score = list(map((lambda x, y: 1 if x==y else 0), time1, time2))
            score = np.array(score)
            total_score = total_score + score
    return total_score

def total_condition(matrix, course_count, population):
    count = len(matrix)
    total_score = [0] * population
    total_score = np.array(total_score)

    for i in range(course_count):
        room1 = matrix[2 * i]
        time1 = matrix[2 * i + 1]
        for j in range(i + 1, course_count):
            room2 = matrix[2 * j]
            time2 = matrix[2 * j + 1]
            same_room = list(map((lambda x,y: 1 if x==y else 0), room1, room2))
            same_time = list(map((lambda x,y: 1 if x==y else 0), time1, time2))
            score = list(map((lambda x,y: 1 if x==y==1 else 0), same_room, same_time))
            score = np.array(score)
            total_score += score
    return total_score

def aimfunc(Phen, CV, course_teacher, Nind, course_count):
    teacher_count = len(course_teacher)
    matrix = np.array(Phen).T
    CV_score = [0] * Nind
    CV_score = np.array(CV_score)
    for i in range(teacher_count):
        score1 = teacher_condition(i, matrix, Nind, course_teacher)
        CV_score += score1

    score2 = total_condition(matrix, course_count, Nind)
    # print(score2)
    CV_score += score2
    CV_score = CV_score.reshape(Nind,1)
    return CV_score

