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
        return l

def list_display(l):
    length = len(l)
    for id in range(length):
        print("teacher:%d\tcourse:%d\ttime:%d\troom:%d"%(l[id].teacher,l[id].course,l[id].time,l[id].room))
    return



plan = education_plan()
plan_list = education_plan.list_generation(plan)
list_display(plan_list)