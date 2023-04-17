import numpy as np


class Transformations:

    def __init__(self, x=None, y=None, z=None, h=None, phi=None, lam=None):
        """
        wartości x, y, z, h muszą być podane w metrach,
        φ i λ muszą być podane w stopniach

        """
        self.x = x
        self.y = y
        self.z = z
        self.h = h
        if phi and lam is not None:
            self.phi = np.deg2rad(phi)
            self.lam = np.deg2rad(lam)

    @staticmethod
    def dms(value):
        """
    Zamienia wartość w radianach na wartość w stopniach, minutach i sekundach
    i wyświetla ją. Funkcja nie zwraca zadnych wartości.

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
        print(f"{znak}{degrees:3d}{d_sign}{minutes:2d}\'{seconds:7.5f}\"")

    def hirvonen(self, a=6378137, e2=0.00669438002290) -> tuple[float, float, float]:
        """
    Przelicza współrzędne prostokątne w układzie elipsoidy GRS
    do geodezyjnych φ, λ, h. Transformacja
    zwraca wynik w radianach postaci: (φ, λ, h)
        """
        x = self.x
        y = self.y
        z = self.z
        if x and y and z is not None:
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
        else:
            print("Nie podałeś x,y,z")

    def flh2XYZ(self, a=6378137, e2=0.00669438002290) -> tuple[float, float, float]:
        """

    Zamienia współrzędne geodezyjne φ, λ, h do współrzędnych
    prostokątnych X,Y,Z w układzie elipsoidy GRS 80.
    Transformacja odwrotna do Hirvonena.
    wynik w postaci: (X,Y,Z)

        """
        phi = self.phi
        lam = self.lam
        h = self.h
        if phi and lam and h is not None:
            N = a / np.sqrt(1-e2 * np.sin(phi)**2)
            X = (N+h) * np.cos(phi) * np.cos(lam)
            Y = (N+h) * np.cos(phi) * np.sin(lam)
            Z = (N * (1-e2) + h) * np.sin(phi)
            return (X, Y, Z)
        else:
            print("Nie podałeś φ, λ lub h")

    def neu(self, x_satelity, y_satelity, z_satelity):
        """
Transformuje współrzędne geocentryczne odbiornika do
współrzędnych topocentrycznych
        """
        x_odbiornika = self.x
        y_odbiornika = self.y
        z_odbiornika = self.z
        if x_odbiornika and y_odbiornika and z_odbiornika is not None:
            phi_odbiornika = self.hirvonen()[0]
            lam_odbiornika = self.hirvonen()[1]
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

    def fl_2_2000(self ,nazwa_elipsoidy , l0):
        
            phi = np.rad2deg(self.phi)
            lam = self.lam
            if phi and lam is not None:
                if nazwa_elipsoidy == "WRG84" or "GRS80":
                    a = 6378137
                    e2 = 0.00669438002290
                    m = 0.999923
                elif nazwa_elipsoidy == "Krasowski":
                    a = 6378245
                    e2 = 0.00669342
                    m = 1
                else:
                    print("Nie ma możliwości wyboru takiej elipsoidy")
                
                b2 = (a**2)*(1-e2)
                ep2 = (a**2 - b2)/b2
                dl = np.deg2rad(lam) - np.deg2rad(l0)
                t = np.tan(phi)
                ni2 = ep2 * np.cos(phi)**2
                n = a / np.sqrt(1-e2 * np.sin(phi)**2)
                A0 = 1 - e2/4-3*e2**2/64-5*e2**3/256
                A2 = 3/8*(e2+e2**2/4+15*e2**3/128)
                A4 = 15/256*(e2**2 + 3*e2**3/4)
                A6 = 35*e2**3/3072
                sig = a*(A0 * phi - A2 * np.sin(2*phi) + A4 * np.sin(4*phi) - A6*np.sin(6*phi))
                xgk = sig + (dl**2)/2 * n*np.sin(phi)*np.cos(phi)*(1 + (dl**2)/12 * np.cos(phi)**2 * (5 - t**2 +
                                                                                                    9*ni2 + 4*ni2**2) + dl**4/360*np.cos(phi)**4 * (61 - 58*t**2 + t**4 + 270*ni2 - 330*ni2*t**2))
                ygk = dl*n*np.cos(phi) * (1 + (dl**2)/6 * np.cos(phi)**2 * (1 - t**2 + ni2) +
                                        (dl**4)/120*np.cos(phi)**4 * (5 - 18*t**2 + t**4 + 14*ni2 - 58*ni2*t**2))
                pas = 0
                for _ in range(15):
                    if round(lam/3, 0) == pas:
                        nr = pas
                    pas += 1

                x20 = xgk * m
                y20 = ygk * m + nr*1000000 + 500000
                print(nr)
                return (x20, y20)
            else:
                print("Nie podano współrzędncyh geodezyjnych")
       
    
if __name__ == "__main__":
    Transformations.dms(0.7876567)
    a = Transformations(phi=53.55170961, lam=15.73965028, h=337.369)
    print(a.neu(3681447.9096197425, 1028952.9746189445, 5089166.681763504))
