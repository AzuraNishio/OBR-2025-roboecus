from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch
import umath as math

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
        super().use_gyro(True)
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
        return self.hsv_to_rgb(hsv[0], hsv[1], hsv[2])

    def rgb(self):
        # Retorna os componentes HSV conforme fornecido pela API nativa do sensor

        hsv = super().hsv(True)
        return self.hsv_to_rgb(hsv[0], hsv[1], hsv[2])


    def compare_rgb(self, color, abs_threshold=30, prop_threshold=0.1):
        r1, g1, b1 = self.rgb()  # current sensor RGB
        r2, g2, b2 = color       # target color

        # Calculate absolute Euclidean distance
        abs_distance = pow((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2, 0.5)

        # To avoid division by zero, add a tiny epsilon
        epsilon = 1e-6

        # Normalize RGB to proportions
        sum1 = r1 + g1 + b1 + epsilon
        sum2 = r2 + g2 + b2 + epsilon

        prop_r1, prop_g1, prop_b1 = r1 / sum1, g1 / sum1, b1 / sum1
        prop_r2, prop_g2, prop_b2 = r2 / sum2, g2 / sum2, b2 / sum2

        # Calculate proportional distance (Euclidean in normalized RGB space)
        prop_distance = pow(
            (prop_r1 - prop_r2)**2 +
            (prop_g1 - prop_g2)**2 +
            (prop_b1 - prop_b2)**2,
            0.5
        )

        # Return True only if both absolute and proportional distances are below thresholds
        return abs_distance < abs_threshold and prop_distance < prop_threshold



class ReColorDuo:
    def __init__(self, left: ReColor, right: ReColor):
        self.left = left
        self.right = right

    def reflection_difference(self):
        """Returns the signed difference in reflection (left - right)."""
        return self.left.reflection() - self.right.reflection()

    def squared_reflection_difference(self):
        """
        Returns signed difference between squared reflection values.
        Keeps sign of the difference after sqrt of abs value.
        """
        left_sq = pow(self.left.reflection(), 2)
        right_sq = pow(self.right.reflection(), 2)
        diff = left_sq - right_sq
        return math.sqrt(abs(diff)) * (1 if diff >= 0 else -1)

    # --- RGB COMPONENT DIFFERENCES ---
    def rgb_difference(self):
        """
        Returns a tuple of signed RGB differences (left - right).
        Example: (ΔR, ΔG, ΔB)
        """
        r1, g1, b1 = self.left.rgb()
        r2, g2, b2 = self.right.rgb()
        return (r1 - r2, g1 - g2, b1 - b2)
    
    def r_difference(self):
        return self.left.rgb()[0] - self.right.rgb()[0]

    def g_difference(self):
        return self.left.rgb()[1] - self.right.rgb()[1]

    def b_difference(self):
        return self.left.rgb()[2] - self.right.rgb()[2]

    def r_squared_difference(self):
        r1 = self.left.rgb()[0] ** 2
        r2 = self.right.rgb()[0] ** 2
        diff = r1 - r2
        return math.sqrt(abs(diff)) * (1 if diff >= 0 else -1)

    def g_squared_difference(self):
        g1 = self.left.rgb()[1] ** 2
        g2 = self.right.rgb()[1] ** 2
        diff = g1 - g2
        return math.sqrt(abs(diff)) * (1 if diff >= 0 else -1)

    def b_squared_difference(self):
        b1 = self.left.rgb()[2] ** 2
        b2 = self.right.rgb()[2] ** 2
        diff = b1 - b2
        return math.sqrt(abs(diff)) * (1 if diff >= 0 else -1)

    # --- HSV COMPONENT DIFFERENCES ---
    
    def hsv_difference(self):
        """
        Returns a tuple of signed HSV differences (left - right).
        Example: (ΔH, ΔS, ΔV)
        """
        h1, s1, v1 = self.left.hsv()
        h2, s2, v2 = self.right.hsv()
        return (h1 - h2, s1 - s2, v1 - v2)

    def h_difference(self):
        return self.left.hsv()[0] - self.right.hsv()[0]

    def s_difference(self):
        return self.left.hsv()[1] - self.right.hsv()[1]

    def v_difference(self):
        return self.left.hsv()[2] - self.right.hsv()[2]

    def h_squared_difference(self):
        h1 = self.left.hsv()[0] ** 2
        h2 = self.right.hsv()[0] ** 2
        diff = h1 - h2
        return math.sqrt(abs(diff)) * (1 if diff >= 0 else -1)

    def s_squared_difference(self):
        s1 = self.left.hsv()[1] ** 2
        s2 = self.right.hsv()[1] ** 2
        diff = s1 - s2
        return math.sqrt(abs(diff)) * (1 if diff >= 0 else -1)

    def v_squared_difference(self):
        v1 = self.left.hsv()[2] ** 2
        v2 = self.right.hsv()[2] ** 2
        diff = v1 - v2
        return math.sqrt(abs(diff)) * (1 if diff >= 0 else -1)

    def compare_both_to_color(self, target_rgb, threshold):
        """
        Returns True if either sensor matches the target color within threshold.
        """
        return (self.left.compare_rgb(target_rgb, threshold), self.right.compare_rgb(target_rgb, threshold))
        

    def get_raw_data(self):
        """Returns raw RGB and reflection values from both sensors."""
        return {
            "left_rgb": self.left.rgb(),
            "right_rgb": self.right.rgb(),
            "left_reflection": self.left.reflection(),
            "right_reflection": self.right.reflection()
        }
    
    def get_sensor_right_if_true(self, direito):
        if direito:
            return self.right
        else:
            return self.left
