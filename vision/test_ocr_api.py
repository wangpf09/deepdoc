#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import os
import sys
import json
import requests
import argparse


def test_ocr_api(file_path, api_url="http://localhost:5000/ocr"):
    """
    测试OCR API功能
    
    Args:
        file_path: 要进行OCR处理的文件路径
        api_url: OCR API的URL地址
    
    Returns:
        None
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        return
    
    # 检查文件类型
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in [".pdf", ".png", ".jpg", ".jpeg"]:
        print(f"错误: 不支持的文件类型 {file_ext}，支持的类型: .pdf, .png, .jpg, .jpeg")
        return
    
    print(f"正在发送文件 {file_path} 到 OCR API...")
    
    # 准备文件上传
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f)}
        
        try:
            # 发送POST请求到OCR API
            response = requests.post(api_url, files=files)
            
            # 检查响应状态
            if response.status_code == 200:
                result = response.json()
                print("OCR处理成功!")
                print(f"状态: {result['status']}")
                print(f"消息: {result['message']}")
                print(f"处理页数: {len(result['result'])}")
                
                # 打印每页的OCR结果摘要
                for page in result['result']:
                    page_num = page['page']
                    ocr_count = len(page['ocr_results'])
                    print(f"第 {page_num} 页: 识别到 {ocr_count} 个文本区域")
                    
                    # 打印前5个OCR结果作为示例
                    for i, ocr_item in enumerate(page['ocr_results'][:5]):
                        print(f"  - 文本 {i+1}: {ocr_item['text']}")
                    
                    if ocr_count > 5:
                        print(f"  ... 还有 {ocr_count - 5} 个文本区域")
            else:
                print(f"错误: API返回状态码 {response.status_code}")
                print(response.text)
        
        except requests.exceptions.ConnectionError:
            print(f"错误: 无法连接到API服务器 {api_url}")
            print("请确保OCR API服务已启动")
        except Exception as e:
            print(f"错误: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="测试OCR API功能")
    parser.add_argument('--file', help="要进行OCR处理的文件路径", required=True)
    parser.add_argument('--api_url', help="OCR API的URL地址", default="http://localhost:5000/ocr")
    
    args = parser.parse_args()
    test_ocr_api(args.file, args.api_url)
    
    print("\n使用说明:")
    print("1. 首先启动OCR API服务: python vision/ocr_api.py")
    print("2. 然后运行此测试脚本: python vision/test_ocr_api.py --file=<文件路径>")