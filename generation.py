#coding=UTF-8
import json
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay
import numpy as np
# import geatpy as ea
# import matplotlib.pyplot as plt
import time
import datetime
from dateutil import rrule
from clustering import cluster
import error_control
from genetic import *
import random


class generation():
    with open('input.json', 'r', encoding='gb2312') as f:
        content = json.load(f)
    students = content['students']
    teachers = content['teachers']
    classroom = content['classrooms']
    subject = content['subjects']
    courses = content['courses']
    tools = content['tools']
    schedule = content['schedule']

    def __init__(self):
        generation.subject_info(self)
        generation.schedule_info_read(self)
        generation.tool_info(self)
        generation.room_info(self)
        return

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


        holiday_list = CustomBusinessDay(holidays=generation.schedule["holiday"], weekmask=week_mask)
        s_day = self.schedule["startTermBegin"]
        e_day = self.schedule["startTermEnd"]
        bus_day = pd.date_range(start=s_day, end=e_day, freq=holiday_list)

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
            times_sum += times
            day_period.append(times_sum)

        generation.bus_day = bus_day
        generation.day_period = day_period  # 每天对应哪几节课
        generation.times_sum = times_sum
        generation.week_on = week_on
        generation.lessonNumAm = lessonNumAm
        generation.lessonNumPm = lessonNumPm
        return bus_day

# 科目信息读取,在教师信息之前读入
    def subject_info(self):
        subject = dict()
        for i in generation.subject:
            subject_id = i["subjectId"]
            subject[subject_id] = dict()
            subject[subject_id]["subjectNumber"] = i["subjectNumber"]
            subject[subject_id]["subjectName"] = i["subjectName"]
            subject[subject_id]["teacher"] = list()
            subject[subject_id]["course"] = list()
            # if i["subjectNumber"] % self.bus_week == 0:
            #     times = i["subjectNumber"] // self.bus_week
            # else:
            #     times = i["subjectNumber"] // self.bus_week + 1
            # subject_arrange.append(int(times))
        generation.subject = subject

        self.teacher_info()
        self.course_info()
        return
# 老师信息读取和安排
    def teacher_info(self):
        generation.teacher_num = len(generation.teachers)
        # teacher_work = [0] * generation.teacher_num
        count = 0
        for i in generation.teachers:
            sub = i["subjectId"]
            if type(sub) == list:
                for j in sub:
                    if j in generation.subject:
                        generation.subject[j]["teacher"].append(count)
                    else:
                        print("第",count,"老师无课")
            else:
                if sub in generation.subject:
                    generation.subject[sub]["teacher"].append(count)
                else:
                    print("第",count,"老师无课")
            # 在teacher字典中加入给每个老师安排课程和工作量安排
            i["workload"] = 0
            i["subject"] = list()
            count += 1

        # self.teacher_work = teacher_work
        return

# 课程信息读取和安排
    def course_info(self):
        # subject = dict()
        # subject["course"] = dict()
        count = 0
        for course in generation.courses:
            sub_id = course["subjectId"]
            if sub_id in generation.subject:
                generation.subject[sub_id]["course"].append(count)
            else:
                print("course", count, "is not in subjects")
            count += 1
        self.id2course()
        return
# 教室信息读取
    def room_info(self):
        room_type = dict()
        count = 0
        for i in generation.classroom:
            if i["typeId"] in room_type:
                room_type[i["typeId"]].append(count)
            else:
                room_type[i["typeId"]] = list()
                room_type[i["typeId"]].append(count)
            count += 1
        generation.room_type = room_type
        return
#教具信息读取
    def tool_info(self):
        toolcode2num = dict()
        for i in generation.tools:
            toolcode2num[i["code"]] = i["count"]
        generation.toolcode2num = toolcode2num
        return


    def id2course(self):
        p = {}
        courses = self.courses
        for i in range(len(courses)):
            if type(courses[i]['goalId']) == list:
                for j in courses[i]['goalId']:
                    if j in p:
                        p[j].append(i)
                    else:
                        p[j] = list()
                        p[j].append(i)
            else:
                j = courses[i]['goalId']
                if j in p:
                    p[j].append(i)
                else:
                    p[j] = list()
                    p[j].append(i)
        self.goalid2course = p
        return p
    #
    # def students_num(self, students, courses):
    #     # id2course是一个字典，key是goalID，vaule是courses对应的在队列中的位置，{41:17}
    #     id2cour = id2course(courses)
    #     for a in courses:
    #         a.update({'students_num': 0})
    #     for i in students:
    #         # j是goalId
    #         if (type(i['goalId']) == list):
    #             for j in i['goalId']:
    #                 if (j in id2cour):
    #                     courses[id2cour[j]].update({'students_num': courses[id2cour[j]]['students_num'] + 1})
    #         # 另一种情况，goalId是一个int
    #         elif (type(i['goalId']) == int):
    #             if (i['goalId'] in id2cour):
    #                 courses[id2cour[i['goalId']]]. \
    #                     update({'students_num': courses[id2cour[i['goalId']]]['students_num'] + 1})
    #     return courses
    #
    # '''=========统计subjects间的约束==========='''
    #
    # def course_ys_build(self):
    #     goalId_ys = generation.tongji(generation.students)
    #     # 建立goalId间的约束的字典，该字典键是两个goalId的有序元组，值是约束出现的次数
    #     goalId_ys = dict(goalId_ys)
    #     # cour_in_sub是字典，键是subject，值是courses的列表
    #     cour_in_sub = generation.subject['course']
    #     # sub_Id是所有subject的列表
    #     sub_Id = list(cour_in_sub.keys())
    #     course_ys = dict()
    #     for i in range(len(sub_Id) - 1):
    #         for j in sub_Id[i + 1:]:
    #             for k in cour_in_sub[sub_Id[i]]:
    #                 for l in cour_in_sub[j]:
    #                     a = generation.courses[k]['goalId']
    #                     b = generation.courses[l]['goalId']
    #                     ys = 0
    #
    #                     if (a < b):
    #                         if ((a, b) in goalId_ys):
    #                             ys = ys + goalId_ys[(a, b)]
    #                             course_ys[(k, l)] = ys
    #                     elif (a > b):
    #                         if ((b, a) in goalId_ys):
    #                             ys = ys + goalId_ys[(b, a)]
    #                             course_ys[(k, l)] = ys
    #     # course_ys = sorted(course_ys, key=lambda x: x[1], reverse=True)
    #     self.course_ys = course_ys
    #     return course_ys

    def arrange(self):
        cluster_num = 4
        clustering = cluster(self, cluster_num)
        # clustering.display(self)
        subject_arrange = list()
        # for i in generation.subject:
        #     if generation.subject[i]["subjectNumber"] % self.bus_week == 0:
        #         times = generation.subject[i]["subjectNumber"] // self.bus_week
        #     else:
        #         times = generation.subject[i]["subjectNumber"] // self.bus_week + 1
        #     subject_arrange.append(int(times))
        # course_num = sum(subject_arrange)
        # s = []
        # for class_id in range(cluster_num):
        #     for i in range(course_num):
        #         teacher_id = np.random.randint(1, 8, 1)[0]
        #         s.append(Schedule(i, class_id, teacher_id, 1, 1))
        cluster_dict = self.cluster_dict
        for clusterId in cluster_dict:
            for subjectId in cluster_dict[clusterId]["sub2cou"]:
                length = len(cluster_dict[clusterId]["sub_times"][subjectId])
                subtime_sum = cluster_dict[clusterId]["sub_times"][subjectId][length - 1]
                a = list(range(self.times_sum))
                if subtime_sum > self.times_sum:
                    error_control.error_info(301)
                a = random.sample(a, subtime_sum)

                a.sort()
                time_num = 0

                subject = dict()
                subject["cluster"] = clusterId
                subject["subjectId"] = subjectId
                subject["subtime_sum"] = subtime_sum
                workload_min = 65535
                teacher_length = len(generation.teachers)
                for count in range(teacher_length):
                    if generation.teachers[count]["workload"] < workload_min :
                        teacherId = count
                        workload_min = generation.teachers[count]["workload"]
                subject["teacher"] = teacherId
                subject["course"] = list()

                course_list = cluster_dict[clusterId]["sub2cou"][subjectId]
                for course in course_list:
                    for i in range(generation.courses[course]["period"]):
                        b = Schedule(course, clusterId, teacherId, generation.courses[course]["unitId"])
                        subject["course"].append(b)
                        time_num += 1
                subject_arrange.append(subject)
        return subject_arrange

def result_disply(schedules, plan, successMark):
    time_list = [None] * plan.times_sum
    for subject in schedules:
        teacher = subject["teacher"]
        cluster = subject["cluster"]
        subjectId = subject["subjectId"]
        for course in subject["course"]:
            time = course.time
            room = course.roomId
            toolcode = course.tool

            courseId = course.courseId
            if time_list[time]:
                lesson = {"cluster" : cluster,
                          "teacher" : plan.teachers[teacher]["teacherId"],
                          "lessonNo" : plan.courses[courseId]["lessonNo"],
                          "classroomNo" : plan.classroom[room]["classroomNo"],
                          "unitId" : course.unitId,
                          "subjectId" : subjectId}
                if toolcode != -1:
                    toolId = plan.toolcode2Id[toolcode]
                    lesson["tool"] = plan.tools[toolId]["code"]
                time_list[time].append(lesson)
            else:
                time_list[time] = list()
                lesson = {"cluster": cluster,
                          "teacher": plan.teachers[teacher]["teacherId"],
                          "lessonNo": plan.courses[courseId]["lessonNo"],
                          "classroomNo": plan.classroom[room]["classroomNo"],
                          "unitId": course.unitId,
                          "subjectId" : subjectId}
                if toolcode != -1:
                    toolId = plan.toolcode2Id[toolcode]
                    lesson["tool"] = plan.tools[toolId]["code"]
                time_list[time].append(lesson)

    start = 0
    end = 0
    day_num = 0
    timeTableList = list()

    day_count = 0                               #日期计数
    lesson_count = 1
    for day_bound in plan.day_period:
        end = day_bound
        for time in range(start, end):
            if time_list[time]:
                for lesson in time_list[time]:

                    date = plan.bus_day[day_count]
                    day1 = (date - plan.bus_day[0]).days
                    daysOfWeek = date.weekday() + 1
                    weekNo = rrule.rrule(rrule.WEEKLY, dtstart = plan.bus_day[0], until= date).count()
                    tmpClassId = '%015d' % lesson["cluster"]

                    noOfDay = time - start + 1
                    if plan.week_on[weekNo] == 1:
                        if noOfDay > plan.lessonNumAm :
                            timePeriod = 3
                        else:
                            timePeriod = 2
                    elif plan.week_on[weekNo] == 2:
                        timePeriod = 2
                    elif plan.week_on[weekNo] == 3:
                        timePeriod = 3

                    new_dict = dict()
                    new_dict["gradeId"]     = 0                     #数据缺失
                    new_dict["lessonNo"]    = lesson["lessonNo"]
                    new_dict["noOfDay"]     = noOfDay
                    new_dict["adjustType"]  = 0
                    new_dict["sortNumber"]  = lesson_count
                    new_dict["classroomId"] = lesson["classroomNo"]
                    new_dict["daysOfWeek"]  = daysOfWeek
                    new_dict["subjectId"]   = lesson["subjectId"]
                    new_dict["orgId"]       = plan.schedule["orgId"]
                    new_dict["classTime"]   = noOfDay + (plan.lessonNumPm + plan.lessonNumAm) * day1
                    new_dict["teacherId"]   = lesson["teacher"]
                    new_dict["scheduleType"]= 2
                    new_dict["weeksSum"]    = 1
                    new_dict["scheduleDay"] = date.strftime("%Y-%m-%d")
                    new_dict["timePeriod"]  = timePeriod
                    new_dict["unitId"]      = lesson["unitId"]
                    new_dict["semester"]    = plan.schedule["semester"]
                    new_dict["weekNo"]      = weekNo
                    new_dict["startTime"]   = "00:00:00"            #数据缺失
                    new_dict["endTime"]     = "00:00:00"            #数据缺失
                    new_dict["tmpClassId"]  = tmpClassId
                    new_dict["statusFlag"]  = 0

                    timeTableList.append(new_dict)

                    lesson_count += 1
        start = end
        day_count += 1

    result = dict()
    if successMark == 1:
        result["code"] = 200
        result["msg"] = "success"
    else:
        result["code"] = 400
        result["msg"] = "fail"
    result["data"] = dict()
    result["data"]["timeTableList"] = timeTableList

    result = json.dumps(result, indent=3, ensure_ascii=False)
    with open('result.json', 'w') as f:
        f.write(result)
        f.close()
    return time_list


