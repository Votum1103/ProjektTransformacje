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


if __name__ == "__main__":
    Transformations.dms(0.7876567)
    a = Transformations(phi=53.55170961, lam=15.73965028, h=337.369)
    print(a.neu(3681447.9096197425, 1028952.9746189445, 5089166.681763504))
