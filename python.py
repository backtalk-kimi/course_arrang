#coding=UTF-8
import numpy as np
from genetic import *
from pandas import *
from generation import *
import error_control


plan = generation()
class_arrange = plan.Arrange()

# arrange_info = plan.ArrangeAdjust()
arrange_info = plan.ArrangeDisplay()
error_control.write2json(arrange_info, 'arrange.json')
#种群规模popsize，精英个体数elite，进化代数maxiter
ga = GeneticOptimize(popsize= 100 ,elite= 50, mutprob=0.5,crossprob = 0.4, maxiter= 100)
bestSchedule,successMark= ga.evolution(class_arrange=class_arrange, plan= plan)

schedule_result = result_disply(bestSchedule, plan, successMark)

error_control.error_info_display()
error_control.write2json(schedule_result, 'result.json')
