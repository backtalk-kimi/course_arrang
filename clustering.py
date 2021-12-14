#coding=UTF-8
# from test import generation
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN


class cluster:
    def __init__(self, plan, cluster_num = 3):
        cluster.clustering_kmeans(plan, cluster_num)
        self.cluster_goalid_generate(plan)
        self.subject_arrange(plan)
        return
    def embeding_build(plan):
        students = plan.students
        student_num = len(students)
        goal_max = 1000
        std_embedding = np.zeros([student_num, goal_max])
        i = 0
        for student in students:
            if type(student["goalId"]) == list:
                for j in student["goalId"]:
                    std_embedding[i, j] = 1
            else:
                # print("student_num = ",i, "goal = ",student["goalId"])
                j = student["goalId"]
                std_embedding[i, j] = 1
            i += 1
        return student_num, std_embedding

    def clustering_kmeans(plan, clusters):
        std_num, embeding = cluster.embeding_build(plan)
        if std_num > clusters:
            kmeans = KMeans(n_clusters = clusters, random_state= 0, init='k-means++').fit(embeding)

            label_list = kmeans.labels_

            count = 0
            cluster_dict = dict()
            for i in label_list:
                plan.students[count]["label"] = i
                if i in cluster_dict:
                    cluster_dict[i]["students"].append(count)
                else:
                    cluster_dict[i] = dict()
                    cluster_dict[i]["students"] = list()
                    cluster_dict[i]["students"].append(count)
                count += 1
        else:
            cluster_dict = dict()
            for i in range(std_num):
                cluster_dict[i] = dict()
                cluster_dict[i]["students"] = list()
                cluster_dict[i]["students"].append(i)
        plan.cluster_dict = cluster_dict
        # help(kmeans)
        return

    def cluster_goalid_generate(self, plan):
        cluster_dict = plan.cluster_dict
        for i in cluster_dict:
            cluster_dict[i]["goalId"] = list()
            for j in cluster_dict[i]["students"]:
                cluster_dict[i]["goalId"] = cluster_dict[i]["goalId"] + plan.students[j]["goalId"]
            cluster_dict[i]["goalId"] = list(set(cluster_dict[i]["goalId"]))
            cluster_dict[i]["goalId"].sort()
            # print(i, cluster_dict[i]["goalId"])
        return

    # embeding = clustering(plan, 3)
    def display(self, plan):
        print(plan.cluster_dict)
        for j in plan.cluster_dict:
            print("the",j,"kind of students:")
            for i in plan.cluster_dict[j]["students"]:
                print(plan.students[i]["goalId"])

    def subject_arrange(self, plan):
        cluster_dict = plan.cluster_dict
        id2course = plan.goalid2course
        subject_dict = plan.subject
        for i in cluster_dict:
            cluster_course = list()
            for j in cluster_dict[i]["goalId"]:
                if j not in id2course:
                    print("goal",j,"has no course")
                    # global infomation
                    # infomation += 'goal,%d,has no course'%(j)
                    # break
                else:
                    cluster_course.append(id2course[j][0])
            cluster_course = list(set(cluster_course))

            cluster_dict[i]["sub2cou"] = dict()
            cluster_dict[i]["sub_times"] = dict()
            times_total = 0
            for k in subject_dict:
                cluster_course = set(cluster_course)
                sub_cor_set = set(subject_dict[k]["course"])
                temp = list(cluster_course & sub_cor_set)
                temp.sort()
                if temp:
                    subject_times = list()
                    times = 0
                    length = len(temp)
                    count = 0
                    temp1 = list()
                    # while(times < subject_dict[k]["subjectNumber"]):
                    #     times = times + plan.courses[temp[count]]["period"]
                    #     subject_times.append(times)
                    #     temp1.append(temp[count])
                    #     count = (count + 1) % length
                    # for course_temp in temp:
                    #     times += plan.courses[course_temp]["period"]
                    # if times < plan.subject[k]["subjectNumber"]:
                    #     course_num_list = [0] * length
                    #     while (times < subject_dict[k]["subjectNumber"]):
                    #         times = times + plan.courses[temp[count]]["period"]
                    #         course_num_list[count] += 1
                    #         count = (count + 1) % length
                    #     times = 0
                    #     for temp_i in range(length):
                    #         for temp_j in range(course_num_list[temp_i]):
                    #             times = times + plan.courses[temp[temp_i]]["period"]
                    #             subject_times.append(times)
                    #             temp1.append(temp[temp_i])
                    # else:




                    course_num_list = [0] * length
                    while (times < subject_dict[k]["subjectNumber"]):
                        times = times + plan.courses[temp[count]]["period"]
                        course_num_list[count] += 1
                        count = (count + 1) % length
                    times = 0
                    for temp_i in range(length):
                        if course_num_list[temp_i] == 0:
                            print("cluster", i,"subject", k, "course", plan.courses[temp[temp_i]]["lessonNo"],"is not in arrange")
                            # global infomation
                            # infomation += 'cluster, %d,subject, %d, course, %s,课时数不足'%(i,k,plan.courses[temp[temp_i]]["lessonNo"])
                        else:
                            for temp_j in range(course_num_list[temp_i]):
                                times = times + plan.courses[temp[temp_i]]["period"]
                                subject_times.append(times)
                                temp1.append(temp[temp_i])
                    cluster_dict[i]["sub2cou"][k] = temp1
                    cluster_dict[i]["sub_times"][k] = subject_times
                    times_total += times
            cluster_dict[i]["times_total"] = times_total

        plan.cluster_dict = cluster_dict
        return

