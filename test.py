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

    def course_count(self):
        generation.course_num = len(generation.courses)
        return

    def course_teacher_relation(self):
        dict = {}
        for course in generation.courses:
            dict[course['code']] = list()
        for t in generation.teachers:
            for c in t['courseCode']:
                dict[c].append(t['idNo'])
        self.course_teacher_dict = dict
        return dict

    def course_room_relation(self):
        dict = {}
        for course in generation.courses:
            dict[course['code']] = course['classroomCode']
        self.course_room_dict = dict
        return dict

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
        generation.day_period = day_period
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
            count += 1

        subject["teacher"] = dict()
        for key in subject["course"]:
            subject["teacher"][key] = list()
        generation.subject = subject
        self.teacher_info()

        course_sum = 0
        # 以下进行老师的工作分配
        for s in subject["course"]:
            course_list = subject["course"][s]
            teacher_list = subject["teacher"][s]
            for num in course_list:
                period = generation.courses[num]["period"]
                workload_list = list(map(lambda  x: generation.teachers[x]["workload"], subject["teacher"][s]))
                min_teacher = teacher_list[(workload_list.index(min(workload_list)))] #找出当前工作量安排最少的老师，把这个course安排给他
                generation.courses[num]["teacher"] = min_teacher
                generation.teachers[min_teacher]["course"].append(num)
                generation.teachers[min_teacher]["workload"] += period

                course_sum += period
                generation.course_sum = course_sum
                # print(workload_list)
        # generation.subject = subject
        return
# 教室信息读取
    def room_info(self):
        return

# plan = generation()
# plan.course_info()
# print(generation.subject)
# print(work_data, week_num)