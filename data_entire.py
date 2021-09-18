# imput data from txt

import codecs
import pandas as pd
import random
import numpy
import re


class course_range:
    def __init__(self,teacher,course,time,room):  #,team
        self.teacher =teacher
        self.course=course
        self.time=time
        self.room=room
        # self.team=team

class education_plan():
    def __init__(self):
        self.teachers = list()
        self.courses = list()
        self.course_num_week = list()

        input_data = codecs.open('input.txt', 'r', 'utf-8')
        data = input_data.read().splitlines()
        lines = data[0].split('=')
        self.class_num = int(lines[1])
        lines = data[1].split('=')
        self.time = int(lines[1])

        length = len(data)
        self.length = length - 2

        for line in range(2,length):
            lines = data[line].split(' ')
            self.teachers.append(int(lines[0]))
            self.courses.append(int(lines[1]))
            self.course_num_week.append(int(lines[2]))

        # print(teachers)
        # print(courses)
        # print(course_num_week)

    def list_generation(self):
        l = list()
        for id in range(self.length):
            for course_id in range(self.course_num_week[id]):
                course_time = random.randint(1,self.time)
                course_room = random.randint(1,self.class_num)
                temp = course_range(self.teachers[id],self.courses[id],course_time,course_room)
                l.append(temp)
        self.arrange = l
        self.entity_count = len(self.arrange)
        return l

    # 变异过程程序
    def variation(self, rate):
        l = self.arrange
        num = self.entity_count

        # print("count = %d"%(num))

        var_num = int(rate * num)
        var_list = random.sample(range(num),var_num)
        for id in range(var_num):
            var = var_list[id]
            print("varnum:%d\tteacher:%d\tcourse:%d\ttime:%d\troom:%d" % (var,l[var].teacher, l[var].course, l[var].time, l[var].room))
            l[var].time = random.randint(1, self.time)
            l[var].room = random.randint(1, self.time)
            print("teacher:%d\tcourse:%d\ttime:%d\troom:%d" % (l[var].teacher, l[var].course, l[var].time, l[var].room))
        self.arrange = l
        return l

    def list_display(self):
        l = self.arrange
        length = self.entity_count
        for id in range(length):
            print("teacher:%d\tcourse:%d\ttime:%d\troom:%d" % (l[id].teacher, l[id].course, l[id].time, l[id].room))
        return

# class arrange():
#     def __init__(self):
#         l = list()
#         for id in range(self.length):
#             for course_id in range(self.course_num_week[id]):
#                 course_time = random.randint(1,self.time)
#                 course_room = random.randint(1,self.class_num)
#                 temp = course_range(self.teachers[id],self.courses[id],course_time,course_room)
#                 l.append(temp)
#         self.arrange = l
#         self.entity_count = len(self.arrange)
#         return l
#
#     # 变异过程程序
#     def variation(self, rate):
#         l = self.arrange
#         num = self.entity_count
#
#         # print("count = %d"%(num))
#
#         var_num = int(rate * num)
#         var_list = random.sample(range(num),var_num)
#         for id in range(var_num):
#             var = var_list[id]
#             print("varnum:%d\tteacher:%d\tcourse:%d\ttime:%d\troom:%d" % (var,l[var].teacher, l[var].course, l[var].time, l[var].room))
#             l[var].time = random.randint(1, self.time)
#             l[var].room = random.randint(1, self.time)
#             print("teacher:%d\tcourse:%d\ttime:%d\troom:%d" % (l[var].teacher, l[var].course, l[var].time, l[var].room))
#         self.arrange = l
#         return l
#
#     def list_display(self):
#         l = self.arrange
#         length = self.entity_count
#         for id in range(length):
#             print("teacher:%d\tcourse:%d\ttime:%d\troom:%d" % (l[id].teacher, l[id].course, l[id].time, l[id].room))
#         return

plan = education_plan()
plan_list = education_plan.list_generation(plan)
print("教学安排初始情况：")
education_plan.list_display(plan)
plan_list = education_plan.variation(plan,0.2)
print("变异之后情况：")
education_plan.list_display(plan)