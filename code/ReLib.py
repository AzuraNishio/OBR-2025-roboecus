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


class ReColor(ColorSensor):
    def __init__(self, port):
        super().__init__(port)
        self.port = port

        # Multiplicadores padrão (1.0)
        self.multiplicador_vermelho = 1.0
        self.multiplicador_verde = 1.0
        self.multiplicador_azul = 1.0
        self.multiplicador_geral = 1.0

    def set_multiplicadores(self, vermelho=1.0, verde=1.0, azul=1.0, geral=1.0):
        """Atualiza os multiplicadores de ajuste de cor."""
        self.multiplicador_vermelho = vermelho
        self.multiplicador_verde = verde
        self.multiplicador_azul = azul
        self.multiplicador_geral = geral

    def aplicar_multiplicadores(self, r, g, b):
        """Aplica os multiplicadores definidos aos valores RGB."""
        r = int(r * self.multiplicador_vermelho * self.multiplicador_geral)
        g = int(g * self.multiplicador_verde * self.multiplicador_geral)
        b = int(b * self.multiplicador_azul * self.multiplicador_geral)
        return r, g, b

    def rgb_to_hsv(self, r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        cmax = max(r, g, b)
        cmin = min(r, g, b)
        delta = cmax - cmin

        if delta == 0:
            h = 0
        elif cmax == r:
            h = (60 * ((g - b) / delta)) % 360
        elif cmax == g:
            h = (60 * ((b - r) / delta) + 120) % 360
        elif cmax == b:
            h = (60 * ((r - g) / delta) + 240) % 360

        s = 0 if cmax == 0 else delta / cmax
        v = cmax

        return h, s, v

    def hsv_to_rgb(self, h, s, v):
        s /= 255.0
        v /= 255.0
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c

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
            r_, g_, b_ = 0, 0, 0

        r = int((r_ + m) * 255)
        g = int((g_ + m) * 255)
        b = int((b_ + m) * 255)

        return r, g, b

    def reflection(self):
        return super().reflection()

    def color(self):
        return super().color()

    def hsv(self, surface=True):
        return super().hsv(surface)

    def rgb(self, surface=True):
        """Retorna os valores RGB ajustados com multiplicadores."""
        h, s, v = super().hsv(surface)
        r, g, b = self.hsv_to_rgb(h, s, v)
        return self.aplicar_multiplicadores(r, g, b)

    def compare_rgb(self, color, abs_threshold=30, prop_threshold=0.1):
        r1, g1, b1 = self.rgb()
        r2, g2, b2 = color

        abs_distance = pow((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2, 0.5)
        epsilon = 1e-6

        sum1 = r1 + g1 + b1 + epsilon
        sum2 = r2 + g2 + b2 + epsilon

        prop_r1, prop_g1, prop_b1 = r1 / sum1, g1 / sum1, b1 / sum1
        prop_r2, prop_g2, prop_b2 = r2 / sum2, g2 / sum2, b2 / sum2

        prop_distance = pow(
            (prop_r1 - prop_r2) ** 2 +
            (prop_g1 - prop_g2) ** 2 +
            (prop_b1 - prop_b2) ** 2,
            0.5
        )

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

    def info_dump(self):
        """Imprime no console os dados completos dos sensores e suas diferenças."""
        l_r, l_g, l_b = self.left.rgb()
        r_r, r_g, r_b = self.right.rgb()
        l_h, l_s, l_v = self.left.hsv()
        r_h, r_s, r_v = self.right.hsv()
        l_ref = self.left.reflection()
        r_ref = self.right.reflection()

        rgb_diff = self.rgb_difference()
        hsv_diff = self.hsv_difference()
        r_diff = self.r_difference()
        g_diff = self.g_difference()
        b_diff = self.b_difference()
        h_diff = self.h_difference()
        s_diff = self.s_difference()
        v_diff = self.v_difference()
        ref_diff = self.reflection_difference()

        r2_diff = self.r_squared_difference()
        g2_diff = self.g_squared_difference()
        b2_diff = self.b_squared_difference()
        h2_diff = self.h_squared_difference()
        s2_diff = self.s_squared_difference()
        v2_diff = self.v_squared_difference()
        ref2_diff = self.squared_reflection_difference()

        print(f"""
       ========== ReColor Duo Info Dump ==========
       --- LEFT SENSOR ---
       RGB : ({l_r:3d}, {l_g:3d}, {l_b:3d})
       HSV : ({l_h:6.1f}, {l_s:6.3f}, {l_v:6.3f})
       Reflexão: {l_ref}

       --- RIGHT SENSOR ---
       RGB : ({r_r:3d}, {r_g:3d}, {r_b:3d})
       HSV : ({r_h:6.1f}, {r_s:6.3f}, {r_v:6.3f})
       Reflexão: {r_ref}

       --- DIFFERENCES (LEFT - RIGHT) ---
       RGB Diferença      : {rgb_diff}
       HSV Diferença      : ({h_diff:+6.1f}, {s_diff:+6.3f}, {v_diff:+6.3f})
       Reflexão Diferença : {ref_diff:+.2f}

       --- SQUARED DIFFERENCES ---
       R² Dif: {r2_diff:+.2f}, G² Dif: {g2_diff:+.2f}, B² Dif: {b2_diff:+.2f}
       H² Dif: {h2_diff:+.2f}, S² Dif: {s2_diff:+.2f}, V² Dif: {v2_diff:+.2f}
       Reflexão² Dif      : {ref2_diff:+.2f}
       ===========================================
       """)

    def is_one_sensor_on_color(self, color, limit):
        return self.left.compare_rgb(color, limit) or self.right.compare_rgb(color, limit)

