import json
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay
import numpy as np
import geatpy as ea
import matplotlib.pyplot as plt
import time
import datetime

class generation():
    with open('生态课表入参参数V1.2.json', 'rb') as f:
        content = json.load(f)
    students = content['students']
    teachers = content['teachers']
    classroom = content['classrooms']
    # subject = content['subject']
    courses = content['courses']
    tools = content['tools']
    schedule = content['schedule']

    def __init__(self):
        return

    # def course_count(self):
    #     generation.course_num = len(generation.courses)
    #     return

    # def course_teacher_relation(self):
    #     dict = {}
    #     for course in generation.courses:
    #         dict[course['code']] = list()
    #     for t in generation.teachers:
    #         for c in t['courseCode']:
    #             dict[c].append(t['idNo'])
    #     self.course_teacher_dict = dict
    #     return dict

    # def course_room_relation(self):
    #     dict = {}
    #     for course in generation.courses:
    #         dict[course['code']] = course['classroomCode']
    #     self.course_room_dict = dict
    #     return dict

# 根据校历计算课时数
    def schedule_info_read(self):
        week_mask = str()
        week_on = [0] * 7
        date_list = list()

        week_on[0] = int(generation.schedule["monday"])
        week_on[1] = int(generation.schedule["tuesday"])
        week_on[2] = int(generation.schedule["wednesday"])
        week_on[3] = int(generation.schedule["thursday"])
        week_on[4] = int(generation.schedule["friday"])
        week_on[5] = int(generation.schedule["saturday"])
        week_on[6] = int(generation.schedule["sunday"])
        lessonNumAm = int(generation.schedule["lessonNumAm"])
        lessonNumPm = int(generation.schedule["lessonNumPm"])
        if week_on[0] != 0:
            week_mask += "Mon"
        if week_on[1] != 0:
            week_mask += " Tue"
        if week_on[2] != 0:
            week_mask += " Wed"
        if week_on[3] != 0:
            week_mask += " Thu"
        if week_on[4] != 0:
            week_mask += " Fri"
        if week_on[5] != 0:
            week_mask += " Sat"
        if week_on[6] != 0:
            week_mask += " Sun"

        holiday_list = CustomBusinessDay(holidays=generation.schedule["holiday"], weekmask = week_mask)
        s_day = self.schedule["startTermBegin"]
        e_day = self.schedule["startTermEnd"]
        bus_day = pd.date_range(start=s_day, end=e_day, freq= holiday_list)

        day_period = list()
        times_sum = 0
        for day in bus_day:
            weekday = day.weekday() + 1
            if week_on[weekday] == 1:
                times = int(generation.schedule["lessonNumAm"]) + int(generation.schedule["lessonNumPm"])
            if week_on[weekday] == 2:
                times = int(generation.schedule["lessonNumAm"])
            if week_on[weekday] == 3:
                times = int(generation.schedule["lessonNumPm"])
            day_period.append(times)
            times_sum += times

        generation.bus_day = bus_day
        generation.day_period = day_period #每天对应哪几节课
        generation.times_sum = times_sum
        generation.week_on = week_on
        generation.lessonNumAm = lessonNumAm
        generation.lessonNumPm = lessonNumPm
        return bus_day

# # 科目信息读取,在教师信息之前读入
#     def subject_info(self):
#         subject_num = len(generation.subject)
#         sub_tea_relation = dict()
#         for subject in generation.subject:
#             sub_tea_relation[subject['code']] = list()
#         self.sub_tea_relation = sub_tea_relation
#         return
# 老师信息读取和安排
    def teacher_info(self):
        generation.teacher_num = len(generation.teachers)
        teacher_work = [0] * generation.teacher_num
        count = 0
        for i in generation.teachers:
            # for j in i["subjectId"]:
            #     self.sub_tea_relation[j].append(i["idNo"])

            sub = i["subjectId"]
            # print(sub,"+",type(sub))
            if sub in generation.subject["teacher"]:
                generation.subject["teacher"][sub].append(count)
            else:
                print("第",count,"老师无课")
            # 在teacher字典中加入给每个老师安排课程和工作量安排
            i["workload"] = 0
            i["course"] = list()
            count += 1

        self.teacher_work = teacher_work
        return

# 课程信息读取和安排
    def course_info(self):
        subject = dict()
        subject["course"] = dict()
        count = 0
        for course in generation.courses:
            sub_id = course["subjectId"]
            if sub_id in subject["course"]:
                subject["course"][sub_id].append(count)
            else:
                subject["course"][sub_id] = list()
                subject["course"][sub_id].append(count)
            count += 1

        subject["teacher"] = dict()
        subject["start"] = dict()
        subject["end"] = dict()
        for key in subject["course"]:
            subject["teacher"][key] = list()
            subject["start"][key] = list()
            subject["end"][key] = list()
        generation.subject = subject
        self.teacher_info()

        course_sum = 0
        # 以下进行老师的工作分配
        for s in subject["course"]:
            course_list = subject["course"][s]
            teacher_list = subject["teacher"][s]
            subject["start"][s] = course_sum

            for num in course_list:
                period = generation.courses[num]["period"]
                workload_list = list(map(lambda  x: generation.teachers[x]["workload"], subject["teacher"][s]))
                min_teacher = teacher_list[(workload_list.index(min(workload_list)))] #找出当前工作量安排最少的老师，把这个course安排给他
                generation.courses[num]["teacher"] = min_teacher
                generation.teachers[min_teacher]["course"].append(num)
                generation.teachers[min_teacher]["workload"] += period

                course_sum1 = course_sum + period
                generation.courses[num]["start"] = course_sum
                generation.courses[num]["end"] = course_sum1
                course_sum = course_sum1

            subject["end"][s] = course_sum
        self.course_sum = course_sum
        return
# 教室信息读取
    def room_info(self):
        return

    def tongji(students):
        ###生成包含所有课程ID的矩阵
        course = np.zeros((110, 110))
        course = course.astype(int)

        for i in students:
            if type(i['goalId']) == list:
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
        # q1 = dict(q)
        return q

    def id2course(courses):
        p = {}
        for i in range(len(courses)):
            if type(courses[i]['goalId']) == list:
                for j in courses[i]['goalId']:
                    p.update({j: i})
            else:
                p.update({int(courses[i]['goalId']): i})
        return p

    def students_num(students, courses):
        # id2course是一个字典，key是goalID，vaule是courses对应的在队列中的位置，{41:17}
        id2cour = id2course(courses)
        for a in courses:
            a.update({'students_num': 0})
        for i in students:
            # j是goalId
            if (type(i['goalId']) == list):
                for j in i['goalId']:
                    if (j in id2cour):
                        courses[id2cour[j]].update({'students_num': courses[id2cour[j]]['students_num'] + 1})
            # 另一种情况，goalId是一个int
            elif (type(i['goalId']) == int):
                if (i['goalId'] in id2cour):
                    courses[id2cour[i['goalId']]]. \
                        update({'students_num': courses[id2cour[i['goalId']]]['students_num'] + 1})
        return courses

    '''=========统计subjects间的约束==========='''

    def course_ys(self):
        goalId_ys = self.tongji(generation.students)
        # 建立goalId间的约束的字典，该字典键是两个goalId的有序元组，值是约束出现的次数
        goalId_ys = dict(goalId_ys)
        # cour_in_sub是字典，键是subject，值是courses的列表
        cour_in_sub = generation.subject['course']
        # sub_Id是所有subject的列表
        sub_Id = list(cour_in_sub.keys())
        course_ys = []
        for i in range(len(sub_Id) - 1):
            for j in sub_Id[i + 1:]:
                for k in cour_in_sub[sub_Id[i]]:
                    for l in cour_in_sub[j]:
                        a = generation.courses[k]['goalId']
                        b = generation.courses[l]['goalId']
                        ys = 0

                        if (a < b):
                            if ((a, b) in goalId_ys):
                                ys = ys + goalId_ys[(a, b)]
                                course_ys.append([(k, l), ys])
                        elif (a > b):
                            if ((b, a) in goalId_ys):
                                ys = ys + goalId_ys[(b, a)]
                                course_ys.append([(l, k), ys])
        course_ys = sorted(course_ys, key=lambda x: x[1], reverse=True)
        self.course_ys = course_ys
        return course_ys

# plan = generation()
# plan.schedule_info_read()
# print(generation.times_sum)
# print(generation.subject)
# print(work_data, week_num)