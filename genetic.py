#coding=UTF-8
import copy
import numpy as np
import random

class Schedule:
    def __init__(self, courseId, classId, teacherId, unitId):
        self.courseId = courseId
        self.classId = classId
        self.teacherId = teacherId
        self.unitId = unitId
        #print(courseId, classId, teacherId)
        # self.weekDay = 0
        # self.slot = 0

    def random_init(self, time, plan):
        self.random_room(plan)
        self.random_tool(plan)
        self.time = time
        return

    def random_room(self, plan):
        typeId = plan.courses[self.courseId]["typeId"]
        self.roomId = np.random.choice(plan.room_type[typeId])

    def random_tool(self, plan):
        if "toolsCode" in plan.courses[self.courseId]:
            if type(plan.courses[self.courseId]["toolsCode"]) == list:
                self.tool = np.random.choice(plan.courses[self.courseId]["toolsCode"])
            else:
                self.tool = plan.courses[self.courseId]["toolsCode"]
        else:
            self.tool = -1


def conflict_judge(subject1, subject2, teachersame):
    conflict = 0
    if teachersame:
        j = 0
        length = len(subject2)
        for i in subject1:
            while j < length:
                if i.time > subject2[j].time:
                    j += 1
                else:
                    break
            if j == length:
                break
            if i.time == subject2[j].time:
                conflict += 1                               #教师冲突
                if i.roomId == subject2[j].roomId:
                    conflict += 1                           #教室冲突
                if i.tool != -1 and (i.tool == subject2[j].tool):
                    conflict += 1                           #教具冲突
    else:
        for i in subject1:
            while j < length:
                if i.time > subject2[j].time:
                    j += 1
                else:
                    break
            if j == length:
                break
            if i.time == subject2[j].time:
                if i.roomId == subject2[j].roomId:
                    conflict += 1  # 教室冲突
                if i.tool != -1 and (i.tool == subject2[j].tool):
                    conflict += 1  # 教具冲突
    return conflict



# def schedule_cost(population, elite):
#     conflicts = []
#     n = len(population[0])
#     for entity in population:
#         conflict = 0
#         for i in range(0, n - 1):
#             subject1 = entity[i]["course"]
#             for j in range(i + 1, n):
#                 subject2 = entity[j]["course"]
#                 if entity[i]["teacher"] == entity[j]["teacher"]:
#                     teachersame = 1
#                 else:
#                     teachersame = 0
#                 conflict = conflict + conflict_judge(subject1, subject2, teachersame)
#         conflicts.append(conflict)
#
#     index = np.array(conflicts).argsort()
#     return index[: elite], conflicts[index[0]]

def schedule_cost(ga, population, elite):
    conflicts = []
    n = len(population[0])

    for entity in population:
        time_list = [None] * ga.times_sum
        for subject in entity:
            teacherId = subject["teacher"]
            clusterId = subject["cluster"]
            for lesson in subject["course"]:
                time = lesson.time
                toolcode = lesson.tool
                classroom = lesson.roomId
                if time_list[time] == None:
                    time_list[time] = dict()
                    time_list[time]["teacherId"] = dict()
                    time_list[time]["toolcode"] = dict()
                    time_list[time]["roomId"] = dict()
                    time_list[time]["cluster"] = dict()
                if teacherId in time_list[time]["teacherId"]:
                    time_list[time]["teacherId"][teacherId] += 1
                else:
                    time_list[time]["teacherId"][teacherId] = 1
                if toolcode in time_list[time]["toolcode"]:
                    time_list[time]["toolcode"][toolcode] += 1
                else:
                    time_list[time]["toolcode"][toolcode] = 1
                if classroom in time_list[time]["roomId"]:
                    time_list[time]["roomId"][classroom] += 1
                else:
                    time_list[time]["roomId"][classroom] = 1
                if clusterId in time_list[time]["cluster"]:
                    time_list[time]["cluster"][clusterId] += 1
                else:
                    time_list[time]["cluster"][clusterId] = 1
        score = 0
        for time in time_list:
            if time:
                for teacherId in time["teacherId"]:
                    score += time["teacherId"][teacherId] - 1
                for classroom in time["roomId"]:
                    score += time["roomId"][classroom] - 1
                for toolcode in time["toolcode"]:
                    if toolcode != -1:
                        if time["toolcode"][toolcode] > ga.toolcode2num[toolcode]:
                            score += time["toolcode"][toolcode] - ga.toolcode2num[toolcode]
        conflicts.append(score)
    index = np.array(conflicts).argsort()
    return index[: elite], conflicts[index[0]]

class GeneticOptimize:
    def __init__(self, popsize=64, mutprob=0.5, elite=16, maxiter=500):
        # 种群的规模（0-100）
        self.popsize = popsize
        # 变异概率
        self.mutprob = mutprob
        # 精英个数
        self.elite = elite
        # 进化代数（100-500）
        self.maxiter = maxiter
        
    #随机初始化不同的种群
    def init_population(self, cluster_arrange, plan):
        self.population = []
        self.times_sum = plan.times_sum
        # for i in range(self.popsize):
        #     for subject in schedules:
        #         a = list(range(plan.times_sum))
        #         a = random.sample(a, subject["subtime_sum"])
        #         a.sort()
        #         for count in range(subject["subtime_sum"]):
        #             subject["course"][count].random_init(a[count], plan)
        #     self.population.append(copy.deepcopy(schedules))

        cluster_dict = plan.cluster_dict
        for i in range(self.popsize):
            subject_arrange = list()
            for clusterId in cluster_arrange:
                times_total = cluster_arrange[clusterId]["times_total"]
                a = list(range(plan.times_sum))
                a = random.sample(a, times_total)
                a.sort()
                for s in cluster_arrange[clusterId]["subject"]:
                    subtime_sum = s["subtime_sum"]
                    b = random.sample(a, subtime_sum)
                    for time in b:
                        a.remove(time)
                    b.sort()
                    count = 0

                    subject = dict()
                    subject["cluster"] = s["cluster"]
                    subject["subjectId"] = s["subjectId"]
                    subject["subtime_sum"] = s["subtime_sum"]
                    subject["teacher"] = s["teacher"]
                    subject["course"] = list()
                    subjectId = s["subjectId"]


                    course_list = cluster_dict[clusterId]["sub2cou"][subjectId]
                    for course in course_list:
                        for i in range(plan.courses[course]["period"]):
                            c = Schedule(course, s["cluster"], s["teacher"], plan.courses[course]["unitId"])
                            c.random_init(b[count], plan)
                            count += 1
                            subject["course"].append(c)
                            # time_num += 1
                    subject_arrange.append(subject)
            self.population.append(subject_arrange)

            
    #变异
    def mutate(self, eiltePopulation, plan):
        #选择变异的个数
        e = np.random.randint(0, self.elite, 1)[0]
        ep = copy.deepcopy(eiltePopulation[e])
        for subject in ep:
            if subject["course"][0].tool == -1:
                pos = np.random.randint(0, 2, 1)[0]
                if pos == 0:
                    self.time_change(subject)
                elif pos == 1:
                    self.room_change(subject, plan)
            else:
                pos = np.random.randint(0, 3, 1)[0]
                if pos == 0:
                    self.time_change(subject)
                elif pos == 1:
                    self.room_change(subject, plan)
                elif pos == 2:
                    self.tool_change(subject, plan)
        return ep

    # def time_change(self, subject):
    #     a = list(range(self.times_sum))
    #     a = random.sample(a, subject["subtime_sum"])
    #     a.sort()
    #     for i in range(subject["subtime_sum"]):
    #         subject["course"][i].time = a[i]
    #     return

    def time_change(self, subject):
        time_mutate_rate = 0.3
        lesson_length = subject["subtime_sum"]
        # a = list(map(lambda x : subject["course"][x].time, [y for y in range(lesson_length)]))
        mutate_num = int(lesson_length * time_mutate_rate)
        b = list(range(lesson_length))
        b = random.sample(b, mutate_num)
        for i in b:
            if i == 0:
                start = -1
                end = subject["course"][i + 1].time
            elif i == lesson_length - 1:
                start = subject["course"][i - 1].time
                end = self.times_sum
            else:
                start = subject["course"][i - 1].time
                end = subject["course"][i + 1].time
            time = np.random.randint(start + 1, end, 1)[0]
            subject["course"][i].time = time
        return


    def room_change(self, subject, plan):
        for i in range(subject["subtime_sum"]):
            subject["course"][i].random_room(plan)
    def tool_change(self, subject, plan):
        for i in range(subject["subtime_sum"]):
            subject["course"][i].random_tool(plan)

    # def change(self, value, valueRange):
    #     value = np.random.randint(1, valueRange+1, 1)[0]
    #     #value=(value)%valueRange+1
    #     return value

    def crossover(self, eiltePopulation):
        e1 = np.random.randint(0, self.elite, 1)[0]
        e2 = np.random.randint(0, self.elite, 1)[0]
        pos = np.random.randint(0, 3, 1)[0]
        ep1 = copy.deepcopy(eiltePopulation[e1])
        ep2 = eiltePopulation[e2]

        number = len(ep1)
        for i in range(number):
            length = ep1[i]["subtime_sum"]
            if pos == 0:
                for j in range(length):
                    ep1[i]["course"][j].time = ep2[i]["course"][j].time
            if pos == 1:
                for j in range(length):
                    ep1[i]["course"][j].roomId = ep2[i]["course"][j].roomId
            if pos == 2:
                for j in range(length):
                    if ep1[i]["course"][j].tool != -1:
                        ep1[i]["course"][j].tool = ep2[i]["course"][j].tool
        return ep1

    def evolution(self, cluster_arrange, plan):
        bestScore = 0
        bestSchedule = None
        self.init_population(cluster_arrange, plan)
        self.toolcode2num = plan.toolcode2num
        for i in range(self.maxiter):
            eliteIndex, bestScore = schedule_cost(self, self.population, self.elite)
            print('Iter: {} | conflict: {}'.format(i + 1, bestScore))
            if bestScore == 0:
                bestSchedule = self.population[eliteIndex[0]]
                break
            newPopulation = [self.population[index] for index in eliteIndex]
            while len(newPopulation) < self.popsize:
                if np.random.rand() < self.mutprob:
                    newp = self.mutate(newPopulation, plan)
                else:
                    newp = self.crossover(newPopulation)
                newPopulation.append(newp)
            self.population = newPopulation

        successMark = 1
        if bestSchedule == None:
            bestSchedule = self.population[eliteIndex[0]]
            successMark = 0
        return bestSchedule, successMark
