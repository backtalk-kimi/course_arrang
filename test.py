import json
import pandas as pd
import numpy as np
import geatpy as ea
import matplotlib.pyplot as plt
import time
import datetime



# def DateInput(str):
#     date = str.split('-')
#     for i in range(3):
#         date[i] = int(date[i])
#     someday = datetime.date(year=date[0],month=date[1],day=date[2])
#     return someday
#
# schedule = content['schedule']
# day1 = DateInput(schedule['startTermBegin'])
# day2 = DateInput(schedule['startTermEnd'])
# interval = day2 - day1
# print(interval.days)
#
# schedule = content['schedule']
# day1 = schedule['startTermBegin']
# day2 = schedule['startTermEnd']
#
# day1 = datetime.datetime.strptime(day1,'%Y-%m-%d')
# day2 = datetime.datetime.strptime(day2,'%Y-%m-%d')
# interval = day2 - day1
# print(interval.days)

class generation():
    with open('排课入参测试数据.json', 'rb') as f:
        content = json.load(f)
    students = content['students']
    teachers = content['teachers']
    classroom = content['classrooms']
    courses = content['courses']
    tools = content['tools']
    schedule = content['schedule']

    def __init__(self):
        return
    def student_level_statistics(self):
        return

    def teacher_count(self):
        self.teacher_num = len(generation.teachers)
        return self.teacher_num

    def course_count(self):
        self.course_num = len(generation.courses)
        return self.course_num

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


    def week_num_count(self):
        day1 = generation.schedule['startTermBegin']
        day2 = generation.schedule['startTermEnd']

        day1 = datetime.datetime.strptime(day1,'%Y-%m-%d')
        day2 = datetime.datetime.strptime(day2,'%Y-%m-%d')
        interval = day2 - day1
        total_num = interval.days

        holiday_num = len(generation.schedule['holiday'])

        week_num = total_num//7
        self.week_num = week_num
        return week_num

    def course_arrange_weekly(week_num, period):
        if period % week_num == 0:
            return period/week_num
        else:
            return (period//week_num + 1)

    def arrange_plan_generation(self):

        generation.teacher_count(self)

        generation.course_teacher_relation(self)
        arrange_dict = dict()
        count = 0
        for course in self.courses:
            course_code = int(course['code']) % 10 - 1
            course_code = course_code * 3
            if len(self.course_teacher_dict[course['code']]) == 1:
                t = 3
                for i in range(3):
                    teacher = self.course_teacher_dict[course['code']][0]
                    teacher_code = int(teacher) % 10 - 1
                    arrange_dict[count] = {'course_num': course_code + i,
                                           'teacher_num': teacher_code,
                                           'weekly_course': t}
                    count += 1
                    t -= 1
            else:
                t = 3
                teacher1 = self.course_teacher_dict[course['code']][0]
                teacher_code = int(teacher1) % 10 - 1
                arrange_dict[count] = {'course_num': course_code,
                                       'teacher_num': teacher_code,
                                       'weekly_course': t}
                count += 1
                t -= 1

                teacher2 = self.course_teacher_dict[course['code']][1]
                teacher_code = int(teacher2) % 10 - 1
                arrange_dict[count] = {'course_num': course_code + 1,
                                       'teacher_num': teacher_code,
                                       'weekly_course': t}
                count += 1
                t -= 1

                arrange_dict[count] = {'course_num': course_code + 2,
                                       'teacher_num': teacher_code,
                                       'weekly_course': t}
                count += 1

        self.arrange_dict = arrange_dict
        return arrange_dict

