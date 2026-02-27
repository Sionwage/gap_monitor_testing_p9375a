import numpy as np
import skrf
from skrf.media import DefinedGammaZ0, DistributedCircuit

calKitDefinitions = {
    "Keysight 85032F": {
        "male": {
            "C_0": 89.939 * 10**-15,  # F, Male Calibration Open
            "C_1": 2536.800 * 10**-27,  # F/Hz
            "C_2": -264.990 * 10**-36,  # F/Hz^2
            "C_3": 13.400 * 10**-45,  # F/Hz^3
            "L_0": 3.3998 * 10**-12,  # H, Male Short
            "L_1": -496.4808 * 10**-24,  # H/Hz
            "L_2": 34.8314 * 10**-33,  # H/Hz^2
            "L_3": -0.7847 * 10**-42,  # H/Hz^3
            "R": 50,  # ohms
            "OffsetZ_0_Open": 50,  # ohms
            "OffsetZ_0_Short": 49.992,  # ohms
            "OffsetZ_0_Load": 50,  # ohms
            "OffsetDelay_Open": 4.0856 * 10**-11,  # Sec
            "OffsetDelay_Short": 4.5955 * 10**-11,  # Sec
            "OffsetDelay_Load": 0.0,  # Sec
            "OffsetLoss_Open": 0.93,  # Gohm/Sec
            "OffsetLoss_Short": 1.087,  # Gohm/Sec
            "OffsetLoss_Load": 0,  # Gohm/Sec
            "OffsetZ_0_Thru": 50,  # ohms
            "OffsetDelay_Thru": 0,  # Sec
            "OffsetLoss_Thru": 0,  # Gohm/Sec
            "Standards": {"Open": 8, "Short": 7, "Load": 3},
        },
        "female": {
            "C_0": 89.939 * 10**-15,  # F, Male Calibration Open
            "C_1": 2536.800 * 10**-27,  # F/Hz
            "C_2": -264.990 * 10**-36,  # F/Hz^2
            "C_3": 13.400 * 10**-45,  # F/Hz^3
            "L_0": 3.3998 * 10**-12,  # H, Male Short
            "L_1": -496.4808 * 10**-24,  # H/Hz
            "L_2": 34.8314 * 10**-33,  # H/Hz^2
            "L_3": -0.7847 * 10**-42,  # H/Hz^3
            "R": 50,  # ohms
            "OffsetZ_0_Open": 50,  # ohms
            "OffsetZ_0_Short": 49.99,  # ohms
            "OffsetZ_0_Load": 50,  # ohms
            "OffsetDelay_Open": 4.1170 * 10**-11,  # Sec
            "OffsetDelay_Short": 4.5955 * 10**-11,  # Sec
            "OffsetDelay_Load": 0.0,  # Sec
            "OffsetLoss_Open": 0.93,  # Gohm/Sec
            "OffsetLoss_Short": 1.087,  # Gohm/Sec
            "OffsetLoss_Load": 0,  # Gohm/Sec
            "OffsetZ_0_Thru": 50,  # ohms
            "OffsetDelay_Thru": 0,  # Sec
            "OffsetLoss_Thru": 0,  # Gohm/Sec
            "Standards": {"Open": 2, "Short": 1, "Load": 6},
        },
        "Thru": {"Standards": {"Thru": 4}},
    },
    "Keysight 85520A": {
        "male": {
            "C_0": -0.11 * 10**-15,  # F, Male Calibration Open
            "C_1": 6 * 10**-27,  # F/Hz
            "C_2": -4.39 * 10**-36,  # F/Hz^2
            "C_3": 0.179 * 10**-45,  # F/Hz^3
            "L_0": 4.645 * 10**-12,  # H, Male Short
            "L_1": -331 * 10**-24,  # H/Hz
            "L_2": 10.8 * 10**-33,  # H/Hz^2
            "L_3": -0.12 * 10**-42,  # H/Hz^3
            "R": 50,  # ohms
            "OffsetZ_0_Open": 50,  # ohms
            "OffsetZ_0_Short": 50,  # ohms
            "OffsetZ_0_Load": 50,  # ohms
            "OffsetDelay_Open": 3.0765 * 10**-11,  # Sec
            "OffsetDelay_Short": 3.0508 * 10**-11,  # Sec
            "OffsetDelay_Load": 0.0,  # Sec
            "OffsetLoss_Open": 1.8,  # Gohm/Sec
            "OffsetLoss_Short": 1.8,  # Gohm/Sec
            "OffsetLoss_Load": 0,  # Gohm/Sec
            "OffsetZ_0_Thru": 50,  # ohms
            "OffsetDelay_Thru": 1.15888 * 10**-10,  # Sec
            "OffsetLoss_Thru": 1.8,  # Gohm/Sec
            "Standards": {"Open": 2, "Short": 1, "Load": 3},
        },
        "female": {
            "C_0": None,  # F, Male Calibration Open
            "C_1": None,  # F/Hz
            "C_2": None,  # F/Hz^2
            "C_3": None,  # F/Hz^3
            "L_0": None,  # H, Male Short
            "L_1": None,  # H/Hz
            "L_2": None,  # H/Hz^2
            "L_3": None,  # H/Hz^3
            "R": None,  # ohms
            "OffsetZ_0_Open": None,  # ohms
            "OffsetZ_0_Short": None,  # ohms
            "OffsetZ_0_Load": None,  # ohms
            "OffsetDelay_Open": None,  # Sec
            "OffsetDelay_Short": None,  # Sec
            "OffsetDelay_Load": None,  # Sec
            "OffsetLoss_Open": None,  # Gohm/Sec
            "OffsetLoss_Short": None,  # Gohm/Sec
            "OffsetLoss_Load": None,  # Gohm/Sec
            "OffsetZ_0_Thru": None,  # ohms
            "OffsetDelay_Thru": None,  # Sec
            "OffsetLoss_Thru": None,  # Gohm/Sec
            "Standards": None,
        },
        "Thru": {"Standards": {"Thru": 4}},
    },
    "Keysight 85521A": {
        "female": {
            "C_0": 3.695 * 10**-15,  # F, Male Calibration Open
            "C_1": -625.6 * 10**-27,  # F/Hz
            "C_2": -2.2 * 10**-36,  # F/Hz^2
            "C_3": 0.104 * 10**-45,  # F/Hz^3
            "L_0": -8.424 * 10**-12,  # H, Male Short
            "L_1": 2912 * 10**-24,  # H/Hz
            "L_2": -217 * 10**-33,  # H/Hz^2
            "L_3": 4.51 * 10**-42,  # H/Hz^3
            "R": 50,  # ohms
            "OffsetZ_0_Open": 50,  # ohms
            "OffsetZ_0_Short": 50,  # ohms
            "OffsetZ_0_Load": 50,  # ohms
            "OffsetDelay_Open": 3.1823 * 10**-11,  # Sec
            "OffsetDelay_Short": 3.0581 * 10**-11,  # Sec
            "OffsetDelay_Load": 0.0,  # Sec
            "OffsetLoss_Open": 1.8,  # Gohm/Sec
            "OffsetLoss_Short": 1.8,  # Gohm/Sec
            "OffsetLoss_Load": 0,  # Gohm/Sec
            "OffsetZ_0_Thru": 50,  # ohms
            "OffsetDelay_Thru": 1.15881 * 10**-10,  # Sec
            "OffsetLoss_Thru": 1.8,  # Gohm/Sec
            "Standards": {"Open": 8, "Short": 7, "Load": 3},
        },
        "male": {
            "C_0": None,  # F, Male Calibration Open
            "C_1": None,  # F/Hz
            "C_2": None,  # F/Hz^2
            "C_3": None,  # F/Hz^3
            "L_0": None,  # H, Male Short
            "L_1": None,  # H/Hz
            "L_2": None,  # H/Hz^2
            "L_3": None,  # H/Hz^3
            "R": None,  # ohms
            "OffsetZ_0_Open": None,  # ohms
            "OffsetZ_0_Short": None,  # ohms
            "OffsetZ_0_Load": None,  # ohms
            "OffsetDelay_Open": None,  # Sec
            "OffsetDelay_Short": None,  # Sec
            "OffsetDelay_Load": None,  # Sec
            "OffsetLoss_Open": None,  # Gohm/Sec
            "OffsetLoss_Short": None,  # Gohm/Sec
            "OffsetLoss_Load": None,  # Gohm/Sec
            "OffsetZ_0_Thru": None,  # ohms
            "OffsetDelay_Thru": None,  # Sec
            "OffsetLoss_Thru": None,  # Gohm/Sec
            "Standards": None,
        },
        "Thru": {"Standards": {"Thru": 4}},
    },
}


def create_ideal_cal_response(
    freq=skrf.Frequency(0.03, 6000, 1601, "MHz"),
    calkit=None,
    gender="male",
):
    if calkit is None:
        raise Exception("No Calibration Kit terms provided!")
    calKitTerms = calkit[gender]

    C_0 = calKitTerms["C_0"]
    C_1 = calKitTerms["C_1"]
    C_2 = calKitTerms["C_2"]
    C_3 = calKitTerms["C_3"]
    # Male Short
    L_0 = calKitTerms["L_0"]
    L_1 = calKitTerms["L_1"]
    L_2 = calKitTerms["L_2"]
    L_3 = calKitTerms["L_3"]

    R = calKitTerms["R"]

    OffsetZ_0_Open = calKitTerms["OffsetZ_0_Open"]
    OffsetZ_0_Short = calKitTerms["OffsetZ_0_Short"]
    OffsetZ_0_Load = calKitTerms["OffsetZ_0_Load"]
    OffsetZ_0_Thru = calKitTerms["OffsetZ_0_Thru"]

    OffsetDelay_Open = calKitTerms["OffsetDelay_Open"]
    OffsetDelay_Short = calKitTerms["OffsetDelay_Short"]
    OffsetDelay_Load = calKitTerms["OffsetDelay_Load"]
    OffsetDelay_Thru = calKitTerms["OffsetDelay_Thru"]

    OffsetLoss_Open = calKitTerms["OffsetLoss_Open"]
    OffsetLoss_Short = calKitTerms["OffsetLoss_Short"]
    OffsetLoss_Load = calKitTerms["OffsetLoss_Load"]
    OffsetLoss_Thru = calKitTerms["OffsetLoss_Thru"]

    def keysight_calkit_offset_line(freq, offset_delay, offset_loss, offset_z0, ref_z0):
        if offset_delay or offset_loss:
            r = offset_loss * offset_delay * np.sqrt(freq.f / 1e9)
            l = (offset_delay * offset_z0) + r / (2 * np.pi * freq.f)  # noqa: E741
            c = offset_delay / offset_z0
            g = 0

            medium = DistributedCircuit(
                frequency=freq, R=r, L=l, C=c, G=g, z0_port=ref_z0
            )
            offset_line = medium.line(d=1, unit="m")
            return medium, offset_line
        else:
            medium = DefinedGammaZ0(frequency=freq, z0=ref_z0)
            line = medium.line(d=0)
            return medium, line

    def keysight_calkit_open(
        freq, offset_delay, offset_loss, c0, c1, c2, c3, offset_z0, ref_z0
    ):
        # Capacitance is defined with respect to the system reference impedance ref_z0, not the
        # lossy line impedance. In scikit-rf, the return values of `shunt_capacitor()` and
        # `medium.open()` methods are (correctly) referenced to z0_port, which has been set to
        # ref_z0.
        medium, line = keysight_calkit_offset_line(
            freq, offset_delay, offset_loss, offset_z0, ref_z0
        )
        if c0 or c1 or c2 or c3:
            poly = np.poly1d([c3, c2, c1, c0])
            capacitance = medium.shunt_capacitor(poly(freq.f)) ** medium.open()
        else:
            capacitance = medium.open()
        return line**capacitance

    def keysight_calkit_short(
        freq, offset_delay, offset_loss, l0, l1, l2, l3, offset_z0, ref_z0
    ):
        # Inductance is defined with respect to the system reference impedance ref_z0, not the
        # lossy line impedance. In scikit-rf, the return values of `shunt_inductance()` and
        # `medium.short()` methods are (correctly) referenced to z0_port, which has been set to
        # ref_z0.
        medium, line = keysight_calkit_offset_line(
            freq, offset_delay, offset_loss, offset_z0, ref_z0
        )
        if l0 or l1 or l2 or l3:
            poly = np.poly1d([l3, l2, l1, l0])
            inductance = medium.inductor(poly(freq.f)) ** medium.short()
        else:
            inductance = medium.short()
        return line**inductance

    def keysight_calkit_load(
        freq, offset_delay=0, offset_loss=0, offset_z0=50, ref_z0=50
    ):
        medium, line = keysight_calkit_offset_line(
            freq, offset_delay, offset_loss, offset_z0, ref_z0
        )
        ideal_medium = DefinedGammaZ0(frequency=freq, z0=ref_z0)
        load = ideal_medium.match()
        return line**load

    def keysight_calkit_thru(
        freq, offset_delay=0, offset_loss=0, offset_z0=50, ref_z0=50
    ):
        medium, line = keysight_calkit_offset_line(
            freq, offset_delay, offset_loss, offset_z0, ref_z0
        )
        thru = medium.thru()
        return line**thru

    open_std = keysight_calkit_open(
        freq,
        offset_delay=OffsetDelay_Open,
        offset_loss=OffsetLoss_Open,
        c0=C_0,
        c1=C_1,
        c2=C_2,
        c3=C_3,
        offset_z0=OffsetZ_0_Open,
        ref_z0=R,
    )
    short_std = keysight_calkit_short(
        freq,
        offset_delay=OffsetDelay_Short,
        offset_loss=OffsetLoss_Short,
        l0=L_0,
        l1=L_1,
        l2=L_2,
        l3=L_3,
        offset_z0=OffsetZ_0_Short,
        ref_z0=R,
    )
    load_std = keysight_calkit_load(
        freq,
        offset_delay=OffsetDelay_Load,
        offset_loss=OffsetLoss_Load,
        offset_z0=OffsetZ_0_Load,
        ref_z0=R,
    )
    thru_std = keysight_calkit_thru(
        freq,
        offset_delay=OffsetDelay_Thru,
        offset_loss=OffsetLoss_Thru,
        offset_z0=OffsetZ_0_Thru,
        ref_z0=R,
    )

    for ntwk in [short_std, open_std, load_std, thru_std]:
        ntwk.renormalize(R)

    return [short_std, open_std, load_std, thru_std]
