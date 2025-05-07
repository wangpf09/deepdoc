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
import tempfile

import trio

import utils.file_utils

# 检查必要的依赖是否已安装
try:
    import numpy as np
    from flask import Flask, request, jsonify
    from werkzeug.utils import secure_filename
    from PIL import Image
except ImportError as e:
    print(f"错误: 缺少必要的依赖 - {e}")
    print("请安装所需依赖: pip3 install flask werkzeug pillow numpy")
    print("或者安装项目所有依赖: pip3 install -r requirements.txt")
    sys.exit(1)

# 不需要修改系统路径，因为文件已经在根目录
# 直接导入相关模块
from vision.seeit import draw_box
from vision import OCR, init_in_out

app = Flask(__name__)

# 配置上传文件的保存目录
UPLOAD_FOLDER = os.path.join(
    utils.file_utils.get_project_base_directory(),
    "temp"
)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# 初始化OCR引擎
ocr = OCR()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_params():
    # 检查是否有文件上传
    if 'file' not in request.files:
        return '没有上传文件', 400

    file = request.files['file']

    # 检查文件名是否为空
    if file.filename == '':
        return '未选择文件', 400

    # 检查文件类型是否允许
    if not allowed_file(file.filename):
        return f'不支持的文件类型，允许的类型: {ALLOWED_EXTENSIONS}', 400
    return None, None


def build_in_out():
    file = request.files['file']

    # 保存上传的文件
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # 创建输出目录
    output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'output', filename)
    os.makedirs(output_dir, exist_ok=True)

    # 准备OCR处理参数
    class Args:
        def __init__(self):
            self.inputs = file_path
            self.output_dir = output_dir

    args = Args()
    return args


def recognize(args, images, outputs):
    import torch.cuda

    cuda_devices = torch.cuda.device_count()
    limiter = [trio.CapacityLimiter(1) for _ in range(cuda_devices)] if cuda_devices > 1 else None
    ocr = OCR()

    results = []

    def __ocr(i, id, img):
        bxs = ocr(np.array(img), id)
        bxs = [(line[0], line[1][0]) for line in bxs]
        bxs = [{
            "text": t,
            "bbox": [b[0][0], b[0][1], b[1][0], b[-1][1]],
            "type": "ocr",
            "score": 1} for b, t in bxs if b[0][0] <= b[1][0] and b[0][1] <= b[-1][1]]
        img = draw_box(images[i], bxs, ["ocr"], 1.)
        img.save(outputs[i], quality=95)

        with open(outputs[i] + ".txt", "w+", encoding='utf-8') as f:
            f.write("\n".join([o["text"] for o in bxs]))
            f.seek(0)
            page_content = f.read()

        page_result = {
            "page": i + 1,
            "page_content": page_content,
        }

        results.append(page_result)
        print(f"OCR Task {args.inputs} {i} done, image with box has been save to {outputs[i]}")

    async def __ocr_thread(i, id, img, limiter=None):
        if limiter:
            async with limiter:
                print("Task {} use device {}".format(i, id))
                await trio.to_thread.run_sync(lambda: __ocr(i, id, img))
        else:
            __ocr(i, id, img)

    async def __ocr_launcher():
        if cuda_devices > 1:
            async with trio.open_nursery() as nursery:
                for i, img in enumerate(images):
                    nursery.start_soon(__ocr_thread, i, i % cuda_devices, img, limiter[i % cuda_devices])
                    await trio.sleep(0.1)
        else:
            for i, img in enumerate(images):
                await __ocr_thread(i, 0, img)

    trio.run(__ocr_launcher)
    return results


@app.route('/ocr', methods=['POST'])
def ocr_api():
    msg, code = check_params()
    if msg is not None or code is not None:
        return jsonify({
            "status": "error",
            "message": msg
        })

    args = build_in_out()
    # 初始化输入输出
    images, outputs = init_in_out(args)
    result = recognize(args, images, outputs)
    return jsonify({
        "status": "success",
        "message": "OCR处理完成",
        "result": result
    })


if __name__ == "__main__":
    # 设置环境变量
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # 使用单个GPU

    # 启动Flask应用
    print(f"启动OCR API服务，临时文件目录: {UPLOAD_FOLDER}")
    app.run(host='0.0.0.0', port=8080, debug=True)
