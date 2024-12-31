import mediapipe as mp

class PoseModel:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()

    def process_frame(self, frame):
        # Procesa el cuadro para detectar poses
        results = self.pose.process(frame)
        return results.pose_landmarks if results.pose_landmarks else None