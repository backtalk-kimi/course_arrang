#coding=UTF-8
import copy
import numpy as np
import random
import error_control

class Schedule:
    def __init__(self, courseId, classId, teacherId, unitId):
        self.courseId = courseId
        self.classId = classId
        self.teacherId = teacherId
        self.unitId = unitId

    def random_init(self, time, plan):
        self.random_room(plan)
        self.random_tool(plan)
        self.time = time
        return

    def random_room(self, plan):
        typeId = plan.courses[self.courseId]["typeId"]
        if typeId == plan.classes[self.classId]["classroomtypeId"]:
            self.roomId = plan.classes[self.classId]["classroomCode"]
        else:
            self.roomId = np.random.choice(plan.room_type[typeId])

    def random_tool(self, plan):
        if "toolsCode" in plan.courses[self.courseId]:
            if type(plan.courses[self.courseId]["toolsCode"]) == list:
                self.tool = np.random.choice(plan.courses[self.courseId]["toolsCode"])
            else:
                self.tool = plan.courses[self.courseId]["toolsCode"]
        else:
            self.tool = -1


class GeneticOptimize:
    def __init__(self, popsize=64, elite=16, mutprob=0.5, crossprob = 0.3, maxiter=500):
        # 种群的规模（0-100）
        self.popsize = popsize
        # 变异概率
        self.mutprob = mutprob
        # 交叉概率
        self.crossprob = crossprob
        # 精英个数
        self.elite = elite
        # 进化代数（100-500）
        self.maxiter = maxiter

    def EntityGener(self, class_arrange, plan):
        class_dict = plan.classes
        entity = list()
        for class_node in class_arrange:
            classes = dict()
            classes["class_id"] = class_node["classId"]

            times_total = class_node["times_total"]
            classes["times_total"] = times_total
            classes["subject"] = list()
            a = list(range(self.times_sum))
            a = random.sample(a, times_total)
            a.sort()
            for s in class_node["subject"]:
                subtime_sum = s["subtime_sum"]
                subjectId = s["subjectId"]
                b = random.sample(a, subtime_sum)
                for time in b:
                    a.remove(time)
                b.sort()
                count = 0
                subject = dict()
                subject["subject_id"] = subjectId
                subject["subtime_sum"] = s["subtime_sum"]
                subject["teacher"] = s["teacher"]
                subject["course"] = list()
                # course_list = class_dict[class_id]["sub2cou"][subjectId]
                course_list = s["courses"]
                for course in course_list:
                    for i in range(plan.courses[course]["period"]):
                        c = Schedule(course, s["classId"], s["teacher"], plan.courses[course]["unitId"])
                        c.random_init(b[count], plan)
                        count += 1
                        subject["course"].append(c)
                        # time_num += 1
                classes["subject"].append(subject)
            entity.append(classes)
        return entity
        # self.population.append(subject_arrange)

    #随机初始化不同的种群
    def init_population(self, class_arrange, plan):
        self.population = []
        self.times_sum = plan.times_sum
        # class_dict = plan.classes
        for i in range(self.popsize):
            new = self.EntityGener(class_arrange, plan)
            self.population.append(new)

    #变异
    def mutate(self, eiltePopulation, plan):
        #选择变异的个数
        # e = np.random.randint(0, self.elite, 1)[0]
        e = self.roulettewheel()
        ep = copy.deepcopy(eiltePopulation[e])
        for clbum in ep:
            for subject in clbum["subject"]:
                # lesson_list = subject_list["course"]
                if subject["course"][0].tool == -1:
                    rand = np.random.rand()
                    if rand < 0.8:
                        self.time_change(subject)
                    else:
                        self.room_change(subject, plan)
                else:
                    rand = np.random.rand()
                    if rand < 0.5:
                        self.time_change(subject)
                    elif rand < 0.75:
                        self.room_change(subject, plan)
                    else:
                        self.tool_change(subject, plan)
        return ep

    def rouletteRate(self, conflict_list):
        sum = 0
        for i in conflict_list:
            sum = sum + i
        conflict = [sum - i for i in conflict_list]
        for i in conflict:
            sum = sum + i
        conflict_rate = [i/sum for i in conflict]
        self.conflict_rate = conflict_rate
        return

    def roulettewheel(self):
        fSlice = np.random.rand()
        cfTotal = 0
        selection = self.elite - 1
        for i in range(self.elite):
            cfTotal = cfTotal + self.conflict_rate[i]
            if cfTotal > fSlice:
                selection = i
                break
        return selection

    def time_change(self, subject):
        time_mutate_rate = 0.4
        if np.random.rand() < time_mutate_rate:
            times_total = subject["subtime_sum"]
            a = list(range(self.times_sum))
            a = random.sample(a, times_total)
            a.sort()
            for i in range(times_total):
                subject["course"][i].time = a[i]
        return

    # def time_change(self, subject):
    #     time_mutate_rate = 0.3
    #     lesson_length = subject["subtime_sum"]
    #     # a = list(map(lambda x : subject["course"][x].time, [y for y in range(lesson_length)]))
    #     mutate_num = int(lesson_length * time_mutate_rate)
    #     b = list(range(lesson_length))
    #     b = random.sample(b, mutate_num)
    #     for i in b:
    #         if i == 0:
    #             start = -1
    #             end = subject["course"][i + 1].time
    #         elif i == lesson_length - 1:
    #             start = subject["course"][i - 1].time
    #             end = self.times_sum
    #         else:
    #             start = subject["course"][i - 1].time
    #             end = subject["course"][i + 1].time
    #         time = np.random.randint(start + 1, end, 1)[0]
    #         subject["course"][i].time = time
    #
    #     return


    def room_change(self, subject, plan):
        for i in range(subject["subtime_sum"]):
            subject["course"][i].random_room(plan)
    def tool_change(self, subject, plan):
        for i in range(subject["subtime_sum"]):
            subject["course"][i].random_tool(plan)

    def crossover(self, eiltePopulation):
        e1 = self.roulettewheel()
        e2 = self.roulettewheel()
        if e2 == e1:
            e2 = (e1 + 1) % self.elite
        entity = list()
        for class1, class2 in zip(eiltePopulation[e1], eiltePopulation[e2]):
            classes = dict()
            classes["class_id"] = class1["class_id"]
            classes["times_total"] = class1["times_total"]
            classes["subject"] = list()
            for subject1, subject2 in zip(class1["subject"], class2["subject"]):
                Slice = np.random.rand()
                if Slice > 0.5:
                    subject = copy.deepcopy(subject1)
                else:
                    subject = copy.deepcopy(subject2)
                classes["subject"].append(subject)
            entity.append(classes)
        return entity

    # def crossover(self, eiltePopulation):
    #     e1 = np.random.randint(0, self.elite, 1)[0]
    #     e2 = np.random.randint(0, self.elite, 1)[0]
    #     pos = np.random.randint(0, 3, 1)[0]
    #     ep1 = copy.deepcopy(eiltePopulation[e1])
    #     ep2 = eiltePopulation[e2]
    #
    #     number = len(ep1)
    #     for i in range(number):
    #         length = ep1[i]["subtime_sum"]
    #         if pos == 0:
    #             for j in range(length):
    #                 ep1[i]["course"][j].time = ep2[i]["course"][j].time
    #         if pos == 1:
    #             for j in range(length):
    #                 ep1[i]["course"][j].roomId = ep2[i]["course"][j].roomId
    #         if pos == 2:
    #             for j in range(length):
    #                 if ep1[i]["course"][j].tool != -1:
    #                     ep1[i]["course"][j].tool = ep2[i]["course"][j].tool
    #     return ep1
    def EntityTimeList(self, entity):
        time_list = [None] * self.times_sum
        for clbum in entity:
            class_id = clbum["class_id"]
            for subject in clbum["subject"]:
                teacher_id = subject["teacher"]
                for lesson in subject["course"]:
                    time = lesson.time
                    toolcode = lesson.tool
                    classroom = lesson.roomId
                    if time_list[time] == None:
                        time_list[time] = dict()
                        time_list[time]["teacherId"] = dict()
                        time_list[time]["toolcode"] = dict()
                        time_list[time]["roomId"] = dict()
                        time_list[time]["class"] = dict()
                    if teacher_id in time_list[time]["teacherId"]:
                        time_list[time]["teacherId"][teacher_id] += 1
                    else:
                        time_list[time]["teacherId"][teacher_id] = 1
                    if toolcode in time_list[time]["toolcode"]:
                        time_list[time]["toolcode"][toolcode] += 1
                    else:
                        time_list[time]["toolcode"][toolcode] = 1
                    if classroom in time_list[time]["roomId"]:
                        time_list[time]["roomId"][classroom] += 1
                    else:
                        time_list[time]["roomId"][classroom] = 1
                    if class_id in time_list[time]["class"]:
                        time_list[time]["class"][class_id] += 1
                    else:
                        time_list[time]["class"][class_id] = 1
        return time_list

    def ConflictLocation(self, entity):
        time_list = self.EntityTimeList(entity)
        message = ""
        for time in time_list:
            if time:
                for teacher_id in time["teacherId"]:
                    if time["teacherId"][teacher_id] > 1:
                        print("teacherId = {},conflict = {}".format(teacher_id, time["teacherId"][teacher_id]))
                for classroom in time["roomId"]:
                    if time["roomId"][classroom] > 1:
                        print("roomId = {},conflict = {}".format(classroom, time["roomId"][classroom]))
                for toolcode in time["toolcode"]:
                    if toolcode != -1:
                        if time["toolcode"][toolcode] > self.toolcode2num[toolcode]:
                            print("toolcode = {},conflict = {}".format(toolcode, time["toolcode"][toolcode]))
                for class_id in time["class"]:
                    if time["class"][class_id] > 1:
                        print("classId = {},conflict = {}".format(class_id, time["class"][class_id]))


    def schedule_cost(self):
        conflicts = []
        detail_info = []
        # n = len(population[0])
        for entity in self.population:
            time_list = self.EntityTimeList(entity)
            score = 0
            teacher_score = 0
            room_score = 0
            tool_score = 0
            class_score = 0
            for time in time_list:
                if time:
                    for teacher_id in time["teacherId"]:
                        teacher_score += time["teacherId"][teacher_id] - 1
                    for classroom in time["roomId"]:
                        room_score += time["roomId"][classroom] - 1
                    for toolcode in time["toolcode"]:
                        if toolcode != -1:
                            if time["toolcode"][toolcode] > self.toolcode2num[toolcode]:
                                tool_score += time["toolcode"][toolcode] - self.toolcode2num[toolcode]
                    for class_id in time["class"]:
                        class_score += time["class"][class_id] - 1
            score = teacher_score + room_score + tool_score + class_score
            # score = teacher_score * 10 + room_score * 10 + tool_score * 10 + class_score
            DetailScore = [score, teacher_score, room_score, tool_score, class_score]
            detail_info.append(DetailScore)
            conflicts.append(score)

        index = np.array(conflicts).argsort()
        return index[: self.elite], detail_info[index[0]], conflicts

    def evolution(self, class_arrange, plan):
        bestScore = 0
        bestSchedule = None
        self.init_population(class_arrange, plan)
        self.toolcode2num = plan.toolcode2num
        for i in range(self.maxiter):
            eliteIndex, bestScore, total_conflict = self.schedule_cost()
            print('Iter: {} | conflict: {} | TeacherConflict: {} | RoomConflict: {} | ToolConflict: {} | ClassConflict: {}'.format(i + 1, bestScore[0], bestScore[1], bestScore[2], bestScore[3], bestScore[4]))
            Iter = i + 1
            RunningInformation = 'Iter: {} | conflict: {} | TeacherConflict: {} | RoomConflict: {} | ToolConflict: {} | ClassConflict: {}\n'.format(i + 1, bestScore[0], bestScore[1], bestScore[2], bestScore[3], bestScore[4])
            error_control.running_information(RunningInformation)

            if bestScore[0] == 0:
                bestSchedule = self.population[eliteIndex[0]]
                break
            else:
                if i%20 == 0:
                    self.ConflictLocation(self.population[eliteIndex[0]])
            newPopulation = [self.population[index] for index in eliteIndex]
            conflict_list = [total_conflict[index] for index in eliteIndex]
            self.rouletteRate(conflict_list)

            while len(newPopulation) < self.popsize:
                rand = np.random.rand()
                if rand < self.mutprob:
                    newp = self.mutate(newPopulation, plan)
                elif rand < self.mutprob + self.crossprob:
                    newp = self.crossover(newPopulation)
                else:
                    newp = self.EntityGener(class_arrange, plan)
                newPopulation.append(newp)
            self.population = newPopulation

        successMark = 1
        if bestSchedule == None:
            bestSchedule = self.population[eliteIndex[0]]
            successMark = 0
        return bestSchedule, successMark
