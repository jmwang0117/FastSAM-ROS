#!/usr/bin/env python3
import ast
import torch
import rospy

from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from fastsam import FastSAM, FastSAMPrompt


class FastSAMNode:
    def __init__(self):
        rospy.init_node('fastsam_node')
        self.bridge = CvBridge()

        # Load model
        model_path = "/home/jmwang/ROS4FastSAM/src/fastsam_ros/models/FastSAM-x.pt"
        self.imgsz = 1024

        self.iou = 0.9
        self.conf = 0.4
        self.output = "./output/"
        self.randomcolor = True
        self.point_prompt = [[0, 0]]
        self.point_label = [0]
        self.box_prompt = [[0, 0, 0, 0]]
        self.better_quality = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.retina = True
        self.withContours = False

        self.model = FastSAM(model_path)
        self.model.point_prompt = self.point_prompt
        self.model.box_prompt = self.convert_box_xywh_to_xyxy(self.box_prompt)
        self.model.point_label = self.point_label

        # Create publisher for result
        self.result_pub = rospy.Publisher('/result', Image, queue_size=10)

        # Subscribe to RGB image topic
        rospy.Subscriber('/rgb_image', Image, self.image_callback)
    
    def convert_box_xywh_to_xyxy(self, box):
        x1 = box[0][0]
        y1 = box[0][1]
        x2 = box[0][0] + box[0][2]
        y2 = box[0][1] + box[0][3]
        return [[x1, y1, x2, y2]]

    def image_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
        self.process_image(cv_image)

    def process_image(self, image):
        everything_results = self.model(
            image,
            device=self.device,
            retina_masks=self.retina,
            imgsz=self.imgsz,
            conf=self.conf,
            iou=self.iou
        )

        bboxes = None
        points = None
        point_label = None
        prompt_process = FastSAMPrompt(image, everything_results, device=self.device)
        if self.box_prompt[0][2] != 0 and self.box_prompt[0][3] != 0:
            ann = prompt_process.box_prompt(bboxes=self.box_prompt)
            bboxes = self.box_prompt
        # elif text_prompt is not None:
        #     ann = prompt_process.text_prompt(text=text_prompt)
        elif self.point_prompt[0] != [0, 0]:
            ann = prompt_process.point_prompt(
                points=self.point_prompt, pointlabel=self.point_label
            )
            points = self.point_prompt
            point_label = self.point_label
        else:
            ann = prompt_process.everything_prompt()
        result_image = prompt_process.plot(
            annotations=ann,
            output=self.output,
            bboxes=bboxes,
            points=points,
            point_label=point_label,
            withContours=self.withContours,
            better_quality=self.better_quality,
        )
        self.publish_result(result_image)

    def publish_result(self, image):
        
        msg = self.bridge.cv2_to_imgmsg(image, encoding='rgb8')
        self.result_pub.publish(msg)

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    node = FastSAMNode()
    node.run()
