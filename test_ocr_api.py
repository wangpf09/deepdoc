#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OCR API测试脚本
用于测试根目录下的OCR API服务的功能正确性
"""

import os
import sys
import json
import requests
from PIL import Image
import time

# 测试配置
API_URL = "http://localhost:8080/ocr"
TEST_IMAGE = "./temp/pdcc-2/PDCC第二个里程碑技术出版物立项计划书.pdf_1.jpg"  # 使用项目中已有的图像文件作为测试


def test_ocr_api():
    """测试OCR API的功能"""
    print("开始测试OCR API...")
    
    # 检查测试文件是否存在
    if not os.path.exists(TEST_IMAGE):
        print(f"错误: 测试文件 {TEST_IMAGE} 不存在")
        print("请修改测试文件路径或提供一个有效的测试图像文件")
        return False
    
    # 准备上传文件
    try:
        files = {
            'file': (os.path.basename(TEST_IMAGE), open(TEST_IMAGE, 'rb'))
        }
    except Exception as e:
        print(f"错误: 无法打开测试文件 - {e}")
        return False
    
    # 发送请求
    try:
        print(f"发送请求到 {API_URL}...")
        response = requests.post(API_URL, files=files)
        
        # 检查响应状态码
        if response.status_code != 200:
            print(f"错误: API返回状态码 {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
        # 解析响应内容
        result = response.json()
        print("API响应:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 验证响应格式
        if 'status' not in result or result['status'] != 'success':
            print("错误: API响应格式不正确或状态不是success")
            return False
        
        if 'result' not in result or not isinstance(result['result'], list):
            print("错误: API响应中缺少result字段或格式不正确")
            return False
        
        print("测试成功! OCR API工作正常")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"错误: 无法连接到API服务 {API_URL}")
        print("请确保OCR API服务已启动并在指定端口运行")
        return False
    except Exception as e:
        print(f"错误: 测试过程中发生异常 - {e}")
        return False
    finally:
        # 关闭文件
        files['file'][1].close()


if __name__ == "__main__":
    print("OCR API测试工具")
    print("=================")
    
    # 等待API服务启动
    print("等待API服务启动...")
    time.sleep(2)
    
    # 运行测试
    success = test_ocr_api()
    
    # 输出结果
    if success:
        print("\n✅ 测试通过: OCR API服务工作正常")
        sys.exit(0)
    else:
        print("\n❌ 测试失败: OCR API服务存在问题")
        sys.exit(1)