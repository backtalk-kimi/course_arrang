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

plan = generation()
cluster_num = plan.cluster_num
cluster_arrange = plan.arrange(cluster_num)
#种群规模popsize，精英个体数elite，进化代数maxiter
ga = GeneticOptimize(popsize=300,elite=30,mutprob=0.8,maxiter=200)
bestSchedule,successMark= ga.evolution(cluster_arrange=cluster_arrange, plan= plan)

schedule_result = result_disply(bestSchedule, plan, successMark)

error_control.error_info_display()
error_control.write2json(schedule_result)
# def NumOfCluster(plan):
#     total_subject_time = 0
#     for subjectId in plan.subject:
#         total_subject_time += plan.subject[subjectId]["subjectNumber"]
#     if total_subject_time != 0
#         cluster_num_max = plan.times_sum // total_subject_time + 1