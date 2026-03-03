import cv2
from ursina import Ursina, Button, scene, color, destroy, mouse, Text, Entity, Sky
from ursina.prefabs.first_person_controller import FirstPersonController
import mediapipe as mp
import math

# 1. Initialize the Engine
app = Ursina()
video_capture = cv2.VideoCapture(0)

# 2. Technical Hand Tracking Setup
mp_hands = mp.solutions.hands
hand_tracker = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

# 3. Global State Variables (snake_case)
previous_pinch_state = False
position_history = []  
deletion_mode = False

# 4. Technical UI & Visual Feedback
status_text = Text(text="Hand: Searching...", position=(-0.85, 0.45), color=color.yellow)
ghost_voxel = Entity(model='cube', color=color.rgba(0, 1, 1, 0.3), scale=1) 

# 5. The Voxel Blueprint (Class)
class VoxelBlock(Button):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture='white_cube',
            color=color.white,
            highlight_color=color.cyan
        )

# 6. Core Logic Loop
def update():
    global deletion_mode, previous_pinch_state, position_history
    
    # Calculate count at start so HUD always has the data
    voxel_count = len([e for e in scene.entities if isinstance(e, VoxelBlock)])
    
    # Keyboard Toggles
    from ursina import held_keys
    if held_keys['x']: deletion_mode = True   
    if held_keys['b']: deletion_mode = False  
    if held_keys['c']:
        for e in [v for v in scene.entities if isinstance(v, VoxelBlock)]:
            destroy(e)   

    success, image = video_capture.read()
    if not success: 
        status_text.text = "Hand: Camera Error"
        return

    image = cv2.flip(image, 1)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hand_tracker.process(rgb_image)

    if results.multi_hand_landmarks:
        status_text.color = color.green
        for hand_landmarks in results.multi_hand_landmarks:
            itip = hand_landmarks.landmark[8] 
            ttip = hand_landmarks.landmark[4]

            # Smoothing logic
            position_history.append((itip.x, itip.y))
            if len(position_history) > 5:
                position_history.pop(0)
            
            avg_x = sum(p[0] for p in position_history) / len(position_history)
            avg_y = sum(p[1] for p in position_history) / len(position_history)
            mouse.position = (avg_x - 0.5, (1 - avg_y) - 0.5)

            if mouse.hovered_entity:
                ghost_voxel.enabled = True
                ghost_voxel.position = mouse.hovered_entity.position + mouse.normal
            else:
                ghost_voxel.enabled = False

            # FIXED LINE 85: The parenthesis is now closed
            dist = math.sqrt((itip.x - ttip.x)**2 + (itip.y - ttip.y)**2)
            is_pinching = dist < 0.05

            if is_pinching and not previous_pinch_state:
                if mouse.hovered_entity:
                    if not deletion_mode:
                        VoxelBlock(position=mouse.hovered_entity.position + mouse.normal)
                    else:
                        if isinstance(mouse.hovered_entity, VoxelBlock):
                            destroy(mouse.hovered_entity)
            
            previous_pinch_state = is_pinching
    else:
        status_text.color = color.red
        ghost_voxel.enabled = False

    # HUD Update
    mode_text = "DELETING" if deletion_mode else "BUILDING"
    status_text.text = f"Hand: {'ACTIVE' if results.multi_hand_landmarks else 'SEARCHING'} | MODE: {mode_text} | Voxels: {voxel_count}"

    cv2.imshow("Hand Tracker Monitor", image)

# 7. Initial Floor
for z in range(15):
    for x in range(15):
        VoxelBlock(position=(x, 0, z))

# 8. World Setup
player = FirstPersonController(position=(8, 10, -10))
Sky() 
app.run()