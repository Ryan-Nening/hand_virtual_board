import cv2
from ursina import Ursina, Button, scene, color, destroy, mouse
from ursina.prefabs.first_person_controller import FirstPersonController
import mediapipe
import math

application_engine = Ursina()

video_capture = cv2.VideoCapture(0)
mediapipe_hands = mediapipe.solutions.hands
hand_tracker = mediapipe_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
previous_pinch_state = False

class VoxelBlock(Button):

    def __init__(self, position=(0, 0, 0)):
        super().__init__(parent=scene, position=position, model='cube', origin_y=0.5, texture='white_cube', color=color.color(0, 0, 1))

    def input(self, key_press):
        if self.hovered:
            if key_press == 'left mouse down':
                new_voxel_position = self.position + mouse.normal
                voxel_block = VoxelBlock(position=new_voxel_position)

            if key_press == 'right mouse down':
                destroy(self)
                
application_engine.run()
