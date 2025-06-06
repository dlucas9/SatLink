import numpy as np


# calculation of specific rain attenuation
# according to ITU-R P.838-3 (https://www.itu.int/rec/R-REC-P.838/en)

class specific_attenuation:
    # coefficients for kH, according to table 1 of ITU 838-3
    vars_kH = {"aj": [-5.33980, -0.35351, -0.23789, -0.94158],
               "bj": [-0.10008, 1.26970, 0.86036, 0.64552],
               "cj": [1.13098, 0.45400, 0.15354, 0.16817],
               "mk": -0.18961,
               "ck": 0.71147}

    # coefficients for kV, according to table 2 of ITU 838-3
    vars_kV = {"aj": [-3.80595, -3.44965, -0.39902, 0.50167],
               "bj": [0.56934, -0.22911, 0.73042, 1.07319],
               "cj": [0.81061, 0.51059, 0.11899, 0.27195],
               "mk": -0.16398,
               "ck": 0.63297}

    # coefficients for alfaH, according to table 3 of ITU 838-3
    vars_alfaH = {"aj": [-0.14318, 0.29591, 0.32177, -5.37610, 16.1721],
                  "bj": [1.82442, 0.77564, 0.63773, -0.96230, -3.29980],
                  "cj": [-0.55187, 0.19822, 0.13164, 1.47828, 3.43990],
                  "m_alfa": 0.67849,
                  "c_alfa": -1.95537}

    # coefficients for alfaV, according to table 4 of ITU 838-3
    vars_alfaV = {"aj": [-0.07771, 0.56727, -0.20238, -48.2991, 48.5833],
                  "bj": [2.33840, 0.95545, 1.14520, 0.791669, 0.791459],
                  "cj": [-0.76284, 0.54039, 0.26809, 0.116226, 0.116479],
                  "m_alfa": -0.053739,
                  "c_alfa": 0.83433}

    def eq_k(self, aj, bj, cj, mk, ck, f):
        # this function calculates kH or kV, according to equation (2) of ITU 838-3
        aj = np.array(aj)
        bj = np.array(bj)
        cj = np.array(cj)
        summation = np.sum(aj * np.exp(-(((np.log10(f) - bj) / cj) ** 2))) + mk * np.log10(f) + ck

        return 10 ** summation

    def eq_alfa(self, aj, bj, cj, m_alfa, c_alfa, f):
        # this function calculates alfaV or alfaH, according to equation (3) of ITU 838-3
        aj = np.array(aj)
        bj = np.array(bj)
        cj = np.array(cj)
        summation = np.sum(aj * np.exp(-(((np.log10(f) - bj) / cj) ** 2))) + m_alfa * np.log10(f) + c_alfa

        return summation

    def get_k(self, f, E, tau):
        # this function calculates k, according to equation (4) of ITU 838-3
        E = np.radians(E)
        tau = np.radians(tau)

        kH = self.eq_k(self.vars_kH['aj'], self.vars_kH['bj'], self.vars_kH['cj'], self.vars_kH['mk'],
                       self.vars_kH['ck'], f)
        kV = self.eq_k(self.vars_kV['aj'], self.vars_kV['bj'], self.vars_kV['cj'], self.vars_kV['mk'],
                       self.vars_kV['ck'], f)

        k = (kV + kV + (kH - kV) * (np.cos(E) ** 2) * (np.cos(2 * tau))) / 2
        return k, kV, kH

    def get_alfa(self, f, E, tau):
        # this function calculates alfa, according to equation (5) of ITU 838-3
        E = np.radians(E)
        tau = np.radians(tau)

        alfaH = self.eq_alfa(self.vars_alfaH['aj'], self.vars_alfaH['bj'], self.vars_alfaH['cj'],
                             self.vars_alfaH['m_alfa'],
                             self.vars_alfaH['c_alfa'], f)
        alfaV = self.eq_alfa(self.vars_alfaV['aj'], self.vars_alfaV['bj'], self.vars_alfaV['cj'],
                             self.vars_alfaV['m_alfa'],
                             self.vars_alfaV['c_alfa'], f)
        k, kV, kH = self.get_k(f, E, np.degrees(tau))
        alfa = ((kH * alfaH + kV * alfaV + (kH * alfaH - kV * alfaV) * (np.cos(E) ** 2) *
                 (np.cos(2 * tau))) / (2 * k))

        return alfa, alfaV, alfaH

    def get_gamaR(self, R001, f, E, tau):
        # this function calculates the specific attenuation coefficient gamaR, according to equation (1) of ITU 838
        k, _, _ = self.get_k(f, E, tau)
        alfa, _, _ = self.get_alfa(f, E, tau)
        gamaR = k * (R001) ** alfa
        return gamaR
