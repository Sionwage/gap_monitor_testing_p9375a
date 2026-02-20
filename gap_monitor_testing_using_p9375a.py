import os
import re
from datetime import datetime
from pathlib import Path
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
import skrf as rf
from calibration import calKitDefinitions, create_ideal_cal_response
from IPython.display import display
from ipywidgets.widgets import (
    Button,
    Checkbox,
    Dropdown,
    GridspecLayout,
    HBox,
    Label,
    Layout,
    Output,
    Tab,
    Text,
    VBox,
)
from keysight_p9375a import KeysightP9375A
from pyvisa import ResourceManager
from skrf import SOLT, two_port_reflect

"""
Todo List

DONE All caps for constant "FOLDERS"
TODO Import calibration script
TODO Import P9375A vna script
TODO remove E5071C vna initialization code in "create_vna"
TODO insert P9375A vna initialization code in "create_vna"
TODO Add Verification Measurements post calibration
TODO Create jupyter notebook to pair w/ this



"""


FOLDERS = [
    "calibration_measurements",
    "calibration_verification_measurements",
    "corrected_measurements",
    "plots",
    "uncorrected_measurements",
]


def list_resources():
    rm = ResourceManager("@py")
    resources = rm.list_resources()
    rm.close()
    return resources


def timestamp():
    current_date = datetime.now().strftime("%Y%m%d")
    current_time = datetime.now().strftime("%H%M%S")
    return f"{current_date}-{current_time}"


# find matching files in a directory
def list_files_matching_str(str_filter, files):
    files_re = re.compile(f"(?i).*{str_filter}.*")
    files = list(filter(files_re.match, files))
    return files


def create_folders(folders=FOLDERS):
    """
    Create basic folder structure for saving data.
    """

    # check current directory for these folders and if missing, create them
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)


def create_vna(resource_address):
    vna = KeysightP9375A(resource_address)
    return vna


def configure_vna_for_quick_sweep(vna):
    vna.emit_beep_on_warnings = False
    vna.emit_beep_on_completions = False

    vna.ch_1.IFBW = 400
    vna.ch_1.scan_points = 1601
    vna.ch_1.averaging_count = 2
    vna.ch_1.averaging_enabled = True
    vna.ch_1.auto_sweep_time_enabled = True
    vna.ch_1.correction_enabled = False
    vna.ch_1.port_1.output_power = 10
    # vna.ch_1.port_2.output_power = 0
    # couple vna port power

    vna.ch_1.start_frequency = 20e6
    vna.ch_1.stop_frequency = 250e6

    vna.ch_1.trigger_continuous = True


def configure_vna_for_testing(vna):
    vna.emit_beep_on_warnings = False
    vna.emit_beep_on_completions = False

    vna.ch_1.IFBW = 400
    vna.ch_1.scan_points = 1601
    vna.ch_1.averaging_count = 8
    vna.ch_1.averaging_enabled = True
    vna.ch_1.auto_sweep_time_enabled = True
    vna.ch_1.correction_enabled = False
    vna.ch_1.port_1.output_power = 10
    # vna.ch_1.port_2.output_power = 0
    # couple vna port power

    vna.ch_1.start_frequency = 20e6
    vna.ch_1.stop_frequency = 250e6

    vna.ch_1.trigger_continuous = True


def save_touchstone(vna, network, cal=None):
    network.comments = [
        f"Date and Time: {timestamp()}\n",
        f"VNA ID: {vna.id}",
        f"VNA ID: {vna.options}",
        f"Points: {vna.ch_1.scan_points}",
        f"Averaging Count: {vna.ch_1.averaging_count}",
        f"Averaging Enabled: {vna.ch_1.averaging_enabled}",
        f"Auto Sweep Time Enabled: {vna.ch_1.auto_sweep_time_enabled}",
        f"Correction Enabled: {vna.ch_1.correction_enabled}",
        f"Port 1 Output Power: {vna.ch_1.port_1.output_power}",
        # f"Port 2 Output Power: {vna.ch_1.port_2.output_power}",
        f"Start Frequency: {vna.ch_1.start_frequency}",
        f"Stop Frequency: {vna.ch_1.stop_frequency}",
    ]
    ports = int(len(network.port_tuples) ** 0.5)
    filename = (
        f"./uncorrected_measurements/{timestamp()}_uncorrected_{network.name}.s{ports}p"
    )
    network.write_touchstone(filename=filename)
    with open(filename, "a") as file:
        for comment in network.comments:
            file.write(f"# {comment}")

    if cal is not None:
        cal_network = cal.apply_cal(network)
        filename = filename.replace("uncorrected", "corrected")
        cal_network.write_touchstone(filename=filename)
        with open(filename, "a") as file:
            for comment in network.comments:
                file.write(f"# {comment}")
            file.write("# file corrected by scikit-rf")
            # need to write the list of files used to correct the measurement
            return cal_network

    else:
        return network


def perform_vna_sweep(vna, ports, name="", cal=None):
    """
    Gather S11 or S22 and frequency arrays from the VNA to create a Scikit-RF network.
    """

    assert ports in ["Port 1", "Port 2", "Both"]

    if ports == "Both":
        n = 2
    else:
        n = 1

    sleep(0.5)
    # create s parm array to store s parm measurements
    frequencies = vna.ch_1.sweep_frequencies

    vna.ch_1.tr_1.make_active()
    S11 = vna.ch_1.measurement_data

    assert len(S11) == len(frequencies)

    freq = rf.Frequency.from_f(np.array(frequencies), unit="Hz")
    s = np.zeros((len(frequencies), n, n), dtype=complex)
    s[:, 0, 0] = np.array(S11)

    if ports == "Both":
        vna.ch_1.tr_2.make_active()
        S21 = vna.ch_1.measurement_data

        vna.ch_1.tr_3.make_active()
        S12 = vna.ch_1.measurement_data

        vna.ch_1.tr_4.make_active()
        S22 = vna.ch_1.measurement_data

        # verify len of other three measurements are equal and match s11
        len(S21) == len(S12) == len(S22) == len(frequencies)

        # finish array plumbing
        s[:, 0, 1] = np.array(S12)
        s[:, 1, 0] = np.array(S21)
        s[:, 1, 1] = np.array(S22)

    # create network object in Scikit-RF
    network = rf.Network(frequency=freq, s=s, name=name)

    # simple beep to alert completion on measurement
    vna.emit_beep()

    return save_touchstone(vna, network, cal=cal)


def create_vna_calibration_measurement_menu(vna):
    """
    Create ipywidget menu giving proper options for naming the filename for the sweeps
    """

    # needs calkit manufacture and calkit part number
    # needs fermi asset tag
    # needs standard sn

    display(VBox([calibration_grid, cal_plot_output]))

    def perform_calibration_measurement(button, vna=vna):
        calibration_perform_measurement_button.disabled = True
        cal_plot_output.clear_output()
        name = f"{calibration_port_dropdown.value} {calibration_gender_dropdown.value} {calibration_standard_type_dropdown.value}-Calibration Measurement"

        cal_measurement = perform_vna_sweep(
            vna, ports=calibration_port_dropdown.value, name=name, cal=None
        )

        # move this measurement to the calibration measurement folder too
        ports = int(len(cal_measurement.port_tuples) ** 0.5)
        filename = (
            f"./calibration_measurements/{timestamp()}-{cal_measurement.name}.s{ports}p"
        )
        cal_measurement.write_touchstone(filename=filename)
        with open(filename, "a") as file:
            for comment in cal_measurement.comments:
                file.write(f"# {comment}")
            file.write("# Calibration Measurement")
        calibration_perform_measurement_button.disabled = False

        with cal_plot_output:
            cal_measurement.plot_s_db()

    # attach calibration measurement actions to perform_measurement_button when clicked
    calibration_perform_measurement_button.on_click(perform_calibration_measurement)


def create_one_port_corrections(cal_folder):
    cal_folder = Path(cal_folder)
    cal_files = os.listdir(cal_folder)

    assert len(cal_files) == 3

    assert len(list_files_matching_str("short", cal_files)) == 1
    assert len(list_files_matching_str("open", cal_files)) == 1
    assert len(list_files_matching_str("load", cal_files)) == 1

    port1files = list_files_matching_str("Port 1", cal_files)

    port1gender = None

    port1short = rf.Network(
        cal_folder / list_files_matching_str("short", cal_files)[0], name="short"
    )
    port1open = rf.Network(
        cal_folder / list_files_matching_str("open", cal_files)[0], name="open"
    )
    port1load = rf.Network(
        cal_folder / list_files_matching_str("load", cal_files)[0], name="load"
    )

    calibration_measurements = dict(
        port1short=port1short,
        port1open=port1open,
        port1load=port1load,
    )

    freq = calibration_measurements["port1short"].frequency

    # check they all are equal in number of points
    assert all(
        [
            len(calibration_measurements["port1short"].frequency)
            == len(sweep.frequency)
            for sweep in calibration_measurements.values()
        ]
    )

    if len(list_files_matching_str("female", port1files)) > 0:
        port1gender = "female"
    elif len(list_files_matching_str("male", port1files)) > 0:
        port1gender = "male"
    else:
        raise Exception("""Port 1 Calibration doesn't have a gender""")

    port1IdealShort, port1IdealOpen, port1IdealLoad, idealThru = (
        create_ideal_cal_response(
            freq=freq, calkit=calKitDefinitions["Keysight 85032F"], gender=port1gender
        )
    )

    port1idealResponse = [port1IdealShort, port1IdealOpen, port1IdealLoad]

    port1measuredResponse = [port1short, port1open, port1load]

    port1oneportcal = rf.OnePort(
        ideals=port1idealResponse, measured=port1measuredResponse
    )
    port1oneportcal.run()

    calibrations = {"one": port1oneportcal}

    return calibrations


def create_known_thru_corrections(cal_folder):
    # need to have this create a list of files used for performing the calibration to correct measurements
    cal_folder = Path(cal_folder)
    cal_files = os.listdir(cal_folder)

    assert len(cal_files) == 8
    assert len(list_files_matching_str("Port 1", cal_files)) == 3
    assert len(list_files_matching_str("Port 2", cal_files)) == 3
    assert len(list_files_matching_str("isolation", cal_files)) == 1
    assert len(list_files_matching_str("thru", cal_files)) == 1
    assert len(list_files_matching_str("short", cal_files)) == 2
    assert len(list_files_matching_str("open", cal_files)) == 2
    assert len(list_files_matching_str("load", cal_files)) == 2

    assert len(list_files_matching_str("unk_thru", cal_files)) == 0

    port1files = list_files_matching_str("Port 1", cal_files)
    port2files = list_files_matching_str("Port 2", cal_files)

    assert len(port1files) == 3
    assert len(list_files_matching_str("short", port1files)) == 1
    assert len(list_files_matching_str("open", port1files)) == 1
    assert len(list_files_matching_str("load", port1files)) == 1

    assert len(port2files) == 3
    assert len(list_files_matching_str("short", port2files)) == 1
    assert len(list_files_matching_str("open", port2files)) == 1
    assert len(list_files_matching_str("load", port2files)) == 1

    port1gender = None
    port2gender = None

    port1short = rf.Network(
        cal_folder / list_files_matching_str("short", port1files)[0], name="short"
    )
    port1open = rf.Network(
        cal_folder / list_files_matching_str("open", port1files)[0], name="open"
    )
    port1load = rf.Network(
        cal_folder / list_files_matching_str("load", port1files)[0], name="load"
    )

    port2short = rf.Network(
        cal_folder / list_files_matching_str("short", port2files)[0], name="short"
    )
    port2open = rf.Network(
        cal_folder / list_files_matching_str("open", port2files)[0], name="open"
    )
    port2load = rf.Network(
        cal_folder / list_files_matching_str("load", port2files)[0], name="load"
    )

    isolation = rf.Network(
        cal_folder / list_files_matching_str("isolation", cal_files)[0],
        name="isolation",
    )
    thru = rf.Network(
        cal_folder / list_files_matching_str("thru", cal_files)[0], name="known thru"
    )

    calibration_measurements = dict(
        port1short=port1short,
        port1open=port1open,
        port1load=port1load,
        port2short=port2short,
        port2open=port2open,
        port2load=port2load,
        isolation=isolation,
        thru=thru,
    )

    freq = calibration_measurements["port1short"].frequency

    # check they all are equal in number of points
    assert all(
        [
            len(calibration_measurements["port1short"].frequency)
            == len(sweep.frequency)
            for sweep in calibration_measurements.values()
        ]
    )

    if len(list_files_matching_str("female", port1files)) > 0:
        port1gender = "female"
    elif len(list_files_matching_str("male", port1files)) > 0:
        port1gender = "male"
    else:
        raise Exception("""Port 1 Calibration doesn't have a gender""")

    if len(list_files_matching_str("female", port2files)) > 0:
        port2gender = "female"
    elif len(list_files_matching_str("male", port2files)) > 0:
        port2gender = "male"
    else:
        raise Exception("""Port 2 Calibration doesn't have a gender""")

    port1IdealShort, port1IdealOpen, port1IdealLoad, idealThru = (
        create_ideal_cal_response(
            freq=freq, calkit=calKitDefinitions["Keysight 85032F"], gender=port1gender
        )
    )

    port2IdealShort, port2IdealOpen, port2IdealLoad, idealThru = (
        create_ideal_cal_response(
            freq=freq, calkit=calKitDefinitions["Keysight 85032F"], gender=port2gender
        )
    )

    port1idealResponse = [port1IdealShort, port1IdealOpen, port1IdealLoad]

    port1measuredResponse = [port1short, port1open, port1load]

    port1oneportcal = rf.OnePort(
        ideals=port1idealResponse, measured=port1measuredResponse
    )
    port1oneportcal.run()

    port2idealResponse = [port2IdealShort, port2IdealOpen, port2IdealLoad]

    port2measuredResponse = [port2short, port2open, port2load]

    port2oneportcal = rf.OnePort(
        ideals=port2idealResponse, measured=port2measuredResponse
    )
    port2oneportcal.run()

    idealsS2P = [
        two_port_reflect(port1IdealShort, port2IdealShort),
        two_port_reflect(port1IdealOpen, port2IdealOpen),
        two_port_reflect(port1IdealLoad, port2IdealLoad),
        idealThru,
    ]

    measuredS2P = [
        two_port_reflect(port1short, port2short),
        two_port_reflect(port1open, port2open),
        two_port_reflect(port1load, port2load),
        thru,
    ]

    SOLTcal = SOLT(ideals=idealsS2P, measured=measuredS2P, isolation=isolation)

    SOLTcal.run()

    terminations = {
        "forward switch term": SOLTcal.coefs_12term["forward switch term"],
        "reverse switch term": SOLTcal.coefs_12term["reverse switch term"],
    }

    calibrations = {
        "Port 1": port1oneportcal,
        "Port 2": port2oneportcal,
        "Both": SOLTcal,
        "terminations": terminations,
    }

    # need to save port terminations for unknown thru

    return calibrations


# create unknown thru calibration


# plot comparison
def plot_comparison_to_prior_unit(
    title,
    network=None,
    network_name="DUT",
    prior_network=None,
    prior_name="Prior",
    diff_name=None,
    # plot_folder='plots',
):
    assert isinstance(network, rf.Network)

    if isinstance(prior_network, type(None)):
        files = os.listdir("./corrected_measurements/")
        prior_network = rf.Network("./corrected_measurements/" / files[-2])

    if isinstance(diff_name, type(None)):
        diff_name = f"{network_name}-{prior_name}"

    assert isinstance(prior_network, rf.Network)

    plt.figure()

    # need to change this to the fermi styling
    rf.stylely()
    fig = plt.gcf()

    fig.set_figheight(8)
    fig.set_figwidth(11)
    network.frequency.unit = "MHz"
    prior_network.frequency.unit = "MHz"

    plt.subplot(221)
    network.s21.plot_s_db(label=network_name)
    prior_network.s21.plot_s_db(label=prior_name, color="red", linestyle="dotted")
    ax = plt.gca()
    ax.set_ylabel("Magnitude (dB)")

    plt.subplot(222)
    network.s21.plot_s_deg(label=network_name)
    prior_network.s21.plot_s_deg(label=prior_name, color="red", linestyle="dotted")
    ax = plt.gca()
    ax.set_ylabel(r"Phase ($\degree$)")

    plt.subplot(223)
    (network / prior_network).s21.plot_s_db(label=diff_name, color="purple")
    ax = plt.gca()
    ax.set_ylabel("Magnitude (dB)")

    plt.subplot(224)
    (network / prior_network).s21.plot_s_deg(label=diff_name, color="purple")
    ax = plt.gca()
    ax.set_ylabel(r"Phase ($\degree$)")

    fig.suptitle(title)
    plt.savefig(
        f"./plots/{timestamp()}-{network.name}vs{prior_network.name}-{title}.jpg"
    )
    plt.show()


# create perfect attenuator and phaseshift network
def create_perfect_delay_attenuator(
    freq,
    attenuation=-75.5,
    delay=2.5550314465408805e-09,
    unit="s",
    name="delay attenuator",
    Z_0=50,
    Z_L=50,
):
    """
    Create a 2 port network to represent a perfect delayline and attenuator
    by providing a skrf.Frequency object, attenuation in dB, and delay in seconds.

    This function's default values are for the Gap Monitor Amplitude and Phase responce at 53.108MHz

    args:
    freq: <skrf.Frequency> frequency object from skrf
    attenuation: <float> attenuation in dB
    delay: <float> using units defined in the "unit" arg
    unit: <str> default "s"
    name:
    Z_0:
    Z_L:

    returns:
    skrf.Network representing the delay and attenuation provided
    """

    # freq = rf.Frequency(20, 250, 1601, "MHz")
    # ntw = create_perfect_delay_attenuator(freq, -75.5, 2.5550314465408805e-09)

    # beta needed to calculate the transmission line impedance for a given distance
    beta = freq.w / rf.c

    # defining the transmission line and the perfect attenuator
    tline_media = rf.DefinedGammaZ0(freq, z0=Z_0, gamma=0 + beta * 1j)
    delay_line = tline_media.attenuator(attenuation, d=delay, unit="s", name=name)

    # the input port of the circuit is defined with the Circuit.Port method
    port1 = rf.Circuit.Port(freq, "port1", z0=Z_0)
    port2 = rf.Circuit.Port(freq, "port2", z0=Z_0)

    # connection list
    cnx = [[(port1, 0), (delay_line, 0)], [(delay_line, 1), (port2, 0)]]
    # building the circuit
    cir = rf.Circuit(cnx)

    # getting the resulting Network from the 'network' parameter:
    ntw = cir.network
    return ntw


# ipywidget menu to select calibration files

# ipywidget menu to select golden unit


# ipywidget menu to comment sweep plot and save raw touchstone and corrected touchstone
def create_dut_measurement_menu(vna, cal):
    display(dut_grid, VBox([Label(value=" \n")]), dut_plots_tab)

    def perform_gap_monitor_measurement(button):
        # disable perform button
        dut_perform_measurement_button.disabled = True

        # start countdown in parallel thread

        # clear last plot
        plot_output_1.clear_output()
        plot_output_2.clear_output()
        plot_output_3.clear_output()

        # take measurement
        name = f"Gap Monitor SN{dut_sn_text.value} - {dut_description_text.value}"
        dut_network = perform_vna_sweep(vna, name=name, ports="Both", cal=cal["Both"])

        # plot dut vs last measurement
        prior_network_file = (
            Path("./corrected_measurements/") / os.listdir("corrected_measurements")[-2]
        )
        prior_network = rf.Network(prior_network_file)
        with plot_output_2:
            plot_comparison_to_prior_unit(
                title=f"{name} vs Prior Measurement",
                network=dut_network,
                prior_network=prior_network,
            )

        # plot dut vs golden unit
        if dut_golden_unit_dropdown.value in os.listdir("./corrected_measurements/"):
            golden_network = rf.Network(
                Path("./corrected_measurements/") / dut_golden_unit_dropdown.value,
                name="Golden Unit",
            )
            with plot_output_1:
                plot_comparison_to_prior_unit(
                    title=f"{name} vs Golden Unit",
                    network=dut_network,
                    prior_network=golden_network,
                )
        with plot_output_3:
            freq = rf.Frequency(20, 250, 1601, "MHz")
            perfect_gap_network = create_perfect_delay_attenuator(freq)
            plot_comparison_to_prior_unit(
                title=f"{name} vs Perfect Gap Monitor",
                network=dut_network,
                prior_network=perfect_gap_network,
            )

        # stop countdown and update time to complete measurement
        # update dut_golden_unit_dropdown
        golden_unit_file = dut_golden_unit_dropdown.value
        dut_golden_unit_dropdown.options = os.listdir("./corrected_measurements/")
        dut_golden_unit_dropdown.value = golden_unit_file
        # enable perform button
        dut_perform_measurement_button.disabled = False

    dut_perform_measurement_button.on_click(perform_gap_monitor_measurement)


# ipywidget menu to select two sweeps and plot comparison


def initialize(device, address=17):
    # check datafolder structure or create if needed
    create_folders()

    # list resources connected, using the prologix adapter we need to use the serial
    # port the prologix is connected to which should be 'ASRLx::INSTR' where x some
    # number
    # resources = list_resources()

    # initialize the vna to use in the lines below
    vna = create_vna(resource_address=device, gpib_address=address)

    # initial configuration
    # configure_vna_for_testing(vna)

    return vna


# perform two port measurement and apply corrections
# network is a skrf.Network object with calibration applied
# network = perform_two_port_vna_sweep(vna, ports="Both", name="Test", cal=cals["both"])
# or
# perform_vna_sweep(vna, ports="Both", name="Test")

create_folders(FOLDERS)
# widget definitions for calibration measurements

# styles
header_style = dict(
    font_size="18pt",
)

# calibration widgets

calibration_measurement_label = Label("Calibration Measurements", style=header_style)

calibration_port_label = Label(value="Port: ")
calibration_port_dropdown = Dropdown(
    value="Port 1", options=["Port 1", "Port 2", "Both"]
)

calibration_gender_label = Label(value="Gender: ")
calibration_gender_dropdown = Dropdown(value="Male", options=["Male", "Female"])

calibration_standard_type_label = Label(value="Standard Type: ")
calibration_standard_type_dropdown = Dropdown(
    value="Short", options=["Short", "Open", "Load", "Thru", "Isolation"]
)

calibration_perform_measurement_label = Label(value="Perform Measurement: ")
calibration_perform_measurement_button = Button(description="Proceed")

# calibration widget layout

calibration_grid = GridspecLayout(5, 2)

calibration_grid[0, :] = calibration_measurement_label
calibration_grid[1, 0] = calibration_port_label
calibration_grid[1, 1] = calibration_port_dropdown
calibration_grid[2, 0] = calibration_gender_label
calibration_grid[2, 1] = calibration_gender_dropdown
calibration_grid[3, 0] = calibration_standard_type_label
calibration_grid[3, 1] = calibration_standard_type_dropdown
calibration_grid[4, 0] = calibration_perform_measurement_label
calibration_grid[4, 1] = calibration_perform_measurement_button

cal_plot_output = Output()

# widget definitions for calibration verification

verification_measurement_label = Label("Verfication", style=header_style)

# need to use a grid to align these
verification_port_label = Label(value="Port: ")
verification_port_dropdown = Dropdown(value="Both", options=["Both"])

verification_standard_type_label = Label(value="Standard Type: ")
verification_standard_type_dropdown = Dropdown(
    value="Isolation", options=["Thru", "Isolation"]
)

verification_perform_measurement_label = Label(
    value="Perform Verification Measurement: "
)
verification_perform_measurement_button = Button(description="Proceed")

# widget definitions for dut measurements
dut_measurement_label = Label("DUT Measurement", style=header_style)

dut_sn_label = Label(value="DUT SN:")
dut_sn_text = Text()

dut_description_label = Label(value="Test Description:")
dut_description_text = Text()

dut_golden_unit_label = Label("Select Golden Unit")
dut_golden_unit_dropdown = Dropdown()  # options=[], value=[])
dut_golden_unit_dropdown.options = os.listdir("./corrected_measurements/")
# dut_golden_unit_dropdown.value = os.listdir("./corrected_measurements/")[0]

dut_plotting_label = Label("Plot:")
dut_compare_to_golden_unit_checkbox = Checkbox(
    value=False, description="vs Golden Unit"
)
dut_compare_to_prior_checkbox = Checkbox(value=False, description="vs Prior Unit")

dut_perform_measurement_label = Label(value="Perform DUT Measurement:")
dut_perform_measurement_button = Button(description="Proceed")

# plot outputs
plot_output_1 = Output()
plot_output_2 = Output()
plot_output_3 = Output()

# tab box to hold plots
dut_plots_tab = Tab(
    children=[plot_output_1, plot_output_2, plot_output_3],
    titles=["DUT vs Golden Unit", "DUT vs Prior", "DUT"],
    layout=Layout(height="800px", width="800px"),
)

dut_grid = GridspecLayout(6, 4, width="75%")

dut_grid[0, :] = dut_measurement_label
dut_grid[1, 0] = dut_sn_label
dut_grid[1, 1:] = dut_sn_text
dut_grid[2, 0] = dut_description_label
dut_grid[2, 1:] = dut_description_text
dut_grid[3, 0] = dut_golden_unit_label
dut_grid[3, 1:] = dut_golden_unit_dropdown
dut_grid[4, 0] = dut_plotting_label
dut_grid[4, 1:] = HBox(
    [
        dut_compare_to_golden_unit_checkbox,
        dut_compare_to_prior_checkbox,
        dut_compare_to_prior_checkbox,
    ]
)
dut_grid[5, 0] = dut_perform_measurement_label
dut_grid[5, 1:] = dut_perform_measurement_button
