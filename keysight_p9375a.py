#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
from pathlib import Path

from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.generic_types import SCPIMixin

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class KeysightP9375A_Channels(Channel):
    """
    Channel implimentation for the Keysight P9375A VNA
    """

    scan_points = Instrument.control(
        "SENS{ch}:SWE:POIN?",
        "SENS{ch}:SWE:POIN %d",
        """
        Number of frequency points measured per sweep (int).
        """,
        cast=int,
    )

    # Get / Set IFBW
    IFBW = Instrument.control(
        "SENS{ch}:BAND?",
        "SENS{ch}:BAND %g",
        """
        Number of frequency points measured per sweep (int).
        """,
        cast=float,
    )

    # sweep time

    # Get / Set Averaging Count
    # SENSe<cnum>:AVERage:COUNt <num>
    averaging_count = Instrument.control(
        "SENS{ch}:AVER:COUN?",
        "SENS{ch}:AVER:COUN %d",
        """
        Number of averages (int).
        """,
        cast=int,
    )

    # Get / Set Averaging Enabled
    # SENSe<cnum>:AVERage[:STATe] <ON | OFF>
    averaging_enabled = Instrument.control(
        "SENS{ch}:AVER:STAT?",
        "SENS{ch}:AVER:STAT %d",
        """
        Averaging enabled state (bool).
        """,
        cast=bool,
    )

    # SENSe<cnum>:AVERage:MODE <char>
    averaging_mode = Instrument.control(
        "SENS{ch}:AVER:MODE?",
        "SENS{ch}:AVER:MODE %s",
        """
        Averaging mode to be used. Valid modes are "SWEEP" and "POINT" (str).
        """,
        cast=str,
    )

    # Get / Set Start and Stop Frequency
    # SENSe<cnum>:FREQuency:STARt <num>

    # Get / Set Measurement Dwell time
    # SENSe<cnum>:SWEep:DWELl <num>
    dwell_time = Instrument.control(
        "SENS{ch}:SWE:DWELL?",
        "SENS{ch}:SWE:DWELL %g",
        """
        Control the dwell time per point measurement in seconds (float).
        """,
        cast=float,
    )

    # Get S-Parameter Array
    # CALCulate<cnum>:DATA:SNP:PORTs? <"x,y,z".>[, FAST]
    # better CALCulate<cnum>:MEASure<mnum>:DATA:RAW <string>,<dataBlock>

    # Correction state
    # SENSe<cnum>:CORRection[:STATe] <ON | OFF>
    correction_enabled = Instrument.control(
        "SENS{ch}:CORR:STAT?",
        "SENS{ch}:CORR:STAT %d",
        """
        Correction enabled state (bool).
        """,
        cast=bool,
    )

    start_frequency = Instrument.control(
        "SENS{ch}:FREQ:STAR?",
        "SENS{ch}:FREQ:STAR %g",
        """
        Starting frequency of the VNA sweep in Hz (float).
        """,
        cast=float,
    )

    stop_frequency = Instrument.control(
        "SENS{ch}:FREQ:STOP?",
        "SENS{ch}:FREQ:STOP %g",
        """
        Stopping frequency of the VNA sweep in Hz (float).
        """,
        cast=float,
    )

    power = Instrument.control(
        "SOUR:POW?",
        "SOUR:POW %g",
        """
        VNA output power in dBm (float).
        """,
        cast=float,
    )

    trigger_source = Instrument.control(
        "TRIG:SOUR?",
        "TRIG:SOUR %s",
        """
        Control the triggering source of the VNA. Valid trigger sources are:

        | Trigger Source | Description                                           |
        | -------------- | ----------------------------------------------------- |
        | IMM            | Immediately trigger off the internal, free-run source |
        | EXT            | External trigger input                                |
        | BUS            | VISA bus trigger (software controlled via `*TRG`      |
        | MAN            | Manual (front panel / soft key)                       |
        """,
    )

    trigger_continuously = Instrument.control(
        "INIT:CONT?",
        "INIT:CONT %d",
        """
        Control whether the internal trigger is running continously (bool).
        """,
        cast=bool,
    )

    def save_snp_touchstone(
        self,
        *,
        remote_path: str,
        ports: str = "1,2",
        channel: int = 1,
        meas: int = 1,
        snp_format: str = "RI",  # "RI", "MA", "DB", or "AUTO"
        single_sweep: bool = True,
        fetch_to: str | Path | None = None,
        timeout_ms: int = 120_000,
    ) -> Path | None:
        """
        Save S-parameter data from the selected measurement to a Touchstone SnP file
        on the VNA PC filesystem, and optionally transfer it back to the controller.

        Parameters
        ----------
        vna:
            A PyMeasure Instrument already connected via VISA.
        remote_path:
            Full path *on the VNA controller PC*, e.g.
            r'C:\\Users\\Public\\Documents\\MyData.s2p'
        ports:
            Comma/space delimited list of ports in quotes per SCPI, e.g. "1,2" or "1,2,3,4".
        channel, meas:
            Channel and measurement index used by the SCPI command.
        snp_format:
            Sets MMEM:STORe:TRACe:FORMat:SNP (RI/MA/DB/AUTO).
        single_sweep:
            If True, disables continuous triggering and runs one sweep before saving.
            (Keysight recommends triggering a single measurement then letting the channel go to Hold
            before saving.)
        fetch_to:
            If provided, reads the saved file back using MMEM:TRANsfer? and writes it locally.
            Note: requires “Enable Remote Drive Access” in the VNA Remote Interface dialog.
        timeout_ms:
            VISA timeout for long sweeps / large point counts.

        Returns
        -------
        Path to the fetched local file if fetch_to is provided; otherwise None.
        """
        # Make long operations less likely to timeout
        visa = getattr(self.parent.adapter, "connection", self.parent.adapter)
        visa.timeout = timeout_ms

        # Optional: choose SnP data formatting (RI/MA/DB/AUTO)
        self.write(f"MMEM:STOR:TRAC:FORM:SNP {snp_format}")

        # create list of ports for the measurement being asked for
        if len(ports) == 1:
            s_parms = [f"S{ports}{ports}"]
        if len(ports) > 1:
            s_parms = ["S11", "S21", "S22", "S12"]

        # Check if the measurements are active if not displayed
        measurements = self.ask("CALCulate1:PARameter:CATalog:EXTended?")

        missing_measurements = []
        for port in s_parms:
            if port not in measurements:
                missing_measurements.append(port)

        # Activate the measurements if not in the list
        for parm in missing_measurements:
            self.write(f"CALC:PAR:DEF {parm}, {parm}")

        if single_sweep:
            # Run one sweep and wait for completion
            self.write("INIT:CONT OFF")
            self.write("INIT:IMM")
            self.ask("*OPC?")  # blocks until the sweep is complete

        # Save Touchstone file on the VNA controller PC filesystem
        # SCPI: CALCulate<cnum>:MEASure<mnum>:DATA:SNP:PORTs:SAVE "<ports>","<filename>"
        cmd = f'CALC{channel}:MEAS{meas}:DATA:SNP:PORTS:SAVE "{ports}","{remote_path}"'
        self.write(cmd)
        self.ask("*OPC?")  # Keysight recommends *OPC? for large point counts

        if fetch_to is None:
            return None

        # Transfer the file back to the controller as an IEEE definite-length binary block:
        # Query syntax: MMEMory:TRANsfer? <fileName>
        self.write(f'MMEM:TRAN? "{remote_path}"')
        raw = visa.read_raw()

        # Parse IEEE 488.2 definite-length block: b"#"<ndigits><nbytes><data...>
        if not raw.startswith(b"#"):
            raise RuntimeError(f"Unexpected transfer header: {raw[:64]!r}")

        ndigits = int(raw[1:2].decode("ascii"))
        nbytes = int(raw[2 : 2 + ndigits].decode("ascii"))
        data_start = 2 + ndigits
        data = raw[data_start : data_start + nbytes]

        fetch_to = Path(fetch_to)
        fetch_to.parent.mkdir(parents=True, exist_ok=True)
        fetch_to.write_bytes(data)
        return fetch_to


class KeysightP9375A(SCPIMixin, Instrument):
    """
    Minimum viable code to perform TDR Measurement
    """

    def __init__(self, adapter, name="VNA", **kwargs):
        super().__init__(adapter, name, **kwargs)

    channels = Instrument.MultiChannelCreator(KeysightP9375A_Channels, [1])
