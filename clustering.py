#coding=UTF-8
# from test import generation
import numpy as np
import pandas as pd
from sklearn.cluster import SpectralClustering
import error_control
# import matplotlib.pyplot as plt

# from generation import *

class Cluster:
    def __init__(self, plan):
        self.LoadDataSet(plan)
        # self.cluster_num_max = clusterNum

    # 数据集生成
    def LoadDataSet(self, plan):
        dataMat = []
        StudentList = plan.students
        StudentNum = len(StudentList)
        self.StudentNum = StudentNum
        self.cluster_num_max = StudentNum
        for student in StudentList:
            CourseList = student["course"]
            dataMat.append(CourseList)
        self.dataMat = dataMat
        precomputed_matrix = self.sub_correlation_matrix(dataMat)
        self.precomputed_matrix = precomputed_matrix
        return dataMat, precomputed_matrix

    def sub_correlation_matrix(self, dataMat):
        StudentNum = len(dataMat)
        precomputed_matrix = np.zeros((StudentNum, StudentNum))
        for i in range(StudentNum):
            for j in range(i , StudentNum):
                distance = self.Distance(dataMat[i], dataMat[j])
                precomputed_matrix[i][j] = distance
                precomputed_matrix[j][i] = distance
        # print(precomputed_matrix)
        self.precomputed_matrix = precomputed_matrix
        return precomputed_matrix


    # 计算两个向量的距离
    def Distance(self, listA, listB):
        if listA != [] and listB != []:
            AandB = len(set(listA) & set(listB))
            AorB = len(set(listA + listB))
            distance = AandB / AorB
        elif listA == listB:
            distance = 1
        else:
            distance = 0
        return distance

    def cluster_progress(self, cluster_num):
        pred_y = SpectralClustering(n_clusters=cluster_num, random_state=1, affinity='precomputed').fit_predict(
            self.precomputed_matrix)
        cluster_list = list()
        for cluster in range(cluster_num):
            cluster = dict()
            cluster["students"] = list()
            # cluster["course"] = list()
            cluster_list.append(cluster)
        count = 0
        for i in pred_y:
            cluster_list[i]["students"].append(count)
            count += 1
        for cluster in cluster_list:
            course_list = list()
            for student_id in cluster["students"]:
                course_list = course_list + self.studentList[student_id]["course"]
            cluster["studentNum"] = len(cluster["students"])
            course_list = list(set(course_list))
            course_list.sort()
            cluster["course"] = course_list
        return cluster_list
    # 谱聚类
    def ClusterSpectral(self, plan):
        self.studentList = plan.students

        cluster_num_max = self.cluster_num_max
        std_num = self.StudentNum

        cluster_num_list = []
        Distance_avg_list = []

        for cluster_num in range(1, cluster_num_max):
            Distance_sum = 0
            cluster_list = self.cluster_progress(cluster_num)
            for cluster in cluster_list:
                for student_id in cluster['students']:
                    course_list = self.studentList[student_id]['course']
                    Distance_sum += self.Distance(course_list, cluster['course'])
            # Distance_avg = Distance_sum
            cluster_num_list.append(cluster_num)
            Distance_avg_list.append(Distance_sum)
        best_clusternum = self.bestClusterNum(Distance_avg_list, cluster_num_list)
        cluster_list = self.cluster_progress(best_clusternum)
        self.cluster_list = cluster_list
        self.course2students_gene()
        self.classroom_check(plan)
        # self.lessonlen_check(plan, cluster_list)                  length of lesson check!!!
        self.SubjectArrange(plan)
        # self.cluster_display(cluster_dict)
        # cluster_dict = self.course2students_gene(cluster_dict)

        plan.cluster_list = cluster_list
        return cluster_list

    def bestClusterNum(self, Distance_avg_list, cluster_num_list):
        # plt.plot(cluster_num_list, Distance_avg_list)
        # plt.show()
        max_ratio = -1
        max_id = -1
        for i in range(1, len(Distance_avg_list) - 1):
            f1 = Distance_avg_list[i + 1] - Distance_avg_list[i]
            f2 = Distance_avg_list[i] - Distance_avg_list[i - 1]
            ratio = f1 + f2 - f1 * f2
            # print("ratio ", i ," = ", ratio)
            if ratio > max_ratio:
                max_ratio = ratio
                max_id = i
        bestClusterNum = cluster_num_list[max_id]

        information = "bestClusterNum = " + str(bestClusterNum) + "\n"
        error_control.error_info_generate(information)

        # print("bestClusterNum = ", bestClusterNum)
        return bestClusterNum


    def classroom_check(self, plan):
        cluster_list = self.cluster_list
        check_mark = 1
        while(check_mark):
            check_mark = 0
            clusterId = 0
            for cluster in cluster_list:
                course_no = 0
                for course in cluster["course"]:
                    course_id = course["courseId"]

                    typeId = plan.courses[course_id]["typeId"]
                    student_num = course["studentsNum"]
                    max_room = 0
                    for roomId in plan.room_type[typeId]:
                        if max_room < plan.classroom[roomId]["maxStudents"]:
                            max_room = plan.classroom[roomId]["maxStudents"]
                    if max_room < student_num:
                        cluster["course"] = self.recluster(cluster["course"], course_no, max_room)
                        check_mark = 1
                    course_no += 1
                clusterId += 1
        self.cluster_list = cluster_list
        return cluster_list

    def lessonlen_check(self, plan, cluster_dict):
        times_sum = plan.times_sum
        for clusterId in cluster_dict:
            lessonlen = 0
            for courseId in cluster_dict[clusterId]["course"]:
                lessonlen += plan.courses[courseId]["period"]
            if lessonlen > times_sum:
                information = "Cluster " + str(clusterId) + "'s courses are out of range.Please decrease lesson number of the students in this clusters.\n"
                information += "Students of cluster: \n"
                for studentId in cluster_dict[clusterId]['students']:
                    information += self.studentList[studentId]["idNo"] + "\n"
                error_control.error_info_generate(information)
                error_control.error_info(310)

    def recluster(self, course_list, course_no, max_room):
        course = course_list[course_no]
        students_num = course["students_num"]
        if students_num % max_room:
            lesson_num = students_num // max_room + 1
        else:
            lesson_num = students_num // max_room
        num = students_num // lesson_num
        students_list = course["students"]
        # mark = 0
        for i in range(lesson_num - 1):
            new_course = copy.deepcopy(course)
            new_course["students"] = students_list[: num]
            new_course["students_num"] = num
            del students_list[: num]
            course_list.insert(course_no, new_course)
        course["students_num"] = len(course["students"])
        return course_list
    # def recluster(self, cluster_list, cluster_id, course_students, max_room):
    #     student_list = cluster_list[cluster_id]["students"]
    #
    #     # del cluster_list[clusterId]
    #
    #     clusterId_bias = 0
    #     for clusterId in cluster_dict:
    #         if clusterId_bias < clusterId:
    #             clusterId_bias = clusterId
    #     clusterId_bias += 1
    #
    #     dataMat = []
    #     StudentList = plan.students
    #     std_num = len(studentId_list)
    #     for studentId in studentId_list:
    #         CourseList = plan.students[studentId]["course"]
    #         dataMat.append(CourseList)
    #     precomputed_matrix = self.sub_correlation_matrix(dataMat)
    #     pred_y = SpectralClustering(n_clusters = clusterNum, random_state=1, affinity='precomputed').fit_predict(precomputed_matrix)
    #
    #     new_cluster_dict = dict()
    #     count = 0
    #     for i in pred_y:
    #         clusterId = clusterId_bias + i
    #         studentId = studentId_list[count]
    #         plan.students[studentId]["label"] = clusterId
    #         if clusterId in new_cluster_dict:
    #             new_cluster_dict[clusterId]["students"].append(studentId)
    #         else:
    #             new_cluster_dict[clusterId] = dict()
    #             new_cluster_dict[clusterId]["students"] = list()
    #             new_cluster_dict[clusterId]["students"].append(studentId)
    #         count += 1
    #     for cluster in new_cluster_dict:
    #         course_list = list()
    #         for student_id in new_cluster_dict[cluster]["students"]:
    #             course_list = course_list + plan.students[student_id]["course"]
    #         course_list = list(set(course_list))
    #         course_list.sort()
    #         new_cluster_dict[cluster]["course"] = course_list
    #     # cluster_dict = self.subject_arrange(plan, cluster_dict)
    #     cluster_dict.update(new_cluster_dict)
    #     return cluster_dict

    def cluster_display(self, cluster_dict):
        for cluster_id in cluster_dict:
            print("cluster_id = ", cluster_id)
            print("cluster_course = ", cluster_dict[cluster_id]["course"])
            for student_id in cluster_dict[cluster_id]["students"]:
                course_list = self.studentList[student_id]["course"]
                print(student_id, course_list)
        return
# 学生从班级课表中选择需要上的目标上课
    def course2students_gene(self):
        cluster_list = self.cluster_list
        for cluster in cluster_list:
            course_list = cluster["course"]
            course2students = dict()
            count = 0
            for course_id in course_list:
                course2students[course_id] = list()
                course = dict()
                course["courseId"] = course_id
                course["students"] = list()
                course_list[count] = course
                count += 1
            for student_id in cluster["students"]:
                for course_id in self.studentList[student_id]["course"]:
                    userId = self.studentList[student_id]["idNo"]
                    course2students[course_id].append(userId)
            for course in course_list:
                course_id = course["courseId"]
                course["students"] = course2students[course_id]
                course["studentsNum"] = len(course2students[course_id])
        # self.cluster_list = cluster_list
        return


# 科目安排生成
    def SubjectArrange(self, plan):
        cluster_list = self.cluster_list
        subject_dict = plan.subject
        for cluster in cluster_list:
            subject_arrange = dict()
            course_list = cluster["course"]
            for course in course_list:
                course_id = course["courseId"]
                subject_id = plan.courses[course_id]["subjectId"]
                if subject_id not in subject_arrange:
                    subject_arrange[subject_id] = list()
                subject_arrange[subject_id].append(course)
            cluster["subject"] = subject_arrange
        return cluster_list

        # for i in cluster_dict:
        #     course_list = cluster_dict[i]["course"]
        #     cluster_dict[i]["sub2cou"] = dict()
        #     cluster_dict[i]["sub_times"] = dict()
        #     cluster_dict[i]["times_total"] = 0
        #     times_total = 0
        #     if course_list == []:
        #         continue
        #     for k in subject_dict:
        #         course_list = set(course_list)
        #         sub_cor_set = set(subject_dict[k]["course"])
        #         temp = list(course_list & sub_cor_set)
        #         temp.sort()
        #         if temp:
        #             times = 0
        #             for course_id in temp:
        #                 times = times + plan.courses[course_id]["period"]
        #             cluster_dict[i]["sub2cou"][k] = temp
        #             cluster_dict[i]["sub_times"][k] = times
        #             times_total += times
        #     cluster_dict[i]["times_total"] = times_total
        # return cluster_dict

# # test
# plan = generation()
#
# cluster_num = 7
# clustering = cluster(plan)
# clustering.cluster_spectral(plan=plan, cluster_num=cluster_num)
# clustering.cluster_display(plan)
# print('Done')
