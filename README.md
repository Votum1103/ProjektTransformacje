# ProjektTransformacje
## Opis
Projekt ten został stworzony do transformacji współrzędnych pomiędzy układami. Skrypt napisano w języku Python. 
Została w nim zaimplementowana klasa Transformations w której znajdują się poszczególne metody transformujące podane współrzędne do wskazanego przez użytkownika układu.
Program umożliwia konwertowanie współrzędnych z następujących elipsoid: **GRS80, WGS84, Krasowskiego**.

<span style="color:red">Ważne!</span>

**Wszystkie wartości kątowe wpisywane jako argumenty funkcji muszą by podane w stopniach dziesiętnych (z częścią ułamkową po kropce)**

## Metody
```mermaid
graph LR
A[degrees] -->|degrees_2_dms| B[dms]
E[x,y,z] -->|hirvonen| F[φ,λ,h]
G[φ,λ,h] -->|flh_2_xyz| H[x,y,z]
I[x,y,z odbiornika x,y,z staelity] -->|neu| J[n,e,u]
K[φ,λ] -->|fl_2_xygk| L[x,y G-K]
M[φ,λ] -->|fl_2_2000| N[x,y PL2000]
O[φ,λ] -->|fl_2_1992| P[x,y PL1992]
```
## Opis funcji oraz ich wywołania z użyciem argparse

### <span style="color:green">**degrees_2_dms**</span>

Funkcja zamienia wartość w stopniach na wartość w stopniach, minutach i sekundach i zwraca ją jako str: deg°min'sec"

| Funkcja 	| degrees_2_dms 	|
|---	|---	|
| liczba <br>argumentów 	| 1 	|
| argumenty 	| degrees 	|
| wywołanie z pliku 	| \<elipsoida\> -o \<plik\> -ff degrees_2_dms -cd \<numer kolumny\> <br><br>flaga -cd jest opcjonalna, gdy nie zostanie dodana funkcja<br> zamieni wszystkie wartości w pliku 	|
| wywołanie w cmd 	| \<elipsoida\> -dd  \<kąt w stopniach\> 	|


**Przykładowe wywołanie:**
```bash
python transformacje.py grs80 -o dane.txt -ff degrees_2_dms
```
Program na podstawie danych z podanego pliku (dane.txt)
utworzy plik results.txt, w którym w każdym wierszu będą oddzielone
od siebie średnikiem kąty w postaci deg°min'sec" (tak jak w pliku wejściowym). Rodzaj elipsoidy nie ma w tym przypadku znaczenia (można wpisac 'wgs84', 'krasowski' lub 'grs80' i wynik działania funkcji będzie taki sam).

```bash
python transformacje.py grs80 -dd 50.4565676
```
Program zamieni podaną wartośc i zwróci w konsoli w postaci:
```bash
50°27'23.64336"
```

### <span style="color:green">**hirvonen**</span>

Przelicza współrzędne prostokątne x,y,z do geodezyjnych φ, λ, h. Transformacja zwraca wynik w radianach postaci: (φ, λ, h)
| Funkcja 	| hirvonen 	|
|---	|---	|
| liczba <br>argumentów 	| 3 	|
| argumenty 	| x,y,z 	|
| wywołanie z pliku 	| \<elipsoida\> -o \<plik\> -ff hirvonen  	|
| wywołanie w cmd 	| \<elipsoida\> -hv  \<x\> \<y\> \<z\> 	|

**Przykładowe wywołanie:**
```bash
python transformacje.py grs80 -o dane.txt -ff hirvonen
```
Program na podstawie danych z podanego pliku (dane.txt) współrzędnych
x; y; z utworzy plik results.txt, w którym w każdym wierszu będą oddzielone od siebie średnikiem współrzędne phi ; lam; h 

```bash
python transformacje.py grs80 -hv 3655270.000 1030180.000 5107530.000
```
Program zwróci phi, lam, h w konsoli. Wartości kątowe są w stopniach dziesiętnych:
```bash
(53.55170961404108, 15.73965028282246, 337.3694756710902)
```

### <span style="color:green">**flh_2_xyz**</span>

Funkcja zamienia współrzędne geodezyjne φ, λ, h na współrzędne prostokątne X,Y,Z. Jest to transformacja odwrotna do Hirvonena. Wynik w postaci: (X,Y,Z)

| Funkcja 	| flh_2_xyz 	|
|---	|---	|
| liczba <br>argumentów 	| 3 	|
| argumenty 	| phi, lam, h 	|
| wywołanie z pliku 	| \<elipsoida\> -o \<plik\> -ff flh_2_xyz  	|
| wywołanie w cmd 	| \<elipsoida\> -fx  \<phi\> \<lam\> \<h\> 	|

**Przykładowe wywołanie:**
```bash
python transformacje.py grs80 -o dane.txt -ff flh_2_xyz
```
Program na podstawie danych z podanego pliku (dane.txt) współrzędnych
phi; lam; h utworzy plik results.txt, w którym w każdym wierszu będą oddzielone od siebie średnikiem współrzędne x; y; z

```bash
python transformacje.py grs80 -fx 53.55170961404108 15.73965028282246 337.369476
```
Program zwróci x,y,z w konsoli w postaci:
```bash
(3655270.0000161408, 1030180.000004549, 5107530.000022553)
```
### <span style="color:green">**neu**</span>

Transformuje współrzędne geocentryczne odbiornika do współrzędnych topocentrycznych n, e, u na podstawie współrzędnych x,y,z odbiornika i satelitów. Zwraca wynik w postaci: (n,e,u)

| Funkcja 	| neu 	|
|---	|---	|
| liczba <br>argumentów 	| 6 	|
| argumenty 	| x_odb, y_odb, z_odb, x_sat, y_sat, z_sat 	|
| wywołanie z pliku 	| \<elipsoida\> -o \<plik\> -ff neu  	|
| wywołanie w cmd 	| \<elipsoida\> -n  \<x_odb\> \<y_odb\> \<z_odb\> \<x_sat\> \<y_sat\> \<z_sat\> 	|

**Przykładowe wywołanie:**
```bash
python transformacje.py grs80 -o dane.txt -ff neu
```
Program na podstawie danych z podanego pliku (dane.txt) współrzędnych
x_odb, y_odb, z_odb, x_sat, y_sat, z_sat utworzy plik results.txt, w którym w każdym wierszu będą oddzielone od siebie średnikiem współrzędne n; e; u

```bash
python transformacje.py grs80 -n 3685825.7022625906 1378073.761327304 5002882.146444101 9785596.195556305 14216408.132039897 20399414.041585404 
```
Program zwróci n,e,u w konsoli w postaci:
```bash
(1433804.6566615142, 9889126.110578151, 18418268.45441226)
```
### <span style="color:green">**fl_2_xygk**</span>

Funkcja przelicza współrzędne geodezyjne φ, λ na współrzędne geocentryczne w układzie Gaussa-Krügera. Przy wyborze elipsoidy Krasowskiego należy podać h_krasowskiego. Południk osiowy l0 należy podać w stopniach. ynik w postaci: (X_gk,Y_gk)

| Funkcja 	| fl_2_xygk 	|
|---	|---	|
| liczba <br>argumentów 	| 3<br>dla elipsoidy Krasowskiego:<br>4 	|
| argumenty 	| phi, lam, l0<br><br>dla elipsoidy Krasowskiego:<br><br>phi, lam, l0, h 	|
| wywołanie z pliku 	| \<elipsoida\> -o \<plik\> -ff fl_2_xygk  	|
| wywołanie w cmd 	| \<elipsoida\> -gk  \<phi\> \<lam\> \<l0\><br><br>dla elipsoidy Krasowskiego:<br><br>krasowski -gk  \<phi\> \<lam\> \<l0\> \<h\>  	|

**Przykładowe wywołanie:**
```bash
python transformacje.py grs80 -o dane.txt -ff fl_2_xygk
```
Program na podstawie danych z podanego pliku (dane.txt) współrzędnych
phi;lam;l0 lub dla elipsoidy Krasowskiego: phi;lam;l0;h utworzy plik results.txt, w którym w każdym wierszu będą oddzielone od siebie średnikiem współrzędne xgk;ygk

```bash
python transformacje.py krasowski -gk 50.000373107222224 16.001741142222222 15 259.5263
```
Program zwróci xgk, ygk w konsoli w postaci:
```bash
(5541326.34611664, 71695.12555565967)
```

### <span style="color:green">**fl_2_2000**</span>

Funkcja przelicza współrzędne geodezyjne φ, λ na współrzędne geocentryczne w układzie PL-2000. Przy wyborze elipsoidy Krasowskiego należy podać h_krasowskiego. Południk osiowy l0 należy podać w stopniach. ynik w postaci: (X_2000,Y_2000)

| Funkcja 	| fl_2_2000 	|
|---	|---	|
| liczba <br>argumentów 	| 3<br>dla elipsoidy Krasowskiego:<br>4 	|
| argumenty 	| phi, lam, l0<br><br>dla elipsoidy Krasowskiego:<br><br>phi, lam, l0, h 	|
| wywołanie z pliku 	| \<elipsoida\> -o \<plik\> -ff fl_2_2000  	|
| wywołanie w cmd 	| \<elipsoida\> -20  \<phi\> \<lam\> \<l0\><br><br>dla elipsoidy Krasowskiego:<br><br>krasowski -20  \<phi\> \<lam\> \<l0\> \<h\>  	|

**Przykładowe wywołanie:**
```bash
python transformacje.py grs80 -o dane.txt -ff fl_2_2000
```
Program na podstawie danych z podanego pliku (dane.txt) współrzędnych
phi;lam;l0 lub dla elipsoidy Krasowskiego: phi;lam;l0;h utworzy plik results.txt, w którym w każdym wierszu będą oddzielone od siebie średnikiem współrzędne x20;y20

```bash
python transformacje.py krasowski -20 50.000373107222224 16.001741142222222 15 259.5263
```
Program zwróci x20, y20 w konsoli w postaci:
```bash
(5540899.663987989, 5571689.605030992)
```
### <span style="color:green">**fl_2_1992**</span>

Funkcja przelicza współrzędne geodezyjne φ, λ
na współrzędne geocentryczne w układzie PL-1992.
Przy wyborze elipsoidy Krasowskiego należy podać h_krasowskiego.
Wynik w postaci: (X_1992,Y_1992)

| Funkcja 	| fl_2_1992 	|
|---	|---	|
| liczba <br>argumentów 	| 3<br>dla elipsoidy Krasowskiego:<br>4 	|
| argumenty 	| phi, lam, l0<br><br>dla elipsoidy Krasowskiego:<br><br>phi, lam, l0, h 	|
| wywołanie z pliku 	| \<elipsoida\> -o \<plik\> -ff fl_2_1992  	|
| wywołanie w cmd 	| \<elipsoida\> -92  \<phi\> \<lam\> \<l0\><br><br>dla elipsoidy Krasowskiego:<br><br>krasowski -92  \<phi\> \<lam\> \<l0\> \<h\>  	|

**Przykładowe wywołanie:**
```bash
python transformacje.py grs80 -o dane.txt -ff fl_2_1992
```
Program na podstawie danych z podanego pliku (dane.txt) współrzędnych
phi;lam;l0 lub dla elipsoidy Krasowskiego: phi;lam;l0;h utworzy plik results.txt, w którym w każdym wierszu będą oddzielone od siebie średnikiem współrzędne x92;y92

```bash
python transformacje.py grs80 -92 53.55170961388889 15.739650283333333 19
```
Program zwróci x92, y92 w konsoli w postaci:
```bash
(636809.3247729586, 284095.1148406571)
```

## Formatowanie pliku z danymi 

<span style="color:red">Ważne!</span>

**W kolejnych linijkach w pliku wejściowym należy wpisać współrzędne oddzielone średnikami (CSV oddzielony średnikami).**

- Przykładowy wygląd pliku dla przeliczenia φ,λ,h do x,y,z dla elipsoidy GRS80 (flh_2_xyz). Dane w każdej linijce pliku muszą byc wpisane w postaci: φ;λ;h

```bash
52.45678987654;13.457898765;324.987;
45.978987567;12.078987789;302.78783;
59.87678326;10.0987877;290.87654342;
43.90;21.9878765;288.98765;
```
Plik results.txt, który powstaje w wyniku przeliczenia powyższych wartości na x,y,z: 

```bash
3788029.81191433;906482.1186637862;5034193.738700127;
4341904.223809285;929158.2440457781;4563842.549821416;
3159412.309512206;562708.0780869896;5493852.084013798;
4268559.280520176;1723559.3431196345;4400292.58979039;
```
- Przykładowy wygląd pliku dla przeliczenia wartości w stopniach na wartości w stopniach, minutach i sekundach (degrees_2_dms):

```bash
52.45678987654;13.457898765;324.987;
45.978987567;12.078987789;302.78783;
59.87678326;10.0987877;290.87654342;
43.90;21.9878765;288.98765;
```
Poniższe przeliczenie zostało wykonane tylko dla kolumny pierwszej (flaga -cd 1):

```bash
52°27'24.44356";13.457898765;324.987;
45°58'44.35524";12.078987789;302.78783;
59°52'36.41974";10.0987877;290.87654342;
43°53'60.00000";21.9878765;288.98765;
```

## Wymagania

Program można uruchomic na systemie Windows, MacOS lub Linux z zainstalowanym interpreterem python w wersji >=3.6.
Wymagane biblioteki:
- numpy 1.24.1
