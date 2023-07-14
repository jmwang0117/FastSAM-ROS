#!/usr/bin/env python3
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

def capture_image_publish():
    rospy.init_node('capture_image_publish')
    bridge = CvBridge()
    image_pub = rospy.Publisher('/rgb_image', Image, queue_size=10)
    rate = rospy.Rate(10)  # 设置发布频率为10Hz

    cap = cv2.VideoCapture(0)  # 打开摄像头，0表示默认摄像头

    while not rospy.is_shutdown():
        ret, frame = cap.read()  # 读取摄像头图像

        if ret:
            # 将图像转换为ROS图像消息并发布
            img_msg = bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            image_pub.publish(img_msg)

        rate.sleep()

    cap.release()  # 释放摄像头
    cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        capture_image_publish()
    except rospy.ROSInterruptException:
        pass





# import rospy
# import cv2
# import glob
# from sensor_msgs.msg import Image
# from cv_bridge import CvBridge

# def capture_image_publish():
#     rospy.init_node('capture_image_publish')
#     bridge = CvBridge()
#     image_pub = rospy.Publisher('/rgb_image', Image, queue_size=10)
#     rate = rospy.Rate(10)  # 设置发布频率为10Hz

#     image_files = sorted(glob.glob('/home/jmwang/datasets/20230705_132611/rgb_*.jpg'))  # 获取按顺序排序的图片文件列表

#     for image_file in image_files:
#         frame = cv2.imread(image_file)  # 读取图片帧

#         # 将图像转换为ROS图像消息并发布
#         img_msg = bridge.cv2_to_imgmsg(frame, encoding='bgr8')
#         image_pub.publish(img_msg)

#         rate.sleep()

#     cv2.destroyAllWindows()

# if __name__ == '__main__':
#     try:
#         capture_image_publish()
#     except rospy.ROSInterruptException:
#         pass
