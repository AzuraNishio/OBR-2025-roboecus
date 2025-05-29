from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch


class ReDriveBase(DriveBase):
    def __init__(self, left_motor, right_motor, wheel_diameter, axle_track):
        super().__init__(left_motor, right_motor, wheel_diameter, axle_track)
        self.left = left_motor
        self.right = right_motor
        self.diameter = wheel_diameter
        self.axle = axle_track


        self.curve_cultiplier = 1.0

    def drive(self, speed: float, angular_speed: float):
        super().use_gyro(False)
        super().drive(speed, angular_speed * self.curve_cultiplier)


    def drive_with_gyro(self, speed: float, angular_speed: float):
        super().use_gyro(True)
        super().drive(speed, angular_speed * self.curve_cultiplier)
    


    def brake(self):
        super().brake()
    
    def curve(self, degrees, radius, speed):
        super().curve(radius, degrees)
    
    def calibrate(self, hub: PrimeHub):
        starting_heading = hub.imu.heading()
        super().drive(0, 45)
        wait(4000)
        super().brake()
        delta_heading = hub.imu.heading() - starting_heading
        self.curve_cultiplier = 180/delta_heading
        print(delta_heading)
        print(self.curve_cultiplier)

        speed = 128
        value = 128

        for i in range(7):

            starting_heading = hub.imu.heading()
            super().drive(0, speed * self.curve_cultiplier)
            wait(500)
            super().brake()
            delta_heading = hub.imu.heading() - starting_heading
            if(delta_heading > 0.5 * speed * self.curve_cultiplier):
                speed -= value
            else:
                speed += value
            value /=2
            wait(100)
        print(speed)






class ReHub(PrimeHub):
    def test():
        print("meow")
        