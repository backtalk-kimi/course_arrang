#coding=UTF-8
import numpy as np
from genetic import *
from pandas import *
from generation import *
import os
import error_control

plan = generation()
class_arrange = plan.Arrange()
successMark = 0
count = 1

#种群规模popsize，精英个体数elite，进化代数maxiter
while successMark == 0:
    arrange_info = plan.ArrangeDisplay()
    error_control.arrange_info_display(arrange_info, count)
    ga = GeneticOptimize(popsize= 100 ,elite= 50, mutprob=0.5,crossprob = 0.4, maxiter= 50)
    bestSchedule,successMark= ga.evolution(class_arrange = class_arrange, plan = plan)
    adjust_teacher = ga.ConflictLocation(bestSchedule)
    class_arrange = plan.ArrangeAdjust(adjust_teacher)
    count += 1
schedule_result = result_disply(bestSchedule, plan, successMark)

error_control.error_info_display()
error_control.write2json(schedule_result, 'result.json')