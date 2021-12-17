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
        self.cluster_num = int(generation.schedule["clusterId"])
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
            weekday = day.weekday()
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
                        print("No",count,"teacher is free")
            else:
                if sub in generation.subject:
                    generation.subject[sub]["teacher"].append(count)
                else:
                    print("No",count,"teacher is free")
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
                # global infomation
                # infomation += 'course, %d, is not in subjects'%(count)
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

    def arrange(self, cluster_num):
        clustering = cluster(self, cluster_num)
        # clustering.display(self)
        # subject_arrange = list()
        cluster_dict = self.cluster_dict
        cluster_arrange = dict()

        for clusterId in cluster_dict:
            cluster_arrange[clusterId] = dict()
            times_total = cluster_dict[clusterId]["times_total"]
            if times_total > self.times_sum:
                error_control.error_info(301)
            cluster_arrange[clusterId]["times_total"] = times_total
            cluster_arrange[clusterId]["subject"] = list()

            for subjectId in cluster_dict[clusterId]["sub2cou"]:
                length = len(cluster_dict[clusterId]["sub_times"][subjectId])
                subtime_sum = cluster_dict[clusterId]["sub_times"][subjectId][length - 1]
                # a = list(range(self.times_sum))
                # a = random.sample(a, subtime_sum)

                # a.sort()
                # time_num = 0

                subject = dict()
                subject["cluster"] = clusterId
                subject["subjectId"] = subjectId
                subject["subtime_sum"] = subtime_sum
                workload_min = 65535
                # teacher_length = len(generation.subject[subjectId]["teacher"])
                if generation.subject[subjectId]["teacher"] != []:
                    for teacherId in generation.subject[subjectId]["teacher"]:
                        if generation.teachers[teacherId]["workload"] < workload_min:
                            workload_min = generation.teachers[teacherId]["workload"]
                            teacher_min_Id = teacherId
                    # for teacherId in range(teacher_length):
                    #     if generation.teachers[count]["workload"] < workload_min :
                    #         teacherId = count
                    #         workload_min = generation.teachers[count]["workload"]
                    subject["teacher"] = teacher_min_Id
                    generation.teachers[teacher_min_Id]["workload"] += subtime_sum
                    generation.teachers[teacher_min_Id]["subject"].append({"cluster": clusterId,
                                                                           "subject": subjectId,
                                                                           "subtime": subtime_sum})
                    # subject["course"] = list()

                    # course_list = cluster_dict[clusterId]["sub2cou"][subjectId]
                    # for course in course_list:
                    #     for i in range(generation.courses[course]["period"]):
                    #         b = Schedule(course, clusterId, teacherId, generation.courses[course]["unitId"])
                    #         subject["course"].append(b)
                    #         time_num += 1
                    # subject_arrange.append(subject)
                    cluster_arrange[clusterId]["subject"].append(subject)
                else:
                    string = "subject " + str(subjectId) + " dont have teachers\n"
                    error_control.error_info_generate(string)
        return cluster_arrange

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
                    # toolId = plan.toolcode2Id[toolcode]
                    # lesson["tool"] = plan.tools[toolId]["code"]
                    lesson["tool"] = toolcode
                time_list[time].append(lesson)
            else:
                time_list[time] = list()
                lesson = {"cluster": cluster,
                          "teacher": plan.teachers[teacher]["teacherId"],
                          "lessonNo": plan.courses[courseId]["lessonNo"],
                          "classroomNo": plan.classroom[room]["classroomCode"],
                          "unitId": course.unitId,
                          "subjectId" : subjectId}
                if toolcode != -1:
                    # toolId = plan.toolcode2Id[toolcode]
                    # lesson["tool"] = plan.tools[toolId]["code"]
                    lesson["tool"] = toolcode
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
                    daysOfWeek = date.weekday()
                    weekNo = rrule.rrule(rrule.WEEKLY, dtstart = plan.bus_day[0], until= date).count()
                    tmpClassId = '%015d' % lesson["cluster"]

                    noOfDay = time - start + 1
                    if plan.week_on[daysOfWeek] == 1:
                        if noOfDay > plan.lessonNumAm :
                            timePeriod = 3
                        else:
                            timePeriod = 2
                    elif plan.week_on[daysOfWeek] == 2:
                        timePeriod = 2
                    elif plan.week_on[daysOfWeek] == 3:
                        noOfDay += plan.lessonNumAm
                        timePeriod = 3

                    new_dict = dict()
                    new_dict["gradeId"]     = 0                     #数据缺失
                    new_dict["lessonNo"]    = lesson["lessonNo"]
                    new_dict["noOfDay"]     = noOfDay
                    new_dict["adjustType"]  = 0
                    new_dict["sortNumber"]  = lesson_count
                    new_dict["classroomId"] = lesson["classroomNo"]
                    new_dict["daysOfWeek"]  = daysOfWeek + 1
                    new_dict["subjectId"]   = lesson["subjectId"]
                    new_dict["orgId"]       = plan.schedule["orgId"]
                    new_dict["classTime"]   = noOfDay + (plan.lessonNumPm + plan.lessonNumAm) * daysOfWeek
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
                    new_dict["statusFlag"]  = 1

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

    sortNumber = 1
    cluster_result = list()
    for clusterID in plan.cluster_dict:
        cluster_info = dict()
        cluster_info["semester"] = plan.schedule["semester"]

        # cluster_info["userId"] = list()
        # cluster_info["classId"] = list()
        # for studentNo in plan.cluster_dict[clusterID]["students"]:
        #     cluster_info["userId"].append(plan.students[studentNo]["idNo"])
        #     cluster_info["classId"].append(plan.students[studentNo]["classId"])
        #
        # cluster_info["goalId"] = list()
        # for goal in plan.cluster_dict[clusterID]["goalId"]:
        #     cluster_info["goalId"].append(goal)

        cluster_info["subjectId"] = list()
        cluster_info["unitId"] = list()
        for subjectId in plan.cluster_dict[clusterID]["sub2cou"]:
            cluster_info["subjectId"].append(subjectId)
            for courseNo in plan.cluster_dict[clusterID]["sub2cou"][subjectId]:
                lessonNo = plan.courses[courseNo]["lessonNo"]
                cluster_info["unitId"].append(lessonNo)

        cluster_info["totalLessonNum"] = plan.cluster_dict[clusterID]["times_total"]
        cluster_info["orgId"] = plan.schedule["orgId"]
        cluster_info["statusFlag"] = 1
        # cluster_info["sortNumber"] = sortNumber
        cluster_info["tmpClassId"] = '%015d' % clusterID

        # sortNumber += 1
        # cluster_result.append(cluster_info)
        for studentNo in plan.cluster_dict[clusterID]["students"]:
            cluster_info["userId"] = plan.students[studentNo]["idNo"]
            cluster_info["classId"] = plan.students[studentNo]["classId"]
            cluster_info["goalId"] = plan.students[studentNo]["goalId"]
            cluster_info["sortNumber"] = sortNumber
            sortNumber += 1
            cluster_result.append(copy.deepcopy(cluster_info))

    result["data"]["studentTimeTableList"] = cluster_result
    result["data"]["timeTableList"] = timeTableList
    result = json.dumps(result, indent=3, ensure_ascii=False)
    # with open('result.json', 'w') as f:
    #     f.write(result)
    #     f.close()
    # return time_list
    return result

def write2json(result):
    with open('result.json', 'w') as f:
        f.write(result)
        f.close()

