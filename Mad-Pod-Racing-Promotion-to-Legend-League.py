import sys
import math
import numpy as np

# Game parameters
laps = int(input())  # Total laps in race
checkpoint_count = int(input())  # Number of checkpoints
checkpoints = []  # List to store all checkpoint coordinates
for i in range(checkpoint_count):
    checkpoint_x, checkpoint_y = [int(j) for j in input().split()]
    checkpoints.append((checkpoint_x, checkpoint_y))


class Pod:
    """Represents a racing pod with position, velocity and state"""

    def __init__(self, x, y, vx, vy, angle, next_check_point_id):
        # Position and movement
        self.x = x
        self.y = y
        self.vx = vx  # X velocity
        self.vy = vy  # Y velocity
        self.angle = angle  # Current facing angle

        # Race progress
        self.next_check_point_id = next_check_point_id
        self.target_x = 0  # Current target x
        self.target_y = 0  # Current target y

        # Ability status
        self.has_boost = True  # Whether boost is available
        self.has_shield = True  # Whether shield is available

    def update(self, x, y, vx, vy, angle, next_check_point_id):
        """Update dynamic pod state each turn"""
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.angle = angle
        self.next_check_point_id = next_check_point_id

    def calculate_angle_diff(self, x, y, a):
        """Calculate angle difference between current and target direction"""
        dx = x - self.x
        dy = y - self.y
        target_angle = math.degrees(math.atan2(dy, dx))
        angle_diff = (target_angle - a) % 360
        if angle_diff > 180:
            angle_diff -= 360
        return angle_diff

    def calculate_angle_diff_v(self):
        """Calculate velocity vector angle"""
        dx = self.vx
        dy = self.vy
        target_angle = math.degrees(math.atan2(dy, dx))
        angle_diff_v = target_angle % 360
        if angle_diff_v > 180:
            angle_diff_v -= 360
        return angle_diff_v

    def set_next_check_point_id(self):
        """Determine if should advance to next checkpoint"""
        checkpoint_x, checkpoint_y = checkpoints[self.next_check_point_id]
        # Target position with velocity compensation
        target_x = checkpoint_x - self.vx * 4
        target_y = checkpoint_y - self.vy * 4

        angle_diff_v = self.calculate_angle_diff_v()
        af = self.calculate_angle_diff(target_x, target_y, angle_diff_v)

        # Dynamic distance threshold based on angle difference
        threshold_multiplier = (1 if abs(af) < 150 else
                                1.2 if abs(af) < 160 else
                                1.5 if abs(af) < 170 else 1.9)

        if abs(self.x - target_x) + abs(self.y - target_y) < 800 * threshold_multiplier:
            # Advance to next checkpoint (with loop back)
            if self.next_check_point_id < len(checkpoints) - 1:
                self.next_check_point_id += 1
            else:
                self.next_check_point_id = 0
            return True
        return False

    def set_target(self):
        """Set target coordinates with velocity prediction"""
        checkpoint_x, checkpoint_y = checkpoints[self.next_check_point_id]
        self.target_x = checkpoint_x - self.vx * 4
        self.target_y = checkpoint_y - self.vy * 4
        return self.target_x, self.target_y

    def predict_position(self, step):
        """Predict future position based on current velocity"""
        return self.x + int(1.2 * self.vx * step), self.y + int(1.2 * self.vy * step)

    def calculate_thrust(self):
        """Calculate thrust amount based on angle to target"""
        angle_diff = self.calculate_angle_diff(self.target_x, self.target_y, self.angle)
        if abs(angle_diff) > 90:
            return 100 - int(10 ** (abs(angle_diff) / 90))
        return 100

    def use_boost(self):
        """Activate boost ability"""
        self.has_boost = False
        return 'BOOST'

    def use_shield(self):
        """Activate shield ability"""
        self.has_shield = False
        return 'SHIELD'


# Initialize pods from game input
my_pod1 = Pod(*[int(j) for j in input().split()])
my_pod2 = Pod(*[int(j) for j in input().split()])
opp_pod1 = Pod(*[int(j) for j in input().split()])
opp_pod2 = Pod(*[int(j) for j in input().split()])

# Initial move (dummy values)
print(checkpoints[1][0], checkpoints[1][1], 100)
print(checkpoints[1][0], checkpoints[1][1], 100)

# Main game loop
while True:
    # Update all pods
    my_pod1.update(*[int(j) for j in input().split()])
    my_pod2.update(*[int(j) for j in input().split()])
    opp_pod1.update(*[int(j) for j in input().split()])
    opp_pod2.update(*[int(j) for j in input().split()])

    # Update checkpoints if needed
    my_pod1.set_next_check_point_id()
    my_pod2.set_next_check_point_id()

    # Set targets
    my_pod1.set_target()
    my_pod2.set_target()

    # Calculate thrust
    thrust1 = my_pod1.calculate_thrust()
    thrust2 = my_pod2.calculate_thrust()

    # Use boost if available and optimal
    if my_pod1.has_boost and thrust1 == 100:
        thrust1 = my_pod1.use_boost()
    if my_pod2.has_boost and thrust2 == 100:
        thrust2 = my_pod2.use_boost()

    # Predict positions for collision detection
    x1, y1 = my_pod1.predict_position(1)
    x2, y2 = my_pod2.predict_position(1)
    x3, y3 = opp_pod1.predict_position(1)
    x4, y4 = opp_pod2.predict_position(1)

    # Collision detection and shield activation
    if math.hypot(x1 - x3, y1 - y3) < 800:
        if max(math.hypot(opp_pod1.vx, opp_pod1.vy), math.hypot(my_pod1.vx, my_pod1.vy)) > 300 and 40 < abs(
                opp_pod1.angle - my_pod1.angle) < 320:
            thrust1 = 'SHIELD'
    elif math.hypot(x1 - x4, y1 - y4) < 800:
        if max(math.hypot(opp_pod2.vx, opp_pod2.vy), math.hypot(my_pod1.vx, my_pod1.vy)) > 300 and 40 < abs(
                opp_pod2.angle - my_pod1.angle) < 320:
            thrust1 = 'SHIELD'
    if math.hypot(x2 - x3, y2 - y3) < 800:
        if max(math.hypot(opp_pod1.vx, opp_pod1.vy), math.hypot(my_pod2.vx, my_pod2.vy)) > 300 and 40 < abs(
                opp_pod1.angle - my_pod2.angle) < 320:
            thrust2 = 'SHIELD'
    elif math.hypot(x2 - x4, y2 - y4) < 800:
        if max(math.hypot(opp_pod2.vx, opp_pod2.vy), math.hypot(my_pod2.vx, my_pod2.vy)) > 300 and 40 < abs(
                opp_pod2.angle - my_pod2.angle) < 320:
            thrust2 = 'SHIELD'

            # Output commands
    print(f"{my_pod1.target_x} {my_pod1.target_y} {thrust1}")
    print(f"{my_pod2.target_x} {my_pod2.target_y} {thrust2}")
