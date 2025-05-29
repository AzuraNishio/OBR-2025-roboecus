from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Direction, Port
from pybricks.tools import wait, StopWatch
from ReLib import ReDriveBase

# Initialize hub and timer
hub = PrimeHub()
timer = StopWatch()
line_timer = StopWatch()

# Sensors
right_color = ColorSensor(Port.B)
left_color = ColorSensor(Port.A)

# Motors
left_motor = Motor(Port.C)
right_motor = Motor(Port.D, Direction.COUNTERCLOCKWISE)

# Drive base
drive_base = ReDriveBase(left_motor, right_motor, wheel_diameter=38, axle_track=112)

# Parâmetros PDC (Proporcional Derivado Cumulativo)
kp = -6.5
kd = 0.012
kc = 0.02

#Velocidades lineares
base_speed = 75 #velocidade usado em curvas e correção suave
line_speed = 120 #velocidade usada em linhas beeem retas
#velocidades angulares
search_speed = 120 #velocidade usada para procurar o preto na busca de linha
fine_speed = 10 #velocidade usada para ajustes finos de angulo

search_threshold = 51 #valor mínimo de erro para inicar a busca
black_threshold = 8 #abaixo desse valor é preto
gray_range = 12 #acima de black_threshold + gray_range é branco



cumulative_curve = 0
error = 0
last_time = timer.time()
time_in_line = 0
line_starting_angle = 0
line_first_error = 0
was_in_line: bool = False
hub.imu.reset_heading(0)



# Loop forever
while True:
    # Time delta calculation (in seconds), protected against zero
    current_time = timer.time()
    delta_t = max(0.001, (current_time - last_time) / 1000)  # ms to s
    last_time = current_time

    # Calculate error between left and right sensor reflections
    last_error = error
    error = right_color.reflection() - left_color.reflection()
    quadratic_error = pow(pow(right_color.reflection(),2) - pow(left_color.reflection(),2),0.5)

    # Derivative: rate of error change
    derivative = (last_error - error) / delta_t

    # Calculate steering correction
    correction = error * kp + derivative * kd

    # Determine direction of correction safely
    if correction != 0:
        correction_sign = correction / abs(correction)
    else:
        correction_sign = 0

    # Handle curve buildup logic
    if abs(correction) > 10:
        # Allow buildup if cumulative_curve is 0 or heading in same direction
        if cumulative_curve == 0 or correction_sign == cumulative_curve / abs(cumulative_curve):
            cumulative_curve += correction_sign * delta_t * kc
        else:
            cumulative_curve = 0
    else:
        cumulative_curve = 0

    # Apply movement
    if abs(correction) > 10:
        if abs(correction) > 35:
            drive_base.drive_with_gyro(base_speed, correction + cumulative_curve)
        else:
            drive_base.drive(line_speed, correction + cumulative_curve)
    else:
        drive_base.drive(line_speed, 0)


    if abs(quadratic_error) > search_threshold:
        if not was_in_line:
            line_timer.reset()
            line_timer.resume()
            line_starting_angle = hub.imu.heading()
            line_first_error = error
        else:
            drive_base.straight(30)
            drive_base.straight(45)
            drive_base.drive(0, -1 * search_speed * (line_first_error / abs(line_first_error)))
            if line_first_error < 0:
                while left_color.reflection() > black_threshold:
                    wait(1)
            else:
                while right_color.reflection() > black_threshold:
                    wait(1)

            drive_base.drive(0,line_speed * (line_first_error / abs(line_first_error)))
            if line_first_error < 0:
                while left_color.reflection() < black_threshold + gray_range:
                    wait(1)
            else:
                while right_color.reflection() < black_threshold + gray_range:
                    wait(1)
        was_in_line = True
    else:
        if was_in_line:
            time_in_line = line_timer.time()
            line_timer.pause()
        was_in_line = False








    # Brief pause to avoid CPU overload
    wait(1)
