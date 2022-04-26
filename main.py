#coding=UTF-8
import numpy as np
from genetic import *
from pandas import *
from generation import *
import os
import error_control

# path = 'result.json'
# if os.path.exists(path):  # 如果文件存在
#     os.remove(path)
# else:
#     print('no such file:',path)  # 则返回文件不存在


def NumOfCluster(plan):
    cluster_num_min = plan.clusterNum_gener()
    # total_subject_time = 0
    # for subjectId in plan.subject:
    #     total_subject_time += plan.subject[subjectId]["subjectNumber"]
    # if total_subject_time != 0:
    #     cluster_num_max = plan.times_sum // total_subject_time + 1
    #     student_num = len(plan.students)
    #     if cluster_num_max > student_num:
    #         cluster_num_max = student_num
    # else:
    #     error_control.error_info(000)
    #     cluster_num_max = 0
    return cluster_num_min


plan = generation()
Oright = NumOfCluster(plan)
right = Oright
left = 1
mid = right
while(left <= right):
    print("left = ", left,"mid = ",mid,"right = ",right)
    error_control.information_clean()
    cluster_arrange = plan.arrange(mid)
    #种群规模popsize，精英个体数elite，进化代数maxiter
    ga = GeneticOptimize(popsize=300,elite=30,mutprob=0.8,maxiter=200)
    bestSchedule,successMark = ga.evolution(cluster_arrange=cluster_arrange,plan= plan)
    if mid == Oright and successMark:
        schedule_result = result_disply(bestSchedule, plan, successMark)
        break
    if successMark == 1:
        left = mid + 1
        schedule_result = result_disply(bestSchedule, plan, successMark)
    else:
        right = mid - 1
    mid = (left + right) // 2

error_control.error_info_display()
error_control.write2json(schedule_result)

