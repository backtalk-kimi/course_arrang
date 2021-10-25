import numpy as np
import time
import geatpy as ea
from test import generation
from aimfunc import aimfunc
from aimfunc import aimfunc1

# from openpyxl import Workbook ,load_workbook
plan = generation()
arrange = generation.arrange_plan_generation(plan)
course_num = len(plan.arrange_dict)

"""============================变量设置============================"""
ranges = list()
precisions = list()
scales = list()
b = list()
varTypes = list()

teacher_course = dict()
class_course = dict()

for i in range(plan.teacher_num):
    teacher_course[i] = []
for i in range(3):
    class_course[i] = []
course_count = 0

for course in range(course_num):
    for i in range(arrange[course]['weekly_course']):
        class_course[course % 3].append(course_count)
        teacher_course[arrange[course]['teacher_num']].append(course_count)
        course_count += 1
        x1 = [0,3]
        x2 = [0,24]
        ranges.append(x1)
        ranges.append(x2)
        precisions  = np.hstack([precisions,2,6])
        scales = np.hstack([scales,0,0])
        b.append([1, 1])
        b.append([1, 1])
        varTypes = np.hstack([varTypes,1,1])
ranges = np.array(ranges).T
b = np.array(b).T

"""==========================染色体编码设置========================="""
# 定义种群规模（个体数目）
Encoding = 'BG'
# 创建“译码矩阵”
FieldD = np.vstack([precisions , # 各决策变量编码后所占二进制位数，此时染色体长度为3+2=5
                   ranges,
                   varTypes, # 各决策变量采用什么编码方式(0为二进制编码，1为格雷编码)
                   scales, # 各决策变量是否采用对数刻度(0为采用算术刻度)
                   b,
                   varTypes])# 表示两个决策变量都是连续型变量（0为连续1为离散）

"""=========================遗传算法参数设置========================"""
Nind      = 100; # 种群个体数目
MAXGEN    = 200; # 最大遗传代数
selectStyle = 'tour' # 采用锦标赛选择
recStyle  = 'xovdp' # 采用两点交叉
mutStyle  = 'mutbin' # 采用二进制染色体的变异算子
Lind = int(np.sum(FieldD[0, :])) # 计算染色体长度
pc        = 0.7 # 交叉概率
pm        = 1/Lind # 变异概率
"""=========================开始遗传算法进化========================"""
start_time = time.time() # 开始计时
Chrom = ea.crtpc(Encoding, Nind, FieldD)
Phen = ea.bs2ri(Chrom, FieldD)
ObjV = aimfunc(Phen, teacher_course, class_course, Nind, course_count) # 计算初始种群个体的目标函数值

FitnV = ea.ranking(ObjV) # 根据目标函数大小分配适应度值
best_ind = np.argmax(FitnV) # 计算当代最优个体的序号
# 生成初始种群
for gen in range(MAXGEN):
    SelCh = Chrom[ea.selecting(selectStyle,FitnV,Nind-1),:] # 选择
    SelCh = ea.recombin(recStyle, SelCh, pc) # 重组
    SelCh = ea.mutate(mutStyle, Encoding, SelCh, pm) # 变异
    # 把父代精英个体与子代的染色体进行合并，得到新一代种群
    Chrom = np.vstack([Chrom[best_ind, :], SelCh])
    Phen = ea.bs2ri(Chrom, FieldD) # 对种群进行解码(二进制转十进制)
    ObjV = aimfunc(Phen, teacher_course, class_course, Nind, course_count) # 求种群个体的目标函数值
    FitnV = ea.ranking(ObjV) # 根据目标函数大小分配适应度值
    # 记录
    # best_ind = np.argmax(FitnV) # 计算当代最优个体的序号
    # obj_trace[gen,0] = np.sum(ObjV)/ObjV.shape[0] #记录当代种群的目标函数均值
    # obj_trace[gen,1] = ObjV[best_ind] #记录当代种群最优个体目标函数值
    # var_trace[gen,:] = Chrom[best_ind,:] #记录当代种群最优个体的染色体

"""=========================遗传算法参数设置========================"""
Nind      = 100; # 种群个体数目
MAXGEN    = 200; # 最大遗传代数
maxormins = [-1] # 列表元素为1则表示对应的目标函数是最小化，元素为-1则表示对应的目标函数是最大化
maxormins = np.array(maxormins) # 转化为Numpy array行向量
selectStyle = 'rws' # 采用轮盘赌选择
recStyle  = 'xovdp' # 采用两点交叉
mutStyle  = 'mutbin' # 采用二进制染色体的变异算子
Lind = int(np.sum(FieldD[0, :])) # 计算染色体长度
pc        = 0.7 # 交叉概率
pm        = 1/Lind # 变异概率
obj_trace = np.zeros((MAXGEN, 2)) # 定义目标函数值记录器
var_trace = np.zeros((MAXGEN, Lind)) # 染色体记录器，记录历代最优个体的染色体
"""=========================开始遗传算法进化========================"""
#开始优化进化
for gen in range(MAXGEN):
    SelCh = Chrom[ea.selecting(selectStyle,FitnV,Nind-1),:] # 选择
    SelCh = ea.recombin(recStyle, SelCh, pc) # 重组
    SelCh = ea.mutate(mutStyle, Encoding, SelCh, pm) # 变异
    # 把父代精英个体与子代的染色体进行合并，得到新一代种群
    Chrom = np.vstack([Chrom[best_ind, :], SelCh])
    Phen = ea.bs2ri(Chrom, FieldD) # 对种群进行解码(二进制转十进制)
    ObjV,CV = aimfunc1(Phen, teacher_course, class_course, Nind, course_count) # 求种群个体的目标函数值
    FitnV = ea.ranking(ObjV, CV, maxormins) # 根据目标函数大小分配适应度值
    # 记录
    best_ind = np.argmax(FitnV) # 计算当代最优个体的序号
    obj_trace[gen,0] = np.sum(ObjV)/ObjV.shape[0] #记录当代种群的目标函数均值
    obj_trace[gen,1] = ObjV[best_ind] #记录当代种群最优个体目标函数值
    var_trace[gen,:] = Chrom[best_ind,:] #记录当代种群最优个体的染色体
# 进化完成
end_time = time.time() # 结束计时
ea.trcplot(obj_trace, [['种群个体平均目标函数值', '种群最优个体目标函数值']]) # 绘制图像
"""============================输出结果============================"""
best_gen = np.argmax(obj_trace[:, [1]])
print('最优解的目标函数值：', obj_trace[best_gen, 1])
variable = ea.bs2ri(var_trace[[best_gen], :], FieldD) # 解码得到表现型（即对应的决策变量值）
print('最优解的决策变量值为：')
for i in range(variable.shape[1]):
    print('x'+str(i)+'=',variable[0, i])
print('用时：', end_time - start_time, '秒')

variable = ea.bs2ri(var_trace[[199], :], FieldD) # 解码得到表现型（即对应的决策变量值）

count = 0
result = list()




for i in range(course_num):
    for j in range(arrange[i]['weekly_course']):
        teacher = arrange[i]['teacher_num'] + 1
        course = arrange[i]['course_num'] + 1
        room = variable[0,2 * count] + 1
        time = variable[0,2 * count + 1] + 1
        print(teacher,course,room,time)
        result.append([teacher,course,room,time])
        count += 1

# wb = Workbook()
# ws = wb.active
# ws.title = "course_arrangement"
# ws.append(['course_num', 'teacher', 'course', 'time', 'room'])
# for i in range(36):
#     ws.append([i+1,result[i][0],result[i][1],int(result[i][3]),result[i][2]])
#     # print(len(result))
# wb.save('test.xlsx')
# wb=load_workbook("test.xlsx")
# sheets=wb.worksheets
# for i in range(9):
#     sheets[i+1].cell(1,1,'monday')
#     sheets[i+1].cell(1, 2, 'tuesday')
#     sheets[i+1].cell(1, 3, 'wednesday')
#     sheets[i+1].cell(1, 4, 'thurday')
#     sheets[i+1].cell(1, 5, 'friday')
# for i in range(36):
#     sheet_sub_room=result[i][2]
#     date=int((result[i][3]-1)/5)+1
#     time_section=(result[i][3]-1)%5+1
#     course_sub=int((result[i][1]-1)/3)+1
#     course_rank=result[i][1]%3
#     if(course_rank==0): course_rank=3
#
#     sheets[sheet_sub_room].cell(time_section+1,date,"课程{}的第{}类课".format(course_sub,course_rank))
#
#     sheet_sub_teacher=result[i][0]+4
#     sheets[sheet_sub_teacher].cell(time_section+1,date,"课程{}的第{}类课  教室：{}".format(course_sub,course_rank,result[i][2]))
# wb.save("test.xlsx")