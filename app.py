from nicegui import ui
import csv
import os

# =====================================================
# CONFIG
# =====================================================

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = "users.csv"
RESIDENTS_FILE = "residents.csv"

# =====================================================
# CREATE FILES
# =====================================================

def create_file(filename, headers):

    if not os.path.exists(filename):

        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)
            writer.writerow(headers)


create_file(
    USERS_FILE,
    [
        "username",
        "password",
        "role",
        "flatno"
    ]
)

create_file(
    RESIDENTS_FILE,
    [
        "FlatNo",
        "OwnerName",
        "Mobile",
        "Email"
    ]
)

# Default Admin

with open(
    USERS_FILE,
    "r",
    encoding="utf-8"
) as f:

    rows = list(csv.reader(f))

if len(rows) == 1:

    with open(
        USERS_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "admin",
                "admin123",
                "Admin",
                ""
            ]
        )

# =====================================================
# HELPERS
# =====================================================

def read_csv(filename):

    data = []

    with open(
        filename,
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:
            data.append(row)

    return data


def append_csv(filename, row):

    with open(
        filename,
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)
        writer.writerow(row)


def save_csv(filename, rows, headers):

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=headers
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(row)

# =====================================================
# SESSION
# =====================================================

CURRENT_USER = {
    "username": "",
    "role": "",
    "flatno": ""
}

content = ui.column().classes("w-full")

# =====================================================
# DASHBOARD
# =====================================================

def show_dashboard():

    content.clear()

    with content:

        ui.label(
            "🏢 HIT Green Housing Dashboard"
        ).classes(
            "text-h4 text-primary"
        )

        residents = read_csv(
            RESIDENTS_FILE
        )

        total_flats = 80

        occupied = len(residents)

        vacant = total_flats - occupied

        with ui.row():

            with ui.card().classes("w-56"):
                ui.label("Total Flats")
                ui.label(
                    str(total_flats)
                ).classes(
                    "text-h5"
                )

            with ui.card().classes("w-56"):
                ui.label("Occupied")
                ui.label(
                    str(occupied)
                ).classes(
                    "text-h5"
                )

            with ui.card().classes("w-56"):
                ui.label("Vacant")
                ui.label(
                    str(vacant)
                ).classes(
                    "text-h5"
                )

        ui.separator()

        ui.label(
            f"Logged in as: {CURRENT_USER['username']} ({CURRENT_USER['role']})"
        )

# =====================================================
# RESIDENTS
# =====================================================

def show_residents():

    content.clear()

    with content:

        ui.label(
            "👨 Residents"
        ).classes(
            "text-h4"
        )

        if CURRENT_USER["role"] in [
            "Admin",
            "Committee"
        ]:

            flat = ui.input(
                "Flat Number"
            )

            owner = ui.input(
                "Owner Name"
            )

            mobile = ui.input(
                "Mobile"
            )

            email = ui.input(
                "Email"
            )

            def save_resident():

                append_csv(
                    RESIDENTS_FILE,
                    [
                        flat.value,
                        owner.value,
                        mobile.value,
                        email.value
                    ]
                )

                ui.notify(
                    "Resident Added"
                )

                show_residents()

            ui.button(
                "Add Resident",
                on_click=save_resident
            )

            ui.separator()

        residents = read_csv(
            RESIDENTS_FILE
        )

        if CURRENT_USER["role"] == "Resident":

            residents = [
                r
                for r in residents
                if r["FlatNo"]
                == CURRENT_USER["flatno"]
            ]

        for row in residents:

            with ui.card().classes(
                "w-full"
            ):

                ui.label(
                    f"🏠 {row['FlatNo']}"
                ).classes(
                    "text-weight-bold"
                )

                ui.label(
                    f"Owner: {row['OwnerName']}"
                )

                ui.label(
                   f"Mobile: {row['Mobile']}"
                )

                ui.label(
                    f"Email: {row['Email']}"
                )

                if CURRENT_USER["role"] == "Admin":

                    def delete_resident(
                        flat_no=row["FlatNo"]
                    ):

                        data = read_csv(
                            RESIDENTS_FILE
                        )

                        remaining = [
                            x
                            for x in data
                            if x["FlatNo"]
                            != flat_no
                        ]

                        save_csv(
                            RESIDENTS_FILE,
                            remaining,
                            [
                                "FlatNo",
                                "OwnerName",
                                "Mobile",
                                "Email"
                            ]
                        )

                        ui.notify(
                            "Resident Deleted"
                        )

                        show_residents()

                    ui.button(
                        "Delete",
                        color="red",
                        on_click=delete_resident
                    )

# =====================================================
# LOGIN SCREEN
# =====================================================

def login_page():

    ui.label(
        "🏢 HIT Green Housing"
    ).classes(
        "text-h3"
    )

    username = ui.input(
        "Username"
    )

    password = ui.input(
        "Password",
        password=True
    )

    def login():

        users = read_csv(
            USERS_FILE
        )

        for user in users:

            if (
                user["username"]
                == username.value
                and user["password"]
                == password.value
            ):

                CURRENT_USER["username"] = user[
                    "username"
                ]

                CURRENT_USER["role"] = user[
                    "role"
                ]

                CURRENT_USER["flatno"] = user[
                    "flatno"
                ]

                build_ui()

                ui.notify(
                    "Login Successful"
                )

                return

        ui.notify(
            "Invalid Credentials",
            color="negative"
        )

    ui.button(
        "Login",
        on_click=login
    )

# =====================================================
# MAIN UI
# =====================================================

def build_main_page():

    if CURRENT_USER["role"] == "":
        login_page()
        return

    with ui.left_drawer().classes(
        "bg-blue-700 text-white"
    ):

        ui.label(
            "🏢 HIT Green Housing"
        )

        ui.button(
            "Dashboard",
            on_click=show_dashboard
        )

        ui.button(
            "Residents",
            on_click=show_residents
        )

        def logout():

            CURRENT_USER["username"] = ""
            CURRENT_USER["role"] = ""
            CURRENT_USER["flatno"] = ""

            ui.navigate.reload()

        ui.button(
            "Logout",
            color="red",
            on_click=logout
        )

    global content
    content = ui.column().classes("w-full")

    show_dashboard()

# =====================================================
# START
# =====================================================
build_main_page()

ui.run(
    title="HIT Green Housing",
    reload=False
)
