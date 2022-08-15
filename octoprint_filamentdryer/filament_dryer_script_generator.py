"""
Generates a gcode file to set your 3D printer's bed or enclosure temperature to a
fixed temperature for a set amount of time in order to dry spools of filament.
"""

from datetime import datetime

__author__ = """Kestin Goforth"""
__email__ = "kgoforth1503@gmail.com"
__version__ = "0.1.0"
__copyright__ = "Copyright 2022"
__license__ = "AGPLv3"
__scriptname__ = "Filament Dryer Gcode Script Generator"
__url__ = "https://github.com/kforth/Filament-Dryer-GCode-Scripts"

CHIRPS = (
    (60, 100),  # 60Hz 100ms
    (60, 125),  # 60Hz 100ms
    (60, 150),  # 60Hz 100ms
)

DEFAULT_COMMANDS = {
    "bed_set": "M140 S%d; Set target bed temperature",
    "chamber_set": "M141 S%d; Set target chamber temperature",
    "bed_wait": "M190 S%d; Wait for target bed temperature",
    "chamber_wait": "M191 S%d; Wait for target chamber temperfature",
    "dwell": "G4 S%d",
    "chirp": "M300 S%d P%d ; Chirp",
    "message": "M117 %s",
    "progress": "M73 P%d R%d",
}


def create_file(filename, time, temperature, use_bed, use_chamber):
    """
    Generates a gcode file to set your 3D printer's bed or enclosure temperature to a
    fixed temperature for a set amount of time in order to dry spools of filament.

    Args:
        filename (str): Output filename.
        time (int): Drying time, in minutes.
        temperature (int): Drying temperature, in degrees Celsius.
        use_bed (bool, optional): Use the bed heater. Defaults to False.
        use_chamber (bool, optional): Use the chamber heater. Defaults to False.
    """
    with open(filename, "wb+") as handle:
        _ = create_script(handle, time, temperature, use_bed, use_chamber)


def create_script(
    handle,
    time,
    temperature,
    use_bed=False,
    use_chamber=False,
    encoding="utf-8",
    newline="\n",
    cmds=DEFAULT_COMMANDS,
):
    """
    Writes a gcode script to the provided BytesIO-like stream.

    The script sets your 3D printer's bed or enclosure temperature to a fixed
    temperature for a set amount of time in order to dry spools of filament.

    Args:
        handle (BytesIO): Output output stream handle.
        time (int): Drying time, in minutes.
        temperature (int): Drying temperature, in degrees Celsius.
        use_bed (bool, optional): Use the bed heater. Defaults to False.
        use_chamber (bool, optional): Use the chamber heater. Defaults to False.
        encoding (str, optional): Encoding for string. Defaults to encoding.

    Returns:
        handle (BytesIO): The output stream handle.
        num_bytes (int): Number of bytes written
    """
    if not use_chamber and not use_bed:
        raise Exception("Must enable either bed or chamber.")

    num_bytes = 0

    def write(*lines, newline=newline):
        text = newline.join([e for e in lines if e is not None]).encode(encoding)
        text += newline.encode(encoding)
        handle.write(text)
        return len(text)

    # Write header info
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    num_bytes += write(
        f"; generated by [{__scriptname__}]({__url__})",
        f"; {__copyright__}  {__author__}",
        f"; version: {__version__}, date: {date_str}",
        "; ".join(
            (
                "",
                f"temp: {temperature:d} C",
                f"time: {time:d} mins",
                f"use_bed: {use_bed!r}",
                f"use_chamber: {use_chamber!r}",
            )
        ),
        "",
    )

    # Set target temperatures
    num_bytes += write(
        cmds["message"] % "Heating",
        cmds["chirp"] % CHIRPS[0],
        (cmds["bed_set"] % temperature) if use_bed else None,
        (cmds["chamber_set"] % temperature) if use_chamber else None,
        (cmds["bed_wait"] % temperature) if use_bed else None,
        (cmds["chamber_wait"] % temperature) if use_chamber else None,
        cmds["chirp"] % CHIRPS[0],
        cmds["chirp"] % CHIRPS[1],
        "",
    )

    # Dwell until target time has elapsed
    total_mins = 0
    while total_mins < time:
        remaining = time - total_mins
        if remaining <= 5 or total_mins % 5 == 0:
            progress = int(100.0 * total_mins / time)
            num_bytes += write(
                cmds["progress"] % (progress, remaining),
                cmds["message"] % ("Drying: %d mins Remaining" % remaining),
            )
        num_bytes += write(cmds["dwell"] % 60)  # Wait 60 seconds
        total_mins += 1

    # Chirp and set message
    num_bytes += write(
        cmds["progress"] % (100, 0),
        cmds["message"] % "Drying Done",
        "",
        cmds["chirp"] % CHIRPS[0],
        cmds["chirp"] % CHIRPS[1],
        cmds["chirp"] % CHIRPS[2],
        (cmds["bed_set"] % 0) if use_bed else None,
        (cmds["chamber_set"] % 0) if use_chamber else None,
        "",
    )

    return handle, num_bytes


def main():
    import argparse
    import os

    """
    Generates a gcode file to set your 3D printer's bed or enclosure temperature to a
    fixed temperature for a set amount of time in order to dry spools of filament.
    """

    parser = argparse.ArgumentParser(
        prog="filament_dryer_script_generator", description=__doc__
    )

    parser.add_argument("filename", type=str, help="(str) output filename")
    parser.add_argument("time", type=int, help="(int) drying time, in minutes")
    parser.add_argument(
        "temperature",
        type=int,
        help="(int) drying temperature, in degrees Celsius",
    )
    parser.add_argument(
        "--bed", action="store_true", help="use the bed heater for drying"
    )
    parser.add_argument(
        "--chamber", action="store_true", help="use the chamber heater for drying"
    )

    args = parser.parse_args()

    print("Generating Dryer Script")
    print("  File:    %s" % os.path.split(args.filename)[1])
    print("  Time:    %d mins" % args.time)
    print("  Temp:    %d deg C" % args.temperature)
    print("  Bed:     %r" % args.bed)
    print("  Chamber: %r" % args.chamber)

    create_file(args.filename, args.time, args.temperature, args.bed, args.chamber)

    print("Done.")


if __name__ == "__main__":
    import sys

    sys.exit(main())  # pragma: no cover
