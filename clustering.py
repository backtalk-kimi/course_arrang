#coding=UTF-8
# from test import generation
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


class cluster:
    def __init__(self, plan, cluster_num = 3):
        cluster.clustering(plan, cluster_num)
        self.cluster_goalid_generate(plan)
        self.subject_arrange(plan)
        return
    def embeding_build(plan):
        students = plan.students
        student_num = len(students)
        goal_max = 300
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

    def clustering(plan, clusters):
        std_num, embeding = cluster.embeding_build(plan)
        kmeans = KMeans(n_clusters = clusters, random_state= 0, init='k-means++').fit(embeding)
        # print(kmeans.labels_)
        label_list = kmeans.labels_
        # print(kmeans.cluster_centers_)
        # print(kmeans.inertia_)
        # print(kmeans.n_iter_)
        # print(kmeans.n_features_in_)
        # print(kmeans.feature_names_in_(2))
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
                    break
                cluster_course = cluster_course + id2course[j]
            cluster_course = list(set(cluster_course))

            cluster_dict[i]["sub2cou"] = dict()
            cluster_dict[i]["sub_times"] = dict()
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
                    while(times < subject_dict[k]["subjectNumber"]):
                        times = times + plan.courses[temp[count]]["period"]
                        subject_times.append(times)
                        temp1.append(temp[count])
                        count = (count + 1) % length
                    cluster_dict[i]["sub2cou"][k] = temp1
                    cluster_dict[i]["sub_times"][k] = subject_times

        plan.cluster_dict = cluster_dict
        return

