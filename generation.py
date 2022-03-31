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
import error_control
from genetic import *
import random



class generation():
    def __init__(self):
        generation.input_information(self)
        generation.room_info(self)
        generation.subject_info(self)
        generation.schedule_info_read(self)
        generation.tool_info(self)
        return

    def input_information(self):
        content = error_control.input_init()
        generation.classes = content['classes']
        generation.teachers = content['teachers']
        generation.classroom = content['classrooms']
        generation.subject = content['subjects']
        generation.courses = content['courses']
        generation.tools = content['tools']
        generation.schedule = content['schedule']
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
        generation.subject = subject

        self.TeacherInfo()
        self.course_info()
        self.ClassInfo()
        return
# 老师信息读取和安排
    def TeacherInfo(self):
        generation.teacher_num = len(generation.teachers)
        # teacher_work = [0] * generation.teacher_num
        count = 0
        teacherId2count = dict()
        for i in generation.teachers:
            teacherId = str(i["teacherId"])
            teacherId2count[teacherId] = count

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

        self.teacherId2count = teacherId2count
        # self.teacher_work = teacher_work
        return

# 课程信息读取和安排
    def course_info(self):
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

    def Class_RoomInfo(self, class_info):
        classroomCode = class_info["classroomCode"]
        i = 0
        for classroom in self.classroom:
            if classroomCode == classroom["classroomCode"]:
                classroomCode = i
                break
            i += 1

        for typrId in self.room_type:
            if classroomCode in self.room_type[typrId]:
                class_info["classroomtypeId"] = typrId
                break
        class_info["classroomCode"] = classroomCode
        return

    def ClassInfo(self):
        id2course = self.goalid2course
        subject_dict = self.subject
        class_list = list()
        for class_info in generation.classes:
            class_course = list()
            times_total = 0
            for j in class_info["goalId"]:
                if j not in id2course:
                    print("goal", j, "has no course")
                else:
                    class_course.append(id2course[j][0])
            class_course = list(set(class_course))
            class_info["sub2cou"] = dict()
            class_info["sub_times"] = dict()
            self.Class_RoomInfo(class_info)
            times_total = 0
            for k in subject_dict:
                class_course = set(class_course)
                sub_cor_set = set(subject_dict[k]["course"])
                temp = list(class_course & sub_cor_set)
                temp.sort()
                if temp:
                    subject_times = list()
                    times = 0
                    # length = len(temp)
                    count = 0
                    for temp_i in temp:
                        times = times + self.courses[temp_i]["period"]
                        subject_times.append(times)
                    class_info["sub2cou"][k] = temp
                    class_info["sub_times"][k] = subject_times
                    times_total += times
            class_info["times_total"] = times_total
        #     class_list.append(class_info)
        # generation.classes = class_list
        return


    def Arrange(self):
        class_arrange = list()
        count = 0
        for class_info in self.classes:
            class_node = dict()
            # classId = class_info["classId"]
            classId = count
            # class_arrange[classId] = dict()
            class_node["classId"] = classId

            times_total = class_info["times_total"]
            if times_total > self.times_sum:
                error_control.error_info(301)
            class_node["times_total"] = 0
            class_node["subject"] = list()
            for subjectId in class_info["sub2cou"]:
                length = len(class_info["sub_times"][subjectId])
                subtime_sum = class_info["sub_times"][subjectId][length - 1]
                subject = dict()
                subject["classId"] = classId
                subject["subjectId"] = subjectId
                subject["subtime_sum"] = subtime_sum
                if type(class_info["teacherId"]) == list:
                # print(type(class_info["teacherId"]))
                    for teacherId in class_info["teacherId"]:
                        if teacherId in self.teacherId2count:
                            teacherNo = self.teacherId2count[teacherId]
                            if self.teachers[teacherNo]["subjectId"] == subjectId:
                                subject["teacher"] = teacherNo
                                break
                else:
                    teacherId = class_info["teacherId"]
                    teacherNo = self.teacherId2count[teacherId]
                    if self.teachers[teacherNo]["subjectId"] == subjectId:
                        subject["teacher"] = teacherNo

                if "teacher" in subject:
                    subject["courses"] = class_info["sub2cou"][subjectId]
                    class_node["subject"].append(subject)
                    class_node["times_total"] += subject["subtime_sum"]
                    generation.teachers[teacherNo]["workload"] += subtime_sum
                    generation.teachers[teacherNo]["subject"].append({"class": classId,
                                                                      "subject": subjectId,
                                                                      "subtime": subtime_sum})
                else:
                    # error_control.error_info(302)
                    string = str(class_info["classId"]) + " " + str(subjectId) + "don't have no teacher" + "\n"
                    error_control.error_info_generate(string)
            count += 1

            class_arrange.append(class_node)
        self.class_arrange = class_arrange
        self.TeacherWorkloadSort()
        return class_arrange

    def TeacherWorkloadSort(self):
        teacher_list = self.teachers
        teacher_workload = list(map(lambda x: x["workload"], teacher_list))
        index = np.array(teacher_workload).argsort()
        index = list(reversed(index))
        self.teacher_index = index

        for teacher in self.teachers:
            class_lesson = list(map(lambda x:x["subtime"],teacher["subject"]))
            indexes = np.array(class_lesson).argsort()
            new_list = list()
            for index in indexes:
                new_list.append(teacher["subject"][index])
            teacher["subject"] = new_list
        return

    def ArrangeAdjust(self):
        # teacher_ids = self.teacher_index[0:3]
        teacher_ids = [1, 13, 14, 15, 15, 19, 31, 33, 12]
        teacher_list = self.teachers
        S_list = list()
        for teacher_id in teacher_ids:
            S = []
            subject_node = teacher_list[teacher_id]["subject"][-1]
            teacher_list[teacher_id]["subject"].remove(subject_node)
            S.append(subject_node["class"])
            S.append(subject_node["subject"])
            S_list.append(S)
        for S in S_list:
            class_num = S[0]
            subject_id = S[1]
            for subject in self.class_arrange[class_num]["subject"]:
                if subject["subjectId"] == subject_id:
                    self.class_arrange[class_num]["times_total"] = self.class_arrange[class_num]["times_total"] - subject["subtime_sum"]
                    self.class_arrange[class_num]["subject"].remove(subject)
                    break
        return self.class_arrange

    def ArrangeDisplay(self):
        arrange_info = dict()
        teacher_info = list()
        index = self.teacher_index
        teacher_list = self.teachers
        for i in index:
            teacher = dict()
            teacher["teacherId"] = teacher_list[i]["teacherId"]
            teacher["workload"] = teacher_list[i]["workload"]
            teacher_info.append(teacher)
        class_info = list()
        # arrange = self.class_arrange
        for class_node in self.class_arrange:
            node = dict()
            # class_id = clbum["subject"][0]["classId"]
            node["classId"] = class_node["classId"]
            node["totalLessonNum"] = class_node["times_total"]
            node["subject"] = list()
            for subject in class_node["subject"]:
                sub_info = dict()
                sub_info["subjectId"] = subject["subjectId"]
                sub_info["teacherId"] = teacher_list[subject["teacher"]]["teacherId"]
                sub_info["lessonNum"] = subject["subtime_sum"]
                node["subject"].append(sub_info)
            class_info.append(node)
        arrange_info["teacherInfo"] = teacher_info
        arrange_info["classInfo"] = class_info
        return arrange_info


def result_disply(schedules, plan, successMark):
    time_list = [None] * plan.times_sum
    for classes in schedules:
        class_num = classes["class_id"]
        subject_list = classes["subject"]
        for subject in subject_list:
            subject_id = subject["subject_id"]
            teacher_id = subject["teacher"]
            for course in subject["course"]:
                time = course.time
                room = course.roomId
                toolcode = course.tool

                course_id = course.courseId
                if not time_list[time]:
                    time_list[time] = list()

                lesson = {"class": class_num,
                          "teacher": plan.teachers[teacher_id]["teacherId"],
                          "lessonNo": plan.courses[course_id]["lessonNo"],
                          "classroomCode": plan.classroom[room]["classroomCode"],
                          "unitId": course.unitId,
                          "subjectId": subject_id}

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
                    tmpClassId = '%015d' % 0
                    classNUM = lesson["class"]
                    classId = plan.classes[classNUM]["classId"]

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
                    new_dict["classroomId"] = lesson["classroomCode"]
                    new_dict["daysOfWeek"]  = daysOfWeek + 1
                    new_dict["subjectId"]   = lesson["subjectId"]
                    new_dict["orgId"]       = plan.schedule["orgId"]
                    new_dict["classTime"]   = noOfDay + (plan.lessonNumPm + plan.lessonNumAm) * daysOfWeek
                    new_dict["teacherId"]   = lesson["teacher"]
                    new_dict["scheduleType"]= 1
                    new_dict["weeksSum"]    = 1
                    new_dict["scheduleDay"] = date.strftime("%Y-%m-%d")
                    new_dict["timePeriod"]  = timePeriod
                    new_dict["unitId"]      = lesson["unitId"]
                    new_dict["semester"]    = plan.schedule["semester"]
                    new_dict["weekNo"]      = weekNo
                    new_dict["startTime"]   = "00:00:00"            #数据缺失
                    new_dict["endTime"]     = "00:00:00"            #数据缺失
                    new_dict["tmpClassId"]  = tmpClassId
                    new_dict["classId"] = classId
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


    result["data"]["timeTableList"] = timeTableList
    # result = json.dumps(result, indent=3, ensure_ascii=False)
    return result



