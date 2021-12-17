#coding=UTF-8
import json
# error_code = 301, 学期课时数不足以初始化subject安排
# error_code = 000, subjectnum未设置
def error_info(error_code = 300):
    result = dict()
    result["code"] = error_code
    result["msg"] = "算法生成失败，核对初始化条件"
    result = json.dumps(result, indent=3, ensure_ascii=False)
    with open('result.json', 'w') as f:
        f.write(result)
        f.close()
    return result

information = list()

def error_info_generate(string):
    global information
    information.append(string)

def error_info_display():
    global information
    with open('error.txt', 'w') as f:
        for reason in information:
            f.write(reason)
        f.close()
    return