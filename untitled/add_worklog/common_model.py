# 发送post请求无重试机制
import json
import requests


def send_post_request(url, data, token): 

    headers = {  
    'Authorization':  token ,  
    'content-type': 'application/json;charset=UTF-8' # 设置请求头的内容类型为JSON
    }
    # 发送POST请求  
    response = requests.post(url, headers=headers,json=data)  
      
    # 检查请求是否成功  
    if response.status_code == 200:  
        # 返回的内容可能是JSON格式，所以尝试解析  
        try:  
            # return response.json()  
            return response.text
        except json.JSONDecodeError:  
            print("返回的内容不是有效的JSON格式")  
            return response.text  
    else:  
        print(f"请求失败，状态码：{response.status_code}")  
        print(response.text)  # 打印返回的内容，便于调试  
        return None 