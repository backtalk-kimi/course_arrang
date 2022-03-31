import numpy as np


class lesson():
    def __init__(self, course, roomtype, subject, classroom = -1):
        self.course = course
        self.classroom = classroom
        self.subject = subject
        self.teacher = teacher
        self.roomtype = roomtype

class TimeNode():
    def __init__(self):
        self.classrooms = dict()
        self.teachers = dict()
        self.tools = dict()
        self.classes = dict()
    def ResourceInit(plan):
        TimeNode.classroom_type = plan.room_type
        TimeNode.toolcode_num = plan.toolcode2num

    def Check(self, lesson):

def CourseListTurn(plan, subject, class_id):
    lesson_list = list()
    for course in subject["courses"]:
        times = plan.courses[course]["period"]
        roomtype = plan.courses[course]["typeId"]
        # if plan.courses[course]["toolsCode"]:               #教具部分暂时搁置
        #     toolscode = plan.courses[course]["toolsCode"]
        if classroom_type == plan.classes[class_id]["classroomtypeId"]:
            new_lesson = lesson(course, roomtype, subject["subjectId"], plan.classes[class_id]["classroomCode"])
        else:
            new_lesson = lesson()
        # lesson_list = lesson_list + [course] * times
    subject["lesson"] = lesson_list


def BruteForce(plan, class_arrange):
    times = plan.times_sum
    TimeNode.ResourceInit(plan)
    for time in range(times):
        new_node = TimeNode()
        for clumb in class_arrange:
            subject_list = clumb["subject"]
            count_list = [0] * len(clumb)
            count = 0
            for subject in subject_list:
                if subject["subtime_sum"] > 0:
                    lesson =
                    new.check()


