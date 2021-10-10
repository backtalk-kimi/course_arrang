import numpy as np

def teacher_condition(matrix, population, teacher_course):
    num = len(teacher_course)
    total_score = [0] * population
    total_score = np.array(total_score)

    for teacher in range(num):
        course_list = teacher_course[teacher]
        count = len(course_list)
        for i in range(count):
            time1 = matrix[2*course_list[i] + 1]
            for j in range(i + 1 , count):
                time2 = matrix[2*course_list[j] + 1]
                score = list(map((lambda x, y: 1 if x==y else 0), time1, time2))
                score = np.array(score)
                total_score = total_score + score
    return total_score

def class_condition(matrix, population, class_course):
    num = len(class_course)
    total_score = [0] * population
    total_score = np.array(total_score)

    for count in range(num):
        course_list = class_course[count]
        for i in range(count):
            time1 = matrix[2 * course_list[i] + 1]
            for j in range(i + 1, count):
                time2 = matrix[2 * course_list[j] + 1]
                score = list(map((lambda x, y: 1 if x == y else 0), time1, time2))
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

def teacher_optimizer(teacher, matrix, population, teacher_course):
    day_course = np.zeros((population,5))
    course_list = teacher_course[teacher]
    count = len(course_list)

    total_score = [0] * population
    total_score = np.array(total_score)

    for i in course_list:
        time = matrix[2 * i + 1, :]
        time = time // 5
        for j in range(population):
            day_course[j][time[j]] += 1
    for i in range(population):
        for j in range(5):
            if (day_course[i][j] > 3):
                total_score[i] += (5-3)
    total_score += 1
    total_score = 5/total_score
    print("teacher_optimizer = ",total_score)
    return total_score

def class_optimizer(lesson, matrix, population, class_course):
    day_course = list()                       #保存该班级每天的课程
    day_num = np.zeros((population, 5))       #记录每天上课数
    day_var = np.zeros(population)          #一周五天课程数的方差
    day_rich = np.zeros(population)         #每天安排课程的丰富度
    lesson_arrange_score = np.zeros(population)

    course_list = class_course[lesson]
    for i in range(population):
        day_course.append({0:[],
                          1:[],
                          2:[],
                          3:[],
                          4:[]})
    for i in course_list:
        time = matrix[2*i + 1, :] // 5
        for j in range(population):
            day_course[j][time[j]].append(i // 6)
            day_num[j][time[j]] += 1
    for i in range(population):
        day_var[i] = np.var(day_num[i ,:])
    for i in range(population):
        for j in range(5):
            m = day_course[i][j]
            day_set = set(m)
            day_rich[i] = day_rich[i] + len(day_set)
    lesson_arrange_score = day_var * 10 + day_rich
    # print("class_optimizer = ", lesson_arrange_score)
    return lesson_arrange_score

def aimfunc2(Phen , Nind, teacher_course, class_course):
    matrix = np.array(Phen).T
    teacher_num = len(teacher_course)
    class_num = len(class_course)
    optimizer_score = np.zeros(Nind)
    for i in range(teacher_num):
        score = teacher_optimizer(i, matrix, Nind, teacher_course)
        optimizer_score = optimizer_score + score
    for i in range(class_num):
        score = class_optimizer(i, matrix, Nind, class_course)
        optimizer_score = optimizer_score + score
    optimizer_score = optimizer_score.reshape(Nind, 1)
    return optimizer_score

def aimfunc(Phen, teacher_course, class_course, Nind, course_count):
    matrix = np.array(Phen).T
    CV_score = [0] * Nind
    CV_score = np.array(CV_score)

    score1 = teacher_condition(matrix, Nind, teacher_course)
    score2 = class_condition(matrix, Nind, class_course)
    score3 = total_condition(matrix, course_count, Nind)
    # print(score2)
    CV_score = score1 + score2 + score3
    CV_score = CV_score.reshape(Nind,1)
    return CV_score

def aimfunc1(Phen, teacher_course, class_course, Nind, course_count):
    CV = aimfunc(Phen, teacher_course, class_course, Nind, course_count)
    ObjV = aimfunc2(Phen , Nind, teacher_course, class_course)
    return ObjV,CV
