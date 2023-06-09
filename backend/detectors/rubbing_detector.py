from functools import reduce

import cv2
import numpy as np
import onnxruntime
from sklearn.cluster import DBSCAN


class RubbingDetector:
    def __init__(self, onnx_path):
        self.onnx_session = onnxruntime.InferenceSession(onnx_path)
        self.input_name = self._get_input_name()
        self.output_name = self._get_output_name()

    # -------------------------------------------------------
    #   获取输入输出的名字
    # -------------------------------------------------------
    def _get_input_name(self):
        input_name = []
        for node in self.onnx_session.get_inputs():
            input_name.append(node.name)
        return input_name

    def _get_output_name(self):
        output_name = []
        for node in self.onnx_session.get_outputs():
            output_name.append(node.name)
        return output_name

    # -------------------------------------------------------
    #   输入图像
    # -------------------------------------------------------
    def _get_input_feed(self, img_tensor):
        input_feed = {}
        for name in self.input_name:
            input_feed[name] = img_tensor
        return input_feed

    # -------------------------------------------------------
    #   1.cv2读取图像并resize
    #	2.图像转BGR2RGB和HWC2CHW
    #	3.图像归一化
    #	4.图像增加维度
    #	5.onnx_session 推理
    # -------------------------------------------------------
    def _inference(self, image):
        or_img = cv2.resize(image, (640, 640))
        img = or_img[:, :, ::-1].transpose(2, 0, 1)  # BGR2RGB和HWC2CHW
        img = img.astype(dtype=np.float32)
        img /= 255.0
        img = np.expand_dims(img, axis=0)
        input_feed = self._get_input_feed(img)
        pred = self.onnx_session.run(None, input_feed)[0]
        return pred, or_img

    def process(self, image, thresh):
        pred, or_img = self._inference(image)
        # left, top, right, bottom, score, class
        outbox = self._filter_box(pred, thresh, 0.5)
        outbox = self._sorted_boxes(outbox)
        outbox = np.array(outbox)
        if len(outbox) > 0:
            self._draw(or_img, outbox)

        return or_img, outbox

    def _sorted_boxes(self, boxes):
        length_side = np.average([x2 - x1 for x1, y1, x2, y2, _, _ in boxes])
        sorted_y = sorted(boxes, key=lambda x: x[1])
        groups = []
        while len(sorted_y) > 0:
            group = []
            group.append(sorted_y[0])
            sorted_y.pop(0)
            i = 0
            while i < len(sorted_y):
                center_now = (sorted_y[i][0] + sorted_y[i][2]) / 2
                center_last = (group[-1][0] + group[-1][2]) / 2
                if abs(center_now - center_last) < length_side:
                    group.append(sorted_y[i])
                    sorted_y.pop(i)
                else:
                    i += 1
            groups.append(group)
        sorted_boxes = []

        def _get_center(x):
            center = 0
            for i in x:
                center += i[0] + i[2]
            return center / len(x) / 2

        groups = sorted(groups, key=lambda x: _get_center(x), reverse=True)
        for group in groups:
            sorted_boxes.extend(group)
        return sorted_boxes

    # dets:  array [x,6] 6个值分别为x1,y1,x2,y2,score,class
    # thresh: 阈值
    def _nms(self, dets, thresh):
        x1 = dets[:, 0]
        y1 = dets[:, 1]
        x2 = dets[:, 2]
        y2 = dets[:, 3]
        # -------------------------------------------------------
        #   计算框的面积
        #	置信度从大到小排序
        # -------------------------------------------------------
        areas = (y2 - y1 + 1) * (x2 - x1 + 1)
        scores = dets[:, 4]
        keep = []
        index = scores.argsort()[::-1]

        while index.size > 0:
            i = index[0]
            keep.append(i)
            # -------------------------------------------------------
            #   计算相交面积
            #	1.相交
            #	2.不相交
            # -------------------------------------------------------
            x11 = np.maximum(x1[i], x1[index[1:]])
            y11 = np.maximum(y1[i], y1[index[1:]])
            x22 = np.minimum(x2[i], x2[index[1:]])
            y22 = np.minimum(y2[i], y2[index[1:]])

            w = np.maximum(0, x22 - x11 + 1)
            h = np.maximum(0, y22 - y11 + 1)

            overlaps = w * h
            # -------------------------------------------------------
            #   计算该框与其它框的IOU，去除掉重复的框，即IOU值大的框
            #	IOU小于thresh的框保留下来
            # -------------------------------------------------------
            ious = overlaps / (areas[i] + areas[index[1:]] - overlaps)
            idx = np.where(ious <= thresh)[0]
            index = index[idx + 1]
        return keep

    def _xywh2xyxy(self, x):
        # [x, y, w, h] to [x1, y1, x2, y2]
        y = np.copy(x)
        y[:, 0] = x[:, 0] - x[:, 2] / 2
        y[:, 1] = x[:, 1] - x[:, 3] / 2
        y[:, 2] = x[:, 0] + x[:, 2] / 2
        y[:, 3] = x[:, 1] + x[:, 3] / 2
        return y

    def _filter_box(self, org_box, conf_thres, iou_thres):  # 过滤掉无用的框
        # -------------------------------------------------------
        #   删除为1的维度
        #	删除置信度小于conf_thres的BOX
        # -------------------------------------------------------
        org_box = np.squeeze(org_box)
        conf = org_box[..., 4] > conf_thres
        box = org_box[conf == True]
        # -------------------------------------------------------
        #	通过argmax获取置信度最大的类别
        # -------------------------------------------------------
        cls_cinf = box[..., 5:]
        cls = []
        for i in range(len(cls_cinf)):
            cls.append(int(np.argmax(cls_cinf[i])))
        all_cls = list(set(cls))
        # -------------------------------------------------------
        #   分别对每个类别进行过滤
        #	1.将第6列元素替换为类别下标
        #	2.xywh2xyxy 坐标转换
        #	3.经过非极大抑制后输出的BOX下标
        #	4.利用下标取出非极大抑制后的BOX
        # -------------------------------------------------------
        output = []

        for i in range(len(all_cls)):
            curr_cls = all_cls[i]
            curr_cls_box = []
            curr_out_box = []
            for j in range(len(cls)):
                if cls[j] == curr_cls:
                    box[j][5] = curr_cls
                    curr_cls_box.append(box[j][:6])
            curr_cls_box = np.array(curr_cls_box)
            # curr_cls_box_old = np.copy(curr_cls_box)
            curr_cls_box = self._xywh2xyxy(curr_cls_box)
            curr_out_box = self._nms(curr_cls_box, iou_thres)
            for k in curr_out_box:
                output.append(curr_cls_box[k])
        output = np.array(output)
        return output

    def _draw(self, image, box_data):
        boxes = box_data[..., :4].astype(np.int32)

        for box in boxes:
            left, top, right, bottom = box
            cv2.rectangle(image, (left, top), (right, bottom), (255, 0, 0), 2)


if __name__ == "__main__":
    onnx_path = '../models/best_rubbing.onnx'
    model = RubbingDetector(onnx_path)
    image = cv2.imread('../../rubbing.png')
    image, outbox = model.process(image, 0.5)
    cv2.imwrite('res.jpg', image)
    print(outbox)
