from nicegui import ui
import csv
import os

# =====================================================
# CONFIG
# =====================================================

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = f"{DATA_DIR}/users.csv"
RESIDENTS_FILE = f"{DATA_DIR}/residents.csv"

CURRENT_USER = {
    'username': '',
    'role': '',
    'flatno': '',
}

# =====================================================
# FILE CREATION
# =====================================================

def create_file(file_name, headers):
    if not os.path.exists(file_name):
        with open(file_name, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(headers)

create_file(
    USERS_FILE,
    ['username', 'password', 'role', 'flatno']
)

create_file(
    RESIDENTS_FILE,
    ['FlatNo', 'OwnerName', 'Mobile', 'Email']
)

# Create default admin

with open(USERS_FILE, 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))

if len(rows) == 1:
    with open(USERS_FILE, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(
            ['admin', 'admin123', 'Admin', '']
        )

# =====================================================
# HELPERS
# =====================================================

def read_csv(file_name):

    if not os.path.exists(file_name):
        return []

    with open(
        file_name,
        newline='',
        encoding='utf-8'
    ) as f:

        return list(csv.DictReader(f))

def append_csv(file_name, row):

    with open(
        file_name,
        'a',
        newline='',
        encoding='utf-8'
    ) as f:

        csv.writer(f).writerow(row)

def save_csv(file_name, rows, headers):

    with open(
        file_name,
        'w',
        newline='',
        encoding='utf-8'
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=headers
        )

        writer.writeheader()
        writer.writerows(rows)

# =====================================================
# MAIN CONTENT AREA
# =====================================================

content = ui.column().classes('w-full')

# =====================================================
# SCREENS
# =====================================================

def show_dashboard():

    content.clear()

    residents = read_csv(
        RESIDENTS_FILE
    )

    total_flats = 80
    occupied = len(residents)
    vacant = total_flats - occupied

    with content:

        ui.label(
            '🏢 HIT Green Housing Dashboard'
        ).classes(
            'text-h4'
        )

        with ui.row():

            with ui.card().classes('w-56'):
                ui.label('Total Flats')
                ui.label(
                    str(total_flats)
                ).classes(
                    'text-h5'
                )

            with ui.card().classes('w-56'):
                ui.label('Occupied')
                ui.label(
                    str(occupied)
                ).classes(
                    'text-h5'
                )

            with ui.card().classes('w-56'):
                ui.label('Vacant')
                ui.label(
                    str(vacant)
                ).classes(
                    'text-h5'
                )

        ui.separator()

        ui.label(
            f"User : {CURRENT_USER['username']}"
        )

        ui.label(
            f"Role : {CURRENT_USER['role']}"
        )

def show_residents():

    content.clear()

    with content:

        ui.label(
            '👨 Resident Management'
        ).classes(
            'text-h4'
        )

        if CURRENT_USER['role'] in [
            'Admin',
            'Committee'
        ]:

            flat = ui.input(
                'Flat Number'
            )

            owner = ui.input(
                'Owner Name'
            )

            mobile = ui.input(
                'Mobile'
            )

            email = ui.input(
                'Email'
            )

            def add_resident():

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
                    'Resident Added'
                )

                show_residents()

            ui.button(
                'Add Resident',
                on_click=add_resident
            )

        ui.separator()

        residents = read_csv(
            RESIDENTS_FILE
        )

        if CURRENT_USER['role'] == 'Resident':

            residents= [
                r
                for r in residents
                if r['FlatNo']
                == CURRENT_USER['flatno']
            ]

        for resident in residents:

            with ui.card().classes(
                'w-full'
            ):

                ui.label(
                    resident['FlatNo']
                ).classes(
                    'text-h6'
                )

                ui.label(
                    resident['OwnerName']
                )

                ui.label(
                    resident['Mobile']
                )

                ui.label(
                    resident['Email']
                )

                if CURRENT_USER['role'] == 'Admin':

                    def delete_record(
                        flat_no=resident['FlatNo']
                    ):

                        all_rows = read_csv(
                            RESIDENTS_FILE
                        )

                        all_rows = [
                            row
                            for row in all_rows
                            if row['FlatNo']
                            != flat_no
                        ]

                        save_csv(
                            RESIDENTS_FILE,
                            all_rows,
                            [
                                'FlatNo',
                                'OwnerName',
                                'Mobile',
                                'Email'
                            ]
                        )

                        ui.notify(
                            'Deleted Successfully'
                        )

                        show_residents()

                    ui.button(
                        'Delete',
                        color='red',
                        on_click=delete_record
                    )

# =====================================================
# LOGIN
# =====================================================

def show_login():

    content.clear()

    with content:

        ui.label(
            '🏢 HIT Green Housing'
        ).classes(
            'text-h3'
        )

        username = ui.input(
            'Username'
        )

        password = ui.input(
            'Password',
            password=True
        )

        def login():

            users = read_csv(
                USERS_FILE
            )

            for user in users:

                if (
                    user['username']
                    == username.value
                    and user['password']
                    == password.value
                ):

                    CURRENT_USER[
                        'username'
                    ] = user['username']

                    CURRENT_USER[
                        'role'
                    ] = user['role']

                    CURRENT_USER[
                        'flatno'
                    ] = user['flatno']

                    ui.notify(
                        'Login Successful'
                    )

                    build_application()

                    return

            ui.notify(
                'Invalid Credentials',
                color='negative'
            )

        ui.button(
            'Login',
            on_click=login
        )

# =====================================================
# MENU
# =====================================================

drawer = None

def build_application():

    global drawer

    content.clear()

    if drawer:
        drawer.delete()

    drawer = ui.left_drawer().classes(
        'bg-blue-700 text-white'
    )

    with drawer:

        ui.label(
            '🏢 HIT Green Housing'
        )

        ui.button(
            'Dashboard',
            on_click=show_dashboard
        )

        ui.button(
            'Residents',
            on_click=show_residents
        )

        def logout():

            CURRENT_USER['username'] = ''
            CURRENT_USER['role'] = ''
            CURRENT_USER['flatno'] = ''

            if drawer:
                drawer.delete()

            show_login()

        ui.button(
            'Logout',
            color='red',
            on_click=logout
        )

    show_dashboard()

# =====================================================
# START
# =====================================================

show_login()

ui.run(
    title='HIT Green Housing',
    reload=False
)
