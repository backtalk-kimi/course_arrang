#coding=UTF-8
import json
import os


path = ""
information = list()


def error_init(orgId):
    b = os.getcwd()
    b = os.path.join(b,str(orgId))
    if os.path.exists(b) == 0:
        os.mkdir(b)
    else:
        error = os.path.join(b,'error.txt')
        result = os.path.join(b,'result.json')
        if os.path.exists(error):  # 如果文件存在
            os.remove(error)
        if os.path.exists(result):  # 如果文件存在
            os.remove(result)
    global path
    path = b




def error_info(error_code = 300):
    # error_code = 301, 学期课时数不足以初始化subject安排
    # error_code = 000, subjectnum未设置
    result = dict()
    result["code"] = error_code
    result["msg"] = "算法生成失败，核对初始化条件"
    result = json.dumps(result, indent=3, ensure_ascii=False)
    global path
    result_path = os.path.join(path,'result.json')
    with open(result_path, 'w') as f:
        f.write(result)
        f.close()
    return result


def error_info_generate(string):
    global information
    information.append(string)

def error_info_display():
    global information
    global path
    error_path = os.path.join(path,'error.txt')
    with open(error_path, 'w') as f:
        for reason in information:
            f.write(reason)
        f.close()
    return

def write2json(result):
    global path
    result_path = os.path.join(path,'result.json')
    with open(result_path, 'w') as f:
        f.write(result)
        f.close()

def information_clean():
    global information
    information.clear()
