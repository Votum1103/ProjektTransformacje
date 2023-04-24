import numpy as np
import argparse


class Transformations:

    def __init__(self, elipsoid_name: str):
        """
        nazwa elipsoidy musi być wybrana spośród: GRS80, WGS84, Krasowski

        """

        self.elipsoid_name = elipsoid_name
        assert self.elipsoid_name == "GRS80" or "WGS84" or "Krasowski",\
            "The specified ellipsoid is not supported"
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
    def dms(value: float) -> tuple[float, float, float]:
        """
    Zamienia wartość w radianach na wartość w stopniach, minutach i sekundach,
    wyświetla ją w postaci deg°min'sec" i zwraca ją jako krotkę (deg, min, sec)

        """
        assert type(value) == float or int,\
            "Can't convert value with type different than float or int"
        if value < 0:
            symbol = "-"
        else:
            symbol = ' '
        value_deg = abs(value) * 180/np.pi
        degrees = int(value_deg)
        minutes = int((value_deg - degrees) * 60)
        seconds = (value_deg-degrees-minutes/60)*3600
        d_sign = "\N{DEGREE SIGN}"
        print(f"{symbol}{degrees:3d}{d_sign}{minutes:2d}'{seconds:7.5f}\"")
        return (degrees, minutes, round(seconds, 5))

    def xyz_kras_2_xyz_grs80(self, phi_k: float,
                             lam_k: float, h_k: float) -> tuple[float, float, float]:
        """
        Przelicza współrzędne xyz z elipsoidy Krasowskiego na xyz w układzie GRS80.
        By wykonać transformacje należy przy inicjalizacji klasy wskazać nazwę elipsoidy
        jako Krasowski.
        Zwraca wynik w postaci (x_grs80, y_grs80, z_grs80)
        """
        assert self.elipsoid_name == "Krasowski",\
            "You didn't select the Krasowski ellipsoid"

        xk, yk, zk = self.flh_2_xyz(phi_k, lam_k, h_k)

        params = {
            'Tx': -33.4297,
            'Ty': 146.5746,
            'Tz': 76.2865,
            'd11': 1 - 0.84078048E-6,
            'd12': - 4.08959962E-6,
            'd13': -0.25614575E-6,
            'd21': +4.08960007E-6,
            'd22': 1 - 0.84078196E-6,
            'd23': +1.73888389E-6,
            'd31': +0.25613864E-6,
            'd32': -1.73888494E-6,
            'd33': 1 - 0.84077363E-6
        }

        x_grs80 = params["d11"] * (xk - params["Tx"]) + params["d12"] * \
            (yk - params["Ty"]) + params["d13"] * (zk - params["Tz"])
        y_grs80 = params["d21"] * (xk - params["Tx"]) + params["d22"] * \
            (yk - params["Ty"]) + params["d23"] * (zk - params["Tz"])
        z_grs80 = params["d31"] * (xk - params["Tx"]) + params["d32"] * \
            (yk - params["Ty"]) + params["d33"] * (zk - params["Tz"])
        return (x_grs80, y_grs80, z_grs80)

    def hirvonen(self, x: float, y: float, z: float) -> tuple[float, float, float]:
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

    def flh_2_xyz(self, phi: float, lam: float, h: float) -> tuple[float, float, float]:
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
        należy podać jej nazwę ("WGS84", "GRS80" lub "Krasowski").
        Przy wyborze elipsoidy Krasowskiego należy podać h_krasowskiego.
        Południk osiowy l0 należy podać w stopniach.
        wynik w postaci: (X_2000,Y_2000)


        '''
        a = self.a
        e2 = self.e2
        m = 0.999923
        if self.elipsoid_name == "Krasowski":
            assert h_krasowski is not None, \
                "You didn't specify the height for the Krasowski ellipsoid"
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
        xgk_part_1 = (dl**2)/2 * n * np.sin(phi) * np.cos(phi)
        xgk_part_2 = (dl**2)/12 * np.cos(phi)**2 * \
            (5 - t**2 + 9*ni2 + 4*ni2**2)
        xgk_part_3 = dl**4/360 * \
            np.cos(phi)**4 * (61 - 58*t**2 + t**4 + 270*ni2 - 330*ni2*t**2)
        xgk = sig + xgk_part_1 * (1 + xgk_part_2 + xgk_part_3)

        ygk_part_1 = dl * n * np.cos(phi)
        ygk_part_2 = (dl ** 2) / 6 * np.cos(phi) ** 2 * (1 - t ** 2 + ni2)
        ygk_part_3 = (dl ** 4) / 120 * np.cos(phi) ** 4 * \
            (5 - 18 * t ** 2 + t ** 4 + 14 * ni2 - 58 * ni2 * t ** 2)
        ygk = ygk_part_1 * (1 + ygk_part_2 + ygk_part_3)

        pas = nr = 0
        for _ in range(30):
            if round(np.rad2deg(lam)/3, 0) == pas:
                nr = pas
                break
            pas += 1

        x20 = xgk * m
        y20 = ygk * m + nr * 1e6 + 5e5
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
            assert h_krasowski is not None,\
                "You didn't specify the height for the Krasowski ellipsoid"
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
        sig = a*(A0 * phi - A2 * np.sin(2*phi) + A4 *
                 np.sin(4*phi) - A6*np.sin(6*phi))
        xgk_part_1 = (dl**2)/2 * N * np.sin(phi) * np.cos(phi)
        xgk_part_2 = (dl**2)/12 * np.cos(phi)**2 * \
            (5 - t**2 + 9*ni2 + 4*ni2**2)
        xgk_part_3 = dl**4/360 * \
            np.cos(phi)**4 * (61 - 58*t**2 + t**4 + 270*ni2 - 330*ni2*t**2)
        xgk = sig + xgk_part_1 * (1 + xgk_part_2 + xgk_part_3)

        ygk_part_1 = dl * N * np.cos(phi)
        ygk_part_2 = (dl ** 2) / 6 * np.cos(phi) ** 2 * (1 - t ** 2 + ni2)
        ygk_part_3 = (dl ** 4) / 120 * np.cos(phi) ** 4 * \
            (5 - 18 * t ** 2 + t ** 4 + 14 * ni2 - 58 * ni2 * t ** 2)
        ygk = ygk_part_1 * (1 + ygk_part_2 + ygk_part_3)
        x92 = xgk * m92 - 5300000
        y92 = ygk * m92 + 500000
        return (x92, y92)


def from_file_to_file(elipsoid, args_function_title: str, file_title: str, function):
    """
    Funkcja przelicza współrzędne podane w pliku wejściowym na współrzędne w wybranym przez
    użytkownika układzie. W wyniku działania zwraca plik, który w
    kolejnych wierszach ma zapisane wyniki transformacji dla danych w tym samym wierszu
    w pliku wejściowym
    """
    assert args_function_title is not None,\
        "You didn't specify the name of functionction you want to use"
    assert file_title is not None,\
        """you didn't specify the name of the file from
which you would like to transport the coordinates"""
    if args_function_title in ("hirvonen", "xyz_kras_2_xyz_grs80", "flh_2_xyz"):
        input_nr = 3
        return_nr = 3
    elif args_function_title == "neu":
        input_nr = 6
        return_nr = 1
    elif args_function_title in ("fl_2_1992", "fl_2_2000"):
        if elipsoid.elipsoid_name == "Krasowski":
            input_nr = 4
            return_nr = 2
        else:
            input_nr = 3
            return_nr = 2
    else:
        input_nr = 0
        return_nr = 0

    results = []
    with open(file_title, "r", encoding="UTF-8") as file:
        data = []
        for wiersz in file.readlines():
            wsp = wiersz.replace("\n", "").replace(" ", "").split(";")
            data.append(wsp)
    for list in data:
        params = [float(value) for value in list]
        assert len(params) == input_nr,\
            f"""You didn't provide enough parameters,
you should enter {input_nr} values separated by a semicolon in each line of the file"""
        results.append(function(*params))
    with open("results.txt", "w") as file:
        file.write('\n'.join('%s '*return_nr % x for x in results))


def argparse_data():
    """
    Funkcja ta pozwala na uruchomienie skryptu z wiersza poleceń. Można
    przekonwertować wiele współrzędnych z pliku do innego układu współrzędnych,
    ale także przeliczyć pojedynycze współrzędne wpisując ich wartość "z palca"
    """
    parser = argparse.ArgumentParser(
        description="The program converts coordinates between coordinate systems")
    parser.add_argument("elipsoid", default="GRS80",
                        choices=["WGS84", "GRS80", "Krasowski"],
                        help="Enter elipsoid type. Chose from WGS84, GRS80 or Krasowski")
    parser.add_argument("--open_file", "-o", nargs="?", default=None,
                        help="If you want to enter coordinates in file specify file tittle")

    parser.add_argument("--file_functions", "-ff",
                        choices=["hirvonen", "flh_2_xyz", "neu",
                                 "fl_2_1992", "fl_2_2000", "xyz_kras_2_xyz_grs80"],
                        help="""use it only with open_file to specify,
    how do you want to transform coordinates giwen in file""")

    parser.add_argument("--hirvonen", "-hirv", nargs="*", type=float, default=None, help="""
    Program transforms coordinates from x,y,z to phi, lambda, height""")

    parser.add_argument("--flh_2_xyz", "-fx", nargs="*", type=float, default=None, help="""
    Program transforms coordinates from phi, lambda to xyz""")

    parser.add_argument("--neu", "-n", nargs="*", type=float, default=None, help="""
    Program transforms coordinates based on receiver coordinates (x,y,z)
    and satellite's x,y,z  to neu (topocentric coordinates)""")

    parser.add_argument("--fl_2_1992", "-92", nargs="*", type=float, help="""
    Program transforms coordinates from phi,
    lambda to x, y in 1992 coordinate. If elipsoid GRS80 or WGS84 is chosen
    enter phi, lam and prime meridian,
    if you chose Krasowski elipsoid you need to add height at the end""")

    parser.add_argument("--fl_2_2000", "-20", nargs="*",
                        type=float, help="""
    Program transforms coordinates from phi,
    lambda to x, y in 2000 coordinate. If elipsoid GRS80 or WGS84 is chosen
    enter phi, lam and prime meridian,
    if you chose Krasowski elipsoid you need to add height at the end""")

    parser.add_argument("--xyz_kras_2_xyz_grs80", "-kg", nargs="*",
                        type=float, help=""" Program transforms coordinates
    x,y,z from Krasowski elipsoid to x,y,z on GRS80 elipsoid.
    Before chosing this method make sure you entered Krasowski as elipsoid name""")
    args = parser.parse_args()
    elipsoid = Transformations(args.elipsoid)
    if args.file_functions and args.open_file is not None:
        file_title = args.open_file
        args_function_title = args.file_functions
        names = dict(zip(["hirvonen", "flh_2_xyz", "neu", "fl_2_1992",
                         "fl_2_2000", "xyz_kras_2_xyz_grs80"],
                         [elipsoid.hirvonen, elipsoid.flh_2_xyz,
                         elipsoid.neu, elipsoid.fl_2_1992, elipsoid.fl_2_2000,
                         elipsoid.xyz_kras_2_xyz_grs80]))

        from_file_to_file(elipsoid,
                          args_function_title, file_title, names[args_function_title])

    if args.fl_2_1992:
        print(elipsoid.fl_2_1992(*args.fl_2_1992))
    if args.fl_2_2000:
        print(elipsoid.fl_2_2000(*args.fl_2_2000))
    if args.flh_2_xyz:
        print(elipsoid.fl_2_1992(*args.fl_2_xyz))
    if args.hirvonen:
        print(elipsoid.fl_2_1992(*args.hirvonen))
    if args.neu:
        print(elipsoid.fl_2_1992(*args.neu))
    if args.xyz_kras_2_xyz_grs80:
        print(elipsoid.fl_2_1992(*args.xyz_kras_2_xyz_grs80))


if __name__ == "__main__":
    argparse_data()
