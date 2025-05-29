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
    def test(self):
        print("meow")


# Classe ReColor: extensão do sensor de cor padrão para incluir funcionalidades adicionais
class ReColor(ColorSensor):
    def __init__(self, port):
        # Inicializa a classe base com a porta especificada
        super().__init__(port)
        self.port = port




    def rgb_to_hsv(self, r, g, b):
        """
        Converte um valor RGB (Red, Green, Blue) para o espaço de cor HSV (Hue, Saturation, Value).

        Parâmetros:
            r (int): Componente vermelho (0–255)
            g (int): Componente verde (0–255)
            b (int): Componente azul (0–255)

        Retorno:
            tuple: (h, s, v)
                h (float): Matiz, em graus (0 a 360)
                s (float): Saturação (0 a 1)
                v (float): Valor/brilho (0 a 1)
        """
        # Normaliza os valores RGB para o intervalo [0, 1]
        r, g, b = r / 255.0, g / 255.0, b / 255.0

        # Determina os valores máximo e mínimo entre os componentes
        cmax = max(r, g, b)
        cmin = min(r, g, b)
        delta = cmax - cmin

        # Cálculo da Matiz (Hue)
        if delta == 0:
            h = 0  # Matiz indefinido, cor acromática
        elif cmax == r:
            h = (60 * ((g - b) / delta)) % 360
        elif cmax == g:
            h = (60 * ((b - r) / delta) + 120) % 360
        elif cmax == b:
            h = (60 * ((r - g) / delta) + 240) % 360

        # Cálculo da Saturação (Saturation)
        if cmax == 0:
            s = 0  # Sem saturação (cor preta)
        else:
            s = delta / cmax

        # O Valor (Value) é o maior dos componentes RGB normalizados
        v = cmax

        # Retorna a tupla HSV
        return h, s, v

    def hsv_to_rgb(self, h, s, v):
        """
        Converte um valor HSV (Hue, Saturation, Value) para o espaço de cor RGB (Red, Green, Blue).

        Parâmetros:
            h (float): Matiz, em graus (0 a 360)
            s (float): Saturação (0 a 255)
            v (float): Valor/brilho (0 a 255)

        Retorno:
            tuple: (r, g, b)
                r (int): Componente vermelho (0–255)
                g (int): Componente verde (0–255)
                b (int): Componente azul (0–255)
        """
        # Normaliza saturação e valor para o intervalo [0, 1]
        s /= 255.0
        v /= 255.0

        c = v * s  # Chroma: intensidade da cor
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c

        # Define os valores RGB intermediários com base no setor do círculo HSV
        if 0 <= h < 60:
            r_, g_, b_ = c, x, 0
        elif 60 <= h < 120:
            r_, g_, b_ = x, c, 0
        elif 120 <= h < 180:
            r_, g_, b_ = 0, c, x
        elif 180 <= h < 240:
            r_, g_, b_ = 0, x, c
        elif 240 <= h < 300:
            r_, g_, b_ = x, 0, c
        elif 300 <= h < 360:
            r_, g_, b_ = c, 0, x
        else:
            r_, g_, b_ = 0, 0, 0  # Valor inválido de h, retorna preto

        # Ajusta o brilho final (m) e converte para o intervalo [0, 255]
        r = int((r_ + m) * 255)
        g = int((g_ + m) * 255)
        b = int((b_ + m) * 255)

        return r, g, b



    def reflection(self):
        # Retorna o valor de reflexão de luz (intensidade luminosa)
        return super().reflect()

    def color(self):
        # Retorna a cor detectada como uma enumeração de cor (Color)
        return super().color()

    def hsv(self, surface):
        # Retorna os componentes HSV conforme fornecido pela API nativa do sensor
        return super().hsv(surface)

    def hsv(self):
        # Retorna os componentes HSV conforme fornecido pela API nativa do sensor
        return super().hsv(True)

    def rgb(self, surface):
        # Retorna os componentes HSV conforme fornecido pela API nativa do sensor

        hsv = super().hsv(surface)
        return self.rgb_to_hsv(hsv[0], hsv[1], hsv[2])

    def rgb(self):
        # Retorna os componentes HSV conforme fornecido pela API nativa do sensor

        hsv = super().hsv(True)
        return rgb_to_hsv(hsv[0], hsv[1], hsv[2])


