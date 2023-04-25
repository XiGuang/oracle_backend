import pickle

import numpy as np
import onnxruntime
from PIL import Image


class OracleDetector:
    def __init__(self, onnx_path, dict_path):
        self.onnx_session = onnxruntime.InferenceSession(onnx_path)
        self.input_name = self.onnx_session.get_inputs()[0].name
        self.output_name = self.onnx_session.get_outputs()[0].name
        with open(dict_path, 'rb') as f:
            self.oracle_dict = pickle.load(f)

    def predictTopN(self, image, n):
        img = image.resize((224, 224))
        # 将灰度图转化为RGB模式
        img = img.convert("RGB")
        # 归一化
        img1 = np.array(img) / 255.
        # 将图片增加一个维度，目的是匹配网络模型
        img1 = (np.expand_dims(img1, 0))
        img1 = img1.astype(np.float32)
        output = self.onnx_session.run([self.output_name], {self.input_name: img1})
        prob = np.squeeze(output[0])
        topN = np.argsort(prob)[::-1][:n]
        return [(self.oracle_dict[i], prob[i]) for i in topN]


if __name__ == "__main__":
    oracle_detector = OracleDetector("../models/oracle.onnx", "oracle_dict.pkl")
    img = Image.open('../../60BB6_0.png')
    print(oracle_detector.predictTopN(img, 5))
