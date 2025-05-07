# OCR API 服务使用说明

## 简介

本服务将DeepDoc的OCR功能封装为REST API，使其可以通过HTTP请求进行调用。服务基于Flask框架实现，支持处理PDF文件和图片文件（PNG、JPG、JPEG），并返回OCR识别结果。

## 安装依赖

确保已安装所需的Python依赖包：

```bash
pip3 install flask werkzeug pillow requests numpy
```

如果您使用的是项目的虚拟环境，请确保在虚拟环境中安装这些依赖：

```bash
# 激活虚拟环境（如果有）
source .venv/bin/activate

# 安装依赖
pip install flask werkzeug pillow requests numpy
```

注意：OCR服务依赖于项目中的其他模块，请确保您已经安装了项目的所有依赖：

```bash
pip3 install -r requirements.txt
```

## 启动服务

执行以下命令启动OCR API服务：

```bash
python vision/ocr_api.py
```

服务默认在`0.0.0.0:5000`上运行，可以通过修改`ocr_api.py`文件中的相关参数来更改主机和端口。

## API 接口说明

### OCR识别接口

- **URL**: `/ocr`
- **方法**: POST
- **参数**: 
  - `file`: 要进行OCR识别的文件（支持PDF、PNG、JPG、JPEG格式）
- **返回格式**: JSON

### 返回结果示例

```json
{
  "status": "success",
  "message": "OCR处理完成",
  "result": [
    {
      "page": 1,
      "ocr_results": [
        {
          "text": "识别出的文本内容",
          "bbox": [x0, y0, x1, y1],
          "type": "ocr",
          "score": 1
        },
        ...
      ],
      "image_path": "处理后的图像文件名",
      "text_path": "文本结果文件名"
    },
    ...
  ]
}
```

## 测试API

提供了测试脚本`test_ocr_api.py`用于验证API功能：

```bash
python vision/test_ocr_api.py --file=./temp/PDCC第二个里程碑技术出版物立项计划书.pdf
```

可选参数：
- `--api_url`: 指定API地址，默认为`http://localhost:5000/ocr`

## 使用示例

### Python示例

```python
import requests

# OCR API地址
api_url = "http://localhost:5000/ocr"

# 要处理的文件
file_path = "./temp/PDCC第二个里程碑技术出版物立项计划书.pdf"

# 发送请求
with open(file_path, "rb") as f:
    files = {"file": (os.path.basename(file_path), f)}
    response = requests.post(api_url, files=files)

# 处理结果
if response.status_code == 200:
    result = response.json()
    print(f"OCR处理成功: {result['message']}")
    # 处理OCR结果
    for page in result['result']:
        print(f"第 {page['page']} 页识别到 {len(page['ocr_results'])} 个文本区域")
else:
    print(f"请求失败: {response.text}")
```

### cURL示例

```bash
curl -X POST -F "file=@./temp/PDCC第二个里程碑技术出版物立项计划书.pdf" http://localhost:5000/ocr
```

## 注意事项

1. 服务默认使用GPU进行OCR处理，确保系统已正确配置CUDA环境
2. 对于大型PDF文件，处理可能需要较长时间
3. 临时文件存储在系统临时目录中，重启服务后会清除