# imput data from txt

import codecs
import pandas as pd
import random
import numpy as np
import re
import copy


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
        lines = data[2].split('=')
        self.teachers_num = int(lines[1])

        length = len(data)
        self.length = length - 3

        for line in range(3,length):
            lines = data[line].split(' ')
            self.teachers.append(int(lines[0]))
            self.courses.append(int(lines[1]))
            self.course_num_week.append(int(lines[2]))

        # print(teachers)
        # print(courses)
        # print(course_num_week)



class arrange_list():
    def __init__(self,education_plan):
        l = list()
        for id in range(education_plan.length):
            for course_id in range(education_plan.course_num_week[id]):
                course_time = random.randint(1,education_plan.time)
                course_room = random.randint(1,education_plan.class_num)
                temp = course_range(education_plan.teachers[id],education_plan.courses[id],course_time,course_room)
                l.append(temp)
        self.arrange = l
        self.gene_count = len(self.arrange)
        self.time = education_plan.time
        self.class_num = education_plan.class_num
        self.teachers_num = education_plan.teachers_num

    # def __init__(self,arrange_list,num):
    #     self.gene_count = arrange_list.gene_count
    #     self.time = arrange_list.time
    #     self.class_num = arrange_list.class_num
    #     self.teachers_num = arrange_list.teachers_num
    #     l = list()
    #     for id in range(arrange_list.gene_count):
    #         temp = course_range(arrange_list[id].teacher, arrange_list[id].course, arrange_list[id].time, arrange_list[id].room)
    #         l.append(temp)
    #     self.arrange = l
    #     self.score = arrange_list.score
    # 变异过程程序
    def variation(self, rate):
        l = self.arrange
        num = self.gene_count

        # print("count = %d"%(num))

        var_num = int(rate * num)
        var_list = random.sample(range(num),var_num)
        for id in range(var_num):
            var = var_list[id]
            # print("varnum:%d\tteacher:%d\tcourse:%d\ttime:%d\troom:%d" % (var,l[var].teacher, l[var].course, l[var].time, l[var].room))
            l[var].time = random.randint(1, self.time)
            l[var].room = random.randint(1, self.class_num)
            # print("teacher:%d\tcourse:%d\ttime:%d\troom:%d" % (l[var].teacher, l[var].course, l[var].time, l[var].room))
        self.arrange = l
        return l

    def list_display(self):
        l = self.arrange
        length = self.gene_count
        for id in range(length):
            print("teacher:%d\tcourse:%d\ttime:%d\troom:%d" % (l[id].teacher, l[id].course, l[id].time, l[id].room))
        return

    def judge_conflict(self):

        l = self.arrange
        score = 0

        workload = np.zeros((self.teachers_num,5),dtype=np.int)


        for i in range(self.gene_count):
        # 基本限制条件
            for j in range(i+1,self.gene_count):
                if (l[i].course != l[j].course and l[i].teacher == l[j].teacher and l[i].time == l[j].time):
                    score -= 1
                if (l[i].course != l[j].course and l[i].time == l[j].time and l[i].room == l[j].room):
                    score -= 1
            teacher = l[i].teacher-1
            date = int((l[i].time-1) / 5)  # 课程安排在周几
            workload[teacher][date] += 1
        # 保证每个老师每天上课少于2节
        for i in range(self.teachers_num):
            for j in range(5):
                if (workload[i][j] > 2):
                    score -= 1
        self.score = score
        return score

# plan = education_plan()

# plan_list = arrange_list(plan)
# score = arrange_list.judge_conflict(plan_list)
# print("变异前得分:",score)
# arrange_list.variation(plan_list,0.2)
# score = arrange_list.judge_conflict(plan_list)
# print("变异后得分:",score)

def group_generation(plan,num): #生成种群
    group = list()
    for i in range(num):
        l=arrange_list(plan)
        arrange_list.judge_conflict(l)
        group.append(l)
    return group





def cross_action(list, entity_num, cross_rate, gene_rate):
    cross_num = int(entity_num * cross_rate / 2)
    gene_count = list[0].gene_count
    gene_num = int(gene_count * gene_rate)
    cross_gene = random.sample(range(gene_count), gene_num)

    for id in range(cross_num):
        father_number = 2 * id
        mother_number = 2 * id + 1
        father = copy.deepcopy(list[father_number].arrange)
        mother = copy.deepcopy(list[mother_number].arrange)
        for i in cross_gene:
            temp_time = father[i].time
            temp_room = father[i].room
            father[i].time = mother[i].time
            father[i].room = mother[i].room
            mother[i].time = temp_time
            mother[i].room = temp_room
        list[entity_num - father_number - 1].arrange = father
        arrange_list.judge_conflict(list[entity_num - father_number - 1])
        list[entity_num - mother_number - 1].arrange = mother
        arrange_list.judge_conflict(list[entity_num - mother_number - 1])

    return list

def main():
    plan = education_plan()
    group_num = 300
    g = group_generation(plan,group_num)
    g.sort(key=lambda x:x.score,reverse = True)
    for i in range(50):
        print("score[%d]=%d"%(i,g[i].score))
    for i in range(200):
        cross_action(g,group_num,0.2,0.2)
        g.sort(key=lambda x: x.score, reverse=True)
    print("_____________________________________________________")
    for i in range(50):
        print("score[%d]=%d"%(i,g[i].score))


main()