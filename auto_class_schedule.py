import numpy as np
import random
import data_entire


def group_generation(plan,num): #生成种群
    group = list()
    for i in range(num):
        l=arrange_list(plan)
        arrange_list.judge_conflict(l)
        group.append(l)
    return group




#交叉互换  每次迭代产生两个新的个体， 直接替换掉得分最低的两个个体
def cross_action():
    score=judge_conflict()
    print(score)
    score_range=sorted(score)
    first_big=score_range[29]
    second_big=score_range[28]
    for i in range(30):
        if(score[i]== first_big):
            father_number=i
            break
    for j in range(30):
        if (score[j]==second_big and j!=father_number):
            mother_number=j
            break
    # 父母编号分别是 father_number   mother_number
    father=g[father_number]
    mother=g[mother_number]

    # 暂定让两条排课基因 进行交叉互换
    cross_1=random.randint(0,19)
    cross_2=random.randint(0,19)
    while(cross_1 == cross_2):
        cross_2 = random.randint(0, 19)

    temp_time=father[cross_1].time
    temp_room=father[cross_1].room
    father[cross_1].time = mother[cross_1].time
    father[cross_1].room = mother[cross_1].room
    mother[cross_1].time = temp_time
    mother[cross_1].room = temp_room

    temp_time=father[cross_2].time
    temp_room=father[cross_2].room
    father[cross_2].time = mother[cross_2].time
    father[cross_2].room = mother[cross_2].room
    mother[cross_2].time = temp_time
    mother[cross_2].room = temp_room

    # 用father mother 替换掉分数最低的两个个体
    first_small = score_range[0]
    second_small = score_range[1]
    for i in range(30):
        if(score[i]== first_small):
            agent_1=i
            break
    for j in range(30):
        if (score[j]==second_small and j!=agent_1):
            agent_2=j
            break
    g[agent_1] =father
    g[agent_2] =mother

    # return g

def main():
    plan = education_plan()
    group_num = 100
    g = group_generation(plan,group_num)
    g.sort(key=arrange_list.score)

main()