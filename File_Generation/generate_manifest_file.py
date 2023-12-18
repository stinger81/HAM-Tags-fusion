from tkinter import filedialog
import os
import csv
import datetime
import hashlib

STANDARD_COLORS = {
    'Novice': 'purple',
    "Advanced": "orange",
    "Technician": "red",
    "General": "blue",
    "Amateur Extra": "green"
}

LEVEL_OVERRIDES = {
    "Amateur Extra": "Extra",
}
KNOWN_LENGTHS = {
    "Novice": 30,
    "Technician": 48,
    "General": 35,
    "Advanced": 40,
    "Extra": 27
}

# my parameters
START_BUFFER = 3
LAYER_HEIGHT = 0.2
CHAR_LENGTH = 8
BASE_LAYERS = 5
LETTER_LAYERS = 3

# column numbers

COL_CALLSIGN = 2
COL_COLOR = 4
COL_LICENSE_CLASS = 3
COL_COMPLETED = 6
COL_NOTES = 5

# separated by print color
MANIFEST = {}

NOTES = []


def get_file_path():
    file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a file",
                                           filetypes=(("CSV files", "*.csv"), ("all files", "*.*")))
    return file_path


def get_save_dir():
    save_dir = filedialog.askdirectory(initialdir=os.getcwd(), title="Select a folder to save the files")
    return save_dir


def build_manifest(file_path):
    # open the file
    with open(file_path, "r") as file:
        # read the file
        file_contents = csv.reader(file)
        # skip the first line
        next(file_contents)
        # iterate through the file
        for line in file_contents:
            # get the name of the person
            if line[0] == "":
                continue
            elif line[COL_COMPLETED].upper() == "TRUE":
                continue
            # get the callsign of the person
            callsign = line[COL_CALLSIGN]
            # get the license class of the person
            license_class = line[COL_LICENSE_CLASS]
            # get the color of the person
            color = line[COL_COLOR]
            note = line[COL_NOTES]
            if color == "":
                if license_class in STANDARD_COLORS:
                    color = STANDARD_COLORS[license_class]
                else:
                    color = "black"

            if license_class in LEVEL_OVERRIDES:
                license_class = LEVEL_OVERRIDES[license_class]

            color = color.upper()
            ID = hashlib.md5(str(callsign.upper() + license_class.upper() + color.upper()).encode()).hexdigest()
            # add the person to the manifest
            if color in MANIFEST:
                if ID in MANIFEST[color]:
                    print("Duplicate TAG: " + callsign)
                    continue
                MANIFEST[color][ID] = {
                    "callsign": callsign.upper(),
                    "license_class": license_class.upper(),
                    "color": color.upper(),
                    "note":note
                }
            else:
                MANIFEST[color] = {}
                MANIFEST[color][ID] = {
                    "callsign": callsign.upper(),
                    "license_class": license_class.upper(),
                    "color": color.upper(),
                    "note":note
                }


def print_manifest():
    output = ""
    for color in MANIFEST:
        output += color + ":\n"
        for ID in MANIFEST[color]:
            output += "\t" + ID + "\n"
            for key in MANIFEST[color][ID]:
                output += "\t\t" + key + ": " + MANIFEST[color][ID][key] + "\n"
    print(output)


def generate_fusion_file():
    # get the save directory
    save_dir = get_save_dir()
    file_name = "HAM_" + datetime.datetime.now().strftime("%d_%m_%Y_%H%M%S") + ".csv"
    file_path = os.path.join(save_dir, file_name)
    # open the file
    with open(file_path, "w", newline="") as file:
        # write the header
        # HEADER = "SUB_DIR"+","
        HEADER = []
        HEADER.append("TAG.name")
        HEADER.append("callsign.text")
        HEADER.append("license_class.text")
        HEADER.append("base_height.expression")
        HEADER.append("letter_height.expression")
        HEADER.append("length.expression")
        csv.writer(file).writerow(HEADER, )

        # file.write(HEADER)
        # iterate through the manifest
        line = 2
        for color in MANIFEST:
            for ID in MANIFEST[color]:
                color = MANIFEST[color][ID]["color"].upper()
                callsign = MANIFEST[color][ID]["callsign"].upper()
                license_class = MANIFEST[color][ID]["license_class"].upper()

                name = callsign + "_" + license_class + "_" + color
                name = name.replace(" ", "_")

                base_height = BASE_LAYERS * LAYER_HEIGHT
                letter_height = LETTER_LAYERS * LAYER_HEIGHT
                length = CHAR_LENGTH * len(callsign) + START_BUFFER
                cap_class = license_class.capitalize()
                if cap_class in KNOWN_LENGTHS:
                    if length < KNOWN_LENGTHS[cap_class]:
                        length = KNOWN_LENGTHS[cap_class]

                # handle notes
                if MANIFEST[color][ID]["note"] != "":
                    note_str = ""
                    note_str += "Line " + str(line)+ " "
                    note_str += name
                    note_str += " : "
                    note_str += MANIFEST[color][ID]["note"]
                    NOTES.append(note_str)

                csv.writer(file).writerow([name, callsign, license_class, base_height, letter_height, length])
                line += 1


def display_notes():
    if len(NOTES) > 0:
        print("THERE WERE NOTES IN THIS BATCH")
        print()
        for i in NOTES:
            print(i)

if __name__ == "__main__":
    print("Select the CSV file containing the data to be processed.")
    file_path = get_file_path()
    print("File selected: " + file_path)
    build_manifest(file_path)
    print_manifest()
    generate_fusion_file()
    display_notes()

