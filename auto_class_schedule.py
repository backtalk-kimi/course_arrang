import numpy as np
import random
import data_entire

teacher_num=10
course_num=20
time_num=25 #一共有25个时间段
room_num=5 #有5个教室

# team_num=5


class course_range:
    def __init__(self,teacher,course,time,room):  #,team
        self.teacher =teacher
        self.course=course
        self.time=time
        self.room=room
        # self.team=team

def list_generation():  #列表使用中括号，生成初始解空间
    l=[]
    for i in range(20):
        para=[]
        for j in range(2):
            # print('请输入第 %d 个3参数'%(j+1))
            # #使用str.format() 进行格式化输出
            # print('请输入第{}个参数:\n'.format(j+1))
            # para_temp=input()
            # para_temp=int(para_temp)
            # para.append(para_temp)
            if j==0:
                para_temp=random.randint(1,25)
            else:
                para_temp=random.randint(1,5)
            # elif j==2:
            #     para_temp=random.randint(1,5)
            # else:
            #     para_temp=random.randint(1,5)

            para.append(para_temp)

        temp=course_range(int(i/2+1),i+1,para[0],para[1])
        l.append(temp)
    return l

def group_generation(): #生成种群
    g=[]
    for i in range(30):
        l=list_generation()
        g.append(l)
    return g

g=group_generation()


def judge_conflict():
    score = np.zeros(30, int)  # 给每个方案评分
    # print(score[10])
    for ans in range(30):
        for i in g[ans]:
            for j in g[ans]:
                if (i.course!=j.course and i.teacher == j.teacher and i.time == j.time):
                    score[ans]-=1
                if (i.course != j.course and  i.time == j.time and i.room == j.room ):
                    score[ans]-=1
    return score

# score=judge_conflict()
# print(score)

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
    for i in range(60):
        print('第{}轮打分情况:\n'.format(i+1))
        cross_action()
    # for i in range(20):
    #     print('第{}条排课:\n'.format(i+1),g[0][i].teacher , g[0][i].course , g[0][i].time , g[0][i].room)
main()