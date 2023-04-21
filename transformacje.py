import numpy as np


class Transformations:

    def __init__(self, elipsoid_name):
        """
        nazwa elipsoidy musi być wybrana spośród: GRS80, WGS84, Krasowski

        """
        self.elipsoid_name = elipsoid_name
        if elipsoid_name == "GRS80":
            self.a = 6378137
            self.e2 = 0.00669438002290
        elif elipsoid_name == "WGS84":
            self.e2 = 0.00669437999014
            self.a = 6378137
        elif elipsoid_name == "Krasowski":
            self.a = 6378245
            self.e2 = 0.00669342162296

    @staticmethod
    def dms(value: float) -> str:
        """
    Zamienia wartość w radianach na wartość w stopniach, minutach i sekundach
    i zwraca ją jako string.

        """

        znak = ' '
        if value < 0:
            znak = "-"
            value = abs(value)
        value = value * 180/np.pi
        degrees = int(value)
        minutes = int((value - degrees) * 60)
        seconds = (value-degrees-minutes/60)*3600
        d_sign = "\N{DEGREE SIGN}"
        return f"{znak}{degrees:3d}{d_sign}{minutes:2d}'{seconds:7.5f}\""

    def xyz_kras_2_xyz_grs80(self, phi_k, lam_k, h_k):
        if self.elipsoid_name == "Krasowski":
            xk, yk, zk = self.flh2XYZ(
                phi_k, lam_k, h_k)

            Tx = -33.4297
            Ty = 146.5746
            Tz = 76.2865

            d11 = 1 - 0.84078048E-6
            d12 = - 4.08959962E-6
            d13 = -0.25614575E-6
            d21 = +4.08960007E-6
            d22 = 1 - 0.84078196E-6
            d23 = +1.73888389E-6
            d31 = +0.25613864E-6
            d32 = -1.73888494E-6
            d33 = 1 - 0.84077363E-6

            x = d11 * (xk - Tx) + d12 * (yk - Ty) + d13 * (zk - Tz)
            y = d21 * (xk - Tx) + d22 * (yk - Ty) + d23 * (zk - Tz)
            z = d31 * (xk - Tx) + d32 * (yk - Ty) + d33 * (zk - Tz)
            return (x, y, z)
        else:
            print("Nie wybrano elipsoidy Krasowskiego")

    def hirvonen(self, x, y, z) -> tuple[float, float, float]:
        """
    Przelicza współrzędne prostokątne w układzie elipsoidy GRS
    do geodezyjnych φ, λ, h. Transformacja
    zwraca wynik w radianach postaci: (φ, λ, h)
        """
        a = self.a
        e2 = self.e2
        p = np.sqrt(x**2+y**2)
        phi = np.arctan(z/(p * (1 - e2)))
        while True:
            n = a / np.sqrt(1-e2 * np.sin(phi)**2)
            h = p / np.cos(phi) - n
            phi_p = phi
            phi = np.arctan(z / (p*(1 - e2 * n / (n + h))))
            if abs(phi_p - phi) < (0.000001/206265):
                break
        lam = np.arctan2(y, x)
        return (phi, lam, h)

    def flh2XYZ(self, phi, lam, h) -> tuple[float, float, float]:
        """

    Zamienia współrzędne geodezyjne φ, λ, h do współrzędnych
    prostokątnych X,Y,Z w układzie elipsoidy GRS 80.
    Transformacja odwrotna do Hirvonena.
    wynik w postaci: (X,Y,Z)

        """
        a = self.a
        e2 = self.e2
        phi = np.deg2rad(phi)
        lam = np.deg2rad(lam)
        N = a / np.sqrt(1-e2 * np.sin(phi)**2)
        X = (N+h) * np.cos(phi) * np.cos(lam)
        Y = (N+h) * np.cos(phi) * np.sin(lam)
        Z = (N * (1-e2) + h) * np.sin(phi)
        return (X, Y, Z)

    def neu(self, x_odbiornika: float, y_odbiornika: float,
            z_odbiornika: float, x_satelity: float,
            y_satelity: float, z_satelity: float) -> float:
        """
Transformuje współrzędne geocentryczne odbiornika do
współrzędnych topocentrycznych
        """
        phi_odbiornika = self.hirvonen(
            x_odbiornika, y_odbiornika, z_odbiornika)[0]
        lam_odbiornika = self.hirvonen(
            x_odbiornika, y_odbiornika, z_odbiornika)[1]
        Rneu = np.array([[-np.sin(phi_odbiornika) * np.cos(lam_odbiornika),
                          -np.sin(lam_odbiornika),
                          np.cos(phi_odbiornika) * np.cos(lam_odbiornika)],
                         [-np.sin(phi_odbiornika) * np.sin(lam_odbiornika),
                             np.cos(lam_odbiornika),
                             np.cos(phi_odbiornika) * np.sin(lam_odbiornika)],
                         [np.cos(phi_odbiornika), 0,
                             np.sin(phi_odbiornika)]])

        X_sr = [x_odbiornika - x_satelity, y_odbiornika -
                y_satelity, z_odbiornika - z_satelity]

        neu = Rneu.T @ X_sr
        return neu

    def fl_2_2000(self, phi: float, lam: float,
                  l0: float, h_krasowski=None) -> tuple[float, float]:
        '''
        Funkcja przelicza współrzędne geodezyjne φ, λ
        na współrzędne geocentryczne w układzie PL-2000.
        Istnieje możliwość wyboru elipsoidy,
        z której przeliczane będą współrzędne, w tym celu
        należy podać jej nazwę ("WGS84", "GRS80" lub "Krasowski")
        południk osiowy l0 należy podać w stopniach.
        wynik w postaci: (X_2000,Y_2000)


        '''
        a = self.a
        e2 = self.e2
        m = 0.999923
        if self.elipsoid_name == "Krasowski":
            x, y, z = self.xyz_kras_2_xyz_grs80(phi, lam, h_krasowski)
            e2 = self.e2 = 0.00669438002290
            a = self.a = 6378137
            phi, lam, h = self.hirvonen(x, y, z)
        else:
            phi = np.deg2rad(phi)
            lam = np.deg2rad(lam)

        b2 = (a**2)*(1-e2)
        ep2 = (a**2 - b2)/b2
        dl = lam - np.deg2rad(l0)
        t = np.tan(phi)
        ni2 = ep2 * np.cos(phi)**2
        n = a / np.sqrt(1-e2 * np.sin(phi)**2)
        A0 = 1 - e2/4-3*e2**2/64-5*e2**3/256
        A2 = 3/8*(e2+e2**2/4+15*e2**3/128)
        A4 = 15/256*(e2**2 + 3*e2**3/4)
        A6 = 35*e2**3/3072
        sig = a*(A0 * phi - A2 * np.sin(2*phi) + A4 *
                 np.sin(4*phi) - A6*np.sin(6*phi))
        xgk = sig + (dl**2)/2 * n*np.sin(phi)*np.cos(phi)*(1 + (dl**2)/12 * np.cos(phi)**2 * (5 - t**2 +
                                                                                              9*ni2 + 4*ni2**2) + dl**4/360*np.cos(phi)**4 * (61 - 58*t**2 + t**4 + 270*ni2 - 330*ni2*t**2))
        ygk = dl*n*np.cos(phi) * (1 + (dl**2)/6 * np.cos(phi)**2 * (1 - t**2 + ni2) +
                                      (dl**4)/120*np.cos(phi)**4 * (5 - 18*t**2 + t**4 + 14*ni2 - 58*ni2*t**2))
        pas = 0
        for _ in range(15):
            if round(np.rad2deg(lam)/3, 0) == pas:
                nr = pas
            pas += 1

        x20 = xgk * m
        y20 = ygk * m + nr*1000000 + 500000
        return (x20, y20)

    def fl_2_1992(self, phi: float, lam: float,
                  l0: float, h_krasowski=None) -> tuple[float, float]:
        """
        Funkcja przelicza współrzędne geodezyjne φ, λ
        na współrzędne geocentryczne w układzie PL-1992.
        Istnieje możliwość wyboru elipsoidy,
        z której przeliczane będą współrzędne, w tym celu
        należy podać jej nazwę ("WGS84", "GRS80" lub "Krasowski")
        południk osiowy l0 należy podać w stopniach.
        wynik w postaci: (X_1992,Y_1992)
        """

        a = self.a
        e2 = self.e2
        if self.elipsoid_name == "Krasowski":
            if h_krasowski is None:
                return "Nie podałeś wysokości"
            x, y, z = self.xyz_kras_2_xyz_grs80(phi, lam, h_krasowski)
            e2 = self.e2 = 0.00669438002290
            a = self.a = 6378137
            phi, lam, h = self.hirvonen(x, y, z)
        else:
            phi = np.deg2rad(phi)
            lam = np.deg2rad(lam)

        m92 = 0.9993
        b2 = (a**2)*(1-e2)
        ep2 = (a**2 - b2)/b2
        dl = lam - np.deg2rad(l0)
        t = np.tan(phi)
        ni2 = ep2 * np.cos(phi)**2
        N = a / np.sqrt(1-e2 * np.sin(phi)**2)
        A0 = 1 - e2/4-3*e2**2/64-5*e2**3/256
        A2 = 3/8*(e2+e2**2/4+15*e2**3/128)
        A4 = 15/256*(e2**2 + 3*e2**3/4)
        A6 = 35*e2**3/3072
        sigma = a*(A0 * phi - A2 * np.sin(2*phi) + A4 *
                   np.sin(4*phi) - A6*np.sin(6*phi))
        xgk = sigma + (dl**2)/2 * N*np.sin(phi)*np.cos(phi)*(1 + (dl**2)/12 * np.cos(phi)**2 * (5 - t**2 +
                                                                                                9*ni2 + 4*ni2**2) + dl**4/360*np.cos(phi)**4 * (61 - 58*t**2 + t**4 + 270*ni2 - 330*ni2*t**2))
        ygk = dl*N*np.cos(phi) * (1 + (dl**2)/6 * np.cos(phi)**2 * (1 - t**2 + ni2) +
                                      (dl**4)/120*np.cos(phi)**4 * (5 - 18*t**2 + t**4 + 14*ni2 - 58*ni2*t**2))
        x92 = xgk * m92 - 5300000
        y92 = ygk * m92 + 500000
        return (x92, y92)


if __name__ == "__main__":
    trans1 = Transformations("Krasowski")
    x_20_k, y_20_k = trans1.fl_2_2000(
        50 + 1.343186/3600, 16 + 6.268112/3600, 15, 300)
    print('x_20_k, y_20_k: ', x_20_k, y_20_k)
    trans2 = Transformations("GRS80")
    x_20, y_20 = trans2.fl_2_2000(50, 16, 15)
    print('x_20,y_20: ', x_20, y_20)
