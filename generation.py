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
from clustering import Cluster
import error_control
from genetic import *
import random


class generation():

    def __init__(self):
        generation.input_information(self)
        generation.schedule_info_read(self)
        generation.subject_info(self)
        generation.tool_info(self)
        generation.room_info(self)
        return

    def input_information(self):
        content = error_control.input_init()
        generation.students = content['students']
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
                        string = "No " + str(count) + " teacher is free"
                        error_control.error_info_generate(string)
            else:
                if sub in generation.subject:
                    generation.subject[sub]["teacher"].append(count)
                else:
                    print("No",count,"teacher is free")
                    string = "No " + str(count) + " teacher is free"
                    error_control.error_info_generate(string)
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
        self.GoalToCourse()
        self.StudentCourseListGener()
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

    # 根据GoalList生成学生的CourseList
    def StudentCourseListGener(self):
        std_totalLessonNum = 0

        for student in self.students:
            GoalList = student["goalId"]
            CourseList = list()
            totalLessonNum = 0
            for goal in GoalList:
                if goal in self.goalid2course:
                    Course = self.goalid2course[goal][0]
                    CourseList.append(Course)
            CourseList = list(set(CourseList))
            for CourseId in CourseList:
                totalLessonNum += self.courses[Course]["period"]
            student["course"] = CourseList
            student["totalLessonNum"] = totalLessonNum
            std_totalLessonNum += totalLessonNum
            if totalLessonNum > int(self.times_sum * 0.8):
                userId = student["idNo"]
                infomation = "The courses of " + userId + " is too many.\n"
                error_control.error_info_generate(infomation)
                error_control.error_info(301)
                exit()
        self.std_totalLessonNum = std_totalLessonNum
        return

    def clusterNum_gener(self):
        min_clusterNum = self.std_totalLessonNum // self.times_sum + 1
        self.min_clusterNum = min_clusterNum
        return min_clusterNum

    def GoalToCourse(self):
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

    def Arrange(self):
        clustering = Cluster(self)
        cluster_list = clustering.ClusterSpectral(self)
        # cluster_arrange = dict()
        class_id = 0
        class_arrange = list()
        for cluster in cluster_list:
            class_info = dict()
            class_info["classId"] = class_id
            class_info["subject"] = list()
            class_info["timesTotal"] = 0
            for subject_id in cluster["subject"]:
                subject_info = dict()
                subject_info["subtimeSum"] = 0
                subject_info["subjectId"] = subject_id
                subject_info["course"] = list()
                for course in cluster["subject"][subject_id]:
                    course_info = copy.deepcopy(course)
                    course_id = course["courseId"]
                    course_info["courseId"] = course_id
                    course_info["period"] = self.courses[course_id]["period"]
                    course_info["typeId"] = self.courses[course_id]["typeId"]
                    if "toolsCode" in self.courses[course_id]:
                        course_info["toolsCode"] = self.courses[course_id]["toolsCode"]
                    # course_info["unitId"] = self.courses[course_id]["unitId"]
                    subject_info["subtimeSum"] += course_info["period"]
                    subject_info["course"].append(course_info)
                class_info["subject"].append(subject_info)
                class_info["timesTotal"] += subject_info["subtimeSum"]
            class_arrange.append(class_info)
            class_id += 1
        for class_info in class_arrange:
            for subject_info in class_info["subject"]:
                subject_id = subject_info["subjectId"]
                workload_min = 65535
                for teacher_no in self.subject[subject_id]["teacher"]:
                    if self.teachers[teacher_no]["workload"] < workload_min:
                        workload_min = self.teachers[teacher_no]["workload"]
                        teacher_min_Id = teacher_no
                subject_info["teacher"] = teacher_min_Id
                self.teachers[teacher_min_Id]["workload"] += subject_info["subtimeSum"]
                self.teachers[teacher_min_Id]["subject"].append({
                                                                    "class": class_info["classId"],
                                                                    "subject": subject_id,
                                                                    "subtime": subject_info["subtimeSum"]
                                                                })
        self.class_arrange = class_arrange
        self.TeacherWorkloadSort()
        return class_arrange

    def ArrangeAdjust(self, adjust_info):
        adjust_list = list()
        for teacher_id in adjust_info:
            subject_list = adjust_info[teacher_id]

            adjust_list.append([teacher_id, subject_list[0]])
        for adjust in adjust_list:
            class_id = adjust[1]
            teacher_id = adjust[0]
            for subject in self.class_arrange[class_id]["subject"]:
                if subject["teacher"] == teacher_id:
                    self.class_arrange[class_id]["timeTotal"] = self.class_arrange[class_id]["timesTotal"] - \
                                                                  subject["subtimeSum"]
                    self.class_arrange[class_id]["subject"].remove(subject)
                    self.teachers[teacher_id]["workload"] -= subject["subtimeSum"]
                    for subject in self.teachers[teacher_id]["subject"]:
                        if subject["class"] == class_id:
                            self.teachers[teacher_id]["subject"].remove(subject)
                            break
                    break
        self.TeacherWorkloadSort()
        return self.class_arrange

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
        subjects_count = 0
        # arrange = self.class_arrange
        for class_node in self.class_arrange:
            node = dict()
            # class_id = clbum["subject"][0]["classId"]
            node["classId"] = class_node["classId"]
            node["totalLessonNum"] = class_node["timesTotal"]
            node["subject"] = list()
            for subject in class_node["subject"]:
                sub_info = dict()
                sub_info["subjectId"] = subject["subjectId"]
                sub_info["teacherId"] = teacher_list[subject["teacher"]]["teacherId"]
                sub_info["lessonNum"] = subject["subtimeSum"]
                node["subject"].append(sub_info)
                subjects_count += 1
            class_info.append(node)

        arrange_info["TotalSubjectNumber"] = subjects_count
        arrange_info["teacherInfo"] = teacher_info
        arrange_info["classInfo"] = class_info
        return arrange_info


def student_info_display(studentNo, plan, cluster_info):
    student_info = copy.deepcopy(cluster_info)
    del student_info["subjectId"]
    del student_info["sub2unitId"]
    student_info["unitId"] = list()
    student_info["subjectId"] = list()
    for courseId in plan.students[studentNo]["course"]:
        student_info["unitId"].append(plan.courses[courseId]["lessonNo"])
    for subjectId in cluster_info["subjectId"]:
        set1 = set(cluster_info["sub2unitId"][subjectId])
        set2 = set(student_info["unitId"])
        if set1 & set2 :
            student_info["subjectId"].append(subjectId)
    student_info["userId"] = plan.students[studentNo]["idNo"]
    student_info["classId"] = plan.students[studentNo]["classId"]
    student_info["goalId"] = plan.students[studentNo]["goalId"]

    return student_info


def result_disply(schedules, plan, successMark):
    time_list = [None] * plan.times_sum
    class_count = 0
    for clumb in schedules:
        class_id = clumb["class_id"]
        subject_list = clumb["subject"]
        subject_count = 0
        for subject in subject_list:
            subject_id = subject["subject_id"]
            teacher_id = subject["teacher"]
            course_count = 0
            count = 0
            for course in subject["course"]:
                time = course.time
                room = course.roomId
                toolcode = course.tool
                course_id = course.courseId

                course_info = plan.class_arrange[class_count]["subject"][subject_count]["course"][course_count]
                period = course_info["period"]

                if not time_list[time]:
                    time_list[time] = list()
                lesson = {"cluster": class_id,
                          "teacher": plan.teachers[teacher_id]["teacherId"],
                          "lessonNo": plan.courses[course_id]["lessonNo"],
                          "classroomNo": plan.classroom[room]["classroomNo"],
                          "unitId": plan.courses[course_id]["unitId"],
                          "studentId": course_info["students"],
                          "subjectId": subject_id}
                if toolcode != -1:
                    lesson["tool"] = toolcode
                time_list[time].append(lesson)
                count += 1
                if count == period:
                    count = 0
                    course_count += 1

            subject_count += 1
        class_count += 1

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
                    new_dict["studentId"] = lesson["studentId"]
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

    # sortNumber = 1
    # student_result = list()

    # class_id = 0
    # for classes in plan.class_arrange:
    #     class_info = dict()
    #     class_info["semester"] = plan.schedule["semester"]
    #     class_info["subjectId"] = classes["subejct"]
    #     class_info["sub2unitId"] = dict()
    #     class_info["orgId"] = plan.schedule["orgId"]
    #     class_info["statusFlag"] = 1
    #     # cluster_info["sortNumber"] = sortNumber
    #     class_info["tmpClassId"] = '%015d' % class_id
    #     for studentNo in classes["students"]:
    #         student_info = student_info_display(studentNo, plan, cluster_info)
    #         student_info["sortNumber"] = sortNumber
    #         sortNumber += 1
    #         student_result.append(student_info)
    #
        # class_info = dict()
        # class_info["semester"] = plan.schedule["semester"]
        # class_info["subjectId"] = list()
        # class_info["sub2unitId"] = dict()
        # for subjectId in plan.class_arrange[clusterID]["sub2cou"]:
        #     class_info["subjectId"].append(subjectId)
        #     class_info["sub2unitId"][subjectId] = list()
        #     for courseNo in plan.cluster_dict[clusterID]["sub2cou"][subjectId]:
        #         lessonNo = plan.courses[courseNo]["lessonNo"]
        #         cluster_info["sub2unitId"][subjectId].append(lessonNo)
        # cluster_info["orgId"] = plan.schedule["orgId"]
        # cluster_info["statusFlag"] = 1
        # # cluster_info["sortNumber"] = sortNumber
        # cluster_info["tmpClassId"] = '%015d' % clusterID
        # for studentNo in plan.cluster_dict[clusterID]["students"]:
        #     student_info = student_info_display(studentNo, plan, cluster_info)
        #     student_info["sortNumber"] = sortNumber
        #     sortNumber += 1
        #     student_result.append(student_info)

    # result["data"]["studentTimeTableList"] = student_result
    result["data"]["timeTableList"] = timeTableList
    # result = json.dumps(result, indent=3, ensure_ascii=False)
    return result

def write2json(result):
    with open('result.json', 'w') as f:
        f.write(result)
        f.close()

