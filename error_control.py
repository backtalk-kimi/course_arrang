#coding=UTF-8
import json
import os
import sys


path = ""
information = list()

def input_init():
    # orgId = sys.argv[1]
    orgId = "2"
    b = os.getcwd()
    b = os.path.join(b, orgId)
    global path
    path = b

    input_file = os.path.join(b, 'input.json')
    if not os.path.exists(input_file):
        if not os.path.exists(b):
            os.mkdir(b)
        result = dict()
        result["code"] = 0
        result["msg"] = "缺少输入信息"
        result = json.dumps(result, indent=3, ensure_ascii=False)
        error_info_display()
        result_path = os.path.join(b, 'result.json')
        with open(result_path, 'w') as f:
            f.write(result)
            f.close()
        exit()
    else:
        with open(input_file, 'r', encoding='gb2312') as f:
            content = json.load(f)
        error_init(b)
    return content


# def error_init(b):
#     error = os.path.join(b,'error.txt')
#     result = os.path.join(b,'result.json')
#     if os.path.exists(error):  # 如果文件存在
#         os.remove(error)
#     if os.path.exists(result):  # 如果文件存在
#         os.remove(result)
#     global path
#     path = b
#
#
#
# def error_info_generate(string):
#     global information
#     information.append(string)
#
# def error_info_display():
#     global information
#     global path
#     error_path = os.path.join(path,'error.txt')
#     # if not os.path.exists(error_path):
#
#     with open(error_path, 'w') as f:
#         for reason in information:
#             f.write(reason)
#         f.close()
#     return
#
# def write2json(result):
#     global path
#     result_path = os.path.join(path,'result.json')
#     with open(result_path, 'w') as f:
#         f.write(result)
#         f.close()
#
# def error_info(error_code = 300):
#     # error_code = 301, 学期课时数不足以初始化subject安排
#     # error_code = 000, subjectnum未设置
#     result = dict()
#     result["code"] = error_code
#     result["msg"] = "算法生成失败，核对初始化条件"
#     result = json.dumps(result, indent=3, ensure_ascii=False)
#     error_info_display()
#     global path
#     result_path = os.path.join(path,'result.json')
#     with open(result_path, 'w') as f:
#         f.write(result)
#         f.close()
#     return result
#
# def information_clean():
#     global information
#     information.clear()

def error_init(b):
    error = os.path.join(b,'error.txt')
    result = os.path.join(b,'result.json')
    Running = os.path.join(b,'information.txt')
    arrange = os.path.join(b,'arrange')
    if os.path.exists(error):  # 如果文件存在
        os.remove(error)
    if os.path.exists(result):  # 如果文件存在
        os.remove(result)
    if os.path.exists(Running):  # 如果文件存在
        os.remove(Running)
    if os.path.exists(arrange):  # 如果文件存在
        arrange_list = os.listdir(arrange)
        for i in arrange_list:
            a_path = os.path.join(arrange, i)
            os.remove(a_path)
    global path
    path = b

def arrange_info_display(info, num):
    global path
    arrange_path = os.path.join(path, 'arrange')
    if not os.path.exists(arrange_path):
        os.mkdir(arrange_path)
    arrange = 'arrange' + str(num) + '.json'
    arrange_path = os.path.join(arrange_path, arrange)
    write2json(info, arrange_path)
    return

def error_info_generate(string):
    global information
    information.append(string)

def error_info_display():
    global information
    global path
    error_path = os.path.join(path,'error.txt')
    # if not os.path.exists(error_path):

    with open(error_path, 'w') as f:
        for reason in information:
            f.write(reason)
        f.close()
    return

def write2json(result, fileName):
    result = json.dumps(result, indent=3, ensure_ascii=False)
    global path
    result_path = os.path.join(path, fileName)
    with open(result_path, 'w') as f:
        f.write(result)
        f.close()

def error_info(error_code = 300):
    # error_code = 301, 学期课时数不足以初始化subject安排
    # error_code = 000, subjectnum未设置
    result = dict()
    result["code"] = error_code
    result["msg"] = "算法生成失败，核对初始化条件"
    result = json.dumps(result, indent=3, ensure_ascii=False)
    error_info_display()
    global path
    result_path = os.path.join(path,'result.json')
    with open(result_path, 'w') as f:
        f.write(result)
        f.close()
    return result

def information_clean():
    global information
    information.clear()

def running_information(RuningInformation):
    RunningFile = os.path.join(path, 'information.txt')
    with open(RunningFile, 'a') as f:
        f.write(RuningInformation)
        f.close()
    return