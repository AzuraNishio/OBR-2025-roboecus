from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Direction, Port
from pybricks.tools import StopWatch
from ReLib import *

# Hub e sensores
hub = PrimeHub()
cronometro = StopWatch()
cronometro_linha = StopWatch()

sensor_direito = ReColor(Port.B)
sensor_esquerdo = ReColor(Port.A)
sensor_frente = ReColor(Port.C)
sensores = ReColorDuo(sensor_esquerdo, sensor_direito)
sonic = UltrasonicSensor(Port.D)

# Motores
motor_esquerdo = Motor(Port.E)
motor_direito = Motor(Port.F, Direction.COUNTERCLOCKWISE)
base = ReDriveBase(motor_esquerdo, motor_direito, wheel_diameter=38, axle_track=112)

# Calibração
sensor_esquerdo.set_multiplicadores(1, 1, 1, 0.9)
sensor_direito.set_multiplicadores(1, 1, 1, 0.9)

# Resetar ângulo
hub.imu.reset_heading(0)
