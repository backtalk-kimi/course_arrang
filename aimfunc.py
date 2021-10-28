import numpy as np
from test import generation

def subject_in_order(Phen, population, plan):
    matrix = np.array(Phen).T
    total_score = [0] * population
    total_score = np.array(total_score)

    for sub in plan.subject["course"]:
        start = plan.subject["start"][sub]
        end = plan.subject["end"][sub]
        for i in range(start, end):
            time1 = matrix[2 * i + 1]
            for j in range(i, end):
                time2 = matrix[2 * j + 1]
                score = list(map(lambda x,y: 0 if x < y else 1, time1, time2))
                score = np.array(score)
                total_score = total_score + score
    return total_score

def sametime_statistics(entity, plan):
    count_sum = plan.course_sum
    time_dict = dict()
    for i in range(count_sum):
        time = entity[2 * i + 1]
        if time in time_dict:
            time_dict[time].append(i)
        else:
            time_dict[time] = list()
            time_dict[time].append(i)
    return time_dict


def goal_tool_room_order(Phen, Nind, plan):
    # for i in Phen:
    #     entity = np.array(i).T
    #     time_dict = sametime_statistics(entity, plan)
    #     print(time_dict)
    entity = np.array(Phen[0]).T
    time_dict = sametime_statistics(entity, plan)
    print(time_dict)




def aimfunc(Phen, plan, Nind) :
    # matrix = np.array(Phen).T
    CV_score = [0] * Nind
    CV_score = np.array(CV_score)

    # score1 = subject_in_order(Phen, Nind, plan)
    score2 = goal_tool_room_order(Phen, Nind, plan)
    # CV_score = CV_score + score1
    CV_score = CV_score.reshape(Nind, 1)
    # print(score2)
    return CV_score

def aimfunc1(Phen, teacher_course, class_course, Nind, course_count):
    CV = aimfunc(Phen, teacher_course, class_course, Nind, course_count)
    ObjV = aimfunc2(Phen , Nind, teacher_course, class_course)
    return ObjV,CV
