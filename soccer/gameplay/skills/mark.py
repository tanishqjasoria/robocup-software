import single_robot_behavior
import behavior
import robocup
import main
import constants
import role_assignment


class Mark(single_robot_behavior.SingleRobotBehavior):
    def __init__(self):
        super().__init__(continuous=True)
        self._ratio = 0.9
        self._mark_line_thresh = 0.9
        self._mark_robot = None
        self._mark_point = None
        self._target_point = None

        self.add_transition(behavior.Behavior.State.start,
                            behavior.Behavior.State.running, lambda: True,
                            "immediately")

    def execute_running(self):
        #pylint: disable=no-member
        if self.mark_point is None and \
           (self.mark_robot is None or
            not main.ball().valid or
            not self.mark_robot.visible):
            return

        ball_pos = main.ball().pos
        pos = self.robot.pos
        mark_pos = self.mark_point if self.mark_point is not None else self.mark_robot.pos

        mark_line_dir = (ball_pos - mark_pos).normalized()
        ball_mark_line = robocup.Segment(
            ball_pos - mark_line_dir * constants.Ball.Radius,
            mark_pos + mark_line_dir * 2.0 * constants.Robot.Radius)

        main.system_state().draw_line(ball_mark_line, (0, 0, 255), "Mark")

        mark_line_dist = ball_mark_line.dist_to(pos)
        self._target_point = None
        if mark_line_dist > self.mark_line_thresh:
            self._target_point = ball_mark_line.nearest_point(pos)
        else:
            self._target_point = ball_pos + (
                mark_pos -
                ball_pos).normalized() * self.ratio * ball_mark_line.length()

        main.system_state().draw_circle(mark_pos, constants.Robot.Radius * 1.2,
                                        (0, 127, 255), "Mark")

        if self.mark_robot is not None:
            self.robot.approach_opponent(self.mark_robot.shell_id(), True)
        self.robot.move_to(self._target_point)
        self.robot.face(ball_pos)

    @property
    def ratio(self):
        return self._ratio

    @ratio.setter
    def ratio(self, value):
        self._ratio = min(max(value, 0.0), 1.0)

    @property
    def mark_line_thresh(self):
        return self._mark_line_thresh

    @mark_line_thresh.setter
    def mark_line_thresh(self, value):
        self._mark_line_thresh = value

    # Overrides mark_robot with a static point
    # If mark_point is set, we will still need a mark robot
    # (for the approach_opponent function above)
    @property
    def mark_point(self) -> robocup.Point:
        return self._mark_point

    @mark_point.setter
    def mark_point(self, value: robocup.Point):
        self._mark_point = value

    @property
    def mark_robot(self) -> robocup.Robot:
        return self._mark_robot

    @mark_robot.setter
    def mark_robot(self, value: robocup.Robot):
        self._mark_robot = value

    # Choose a robot close to the mark point
    def role_requirements(self):
        req = super().role_requirements()
        if self._target_point is not None:
            req.destination_shape = self._target_point
        return req
