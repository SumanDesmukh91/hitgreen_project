import streamlit as st
import csv
import os

# ==========================================
# CONFIG
# ==========================================

st.set_page_config(
    page_title="HIT Green Housing",
    page_icon="🏢",
    layout="wide"
)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.csv")
RESIDENTS_FILE = os.path.join(DATA_DIR, "residents.csv")

# ==========================================
# CREATE FILES
# ==========================================

def create_file(file_name, headers):

    if not os.path.exists(file_name):
        with open(
            file_name,
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

# Create default admin

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

        csv.writer(f).writerow(
            [
                "admin",
                "admin123",
                "Admin",
                ""
            ]
        )

# ==========================================
# HELPERS
# ==========================================

def read_csv(file_name):

    if not os.path.exists(file_name):
        return []

    rows = []

    with open(
        file_name,
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:
            rows.append(row)

    return rows


def append_csv(file_name, row):

    with open(
        file_name,
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        csv.writer(f).writerow(row)


def save_csv(file_name, data, headers):

    with open(
        file_name,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=headers
        )

        writer.writeheader()
        writer.writerows(data)

# ==========================================
# SESSION
# ==========================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.flatno = ""

# ==========================================
# LOGIN
# ==========================================

if not st.session_state.logged_in:

    st.title("🏢 HIT Green Housing")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        users = read_csv(USERS_FILE)

        valid = False

        for user in users:

            if (
                user["username"] == username
                and user["password"] == password
            ):

                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.role = user["role"]
                st.session_state.flatno = user["flatno"]

                valid = True

                st.rerun()

        if not valid:
            st.error("Invalid Credentials")

    st.stop()

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("🏢 HIT Green Housing")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard",
        "Residents"
    ]
)

st.sidebar.write(
    f"👤 {st.session_state.username}"
)

st.sidebar.write(
    f"🔐 {st.session_state.role}"
)

if st.sidebar.button("Logout"):

    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.flatno = ""

    st.rerun()

# ==========================================
# DASHBOARD
# ==========================================

if menu == "Dashboard":

    residents = read_csv(
        RESIDENTS_FILE
    )

    total_flats = 80
    occupied = len(residents)
    vacant = total_flats - occupied

    st.title("📊 Dashboard")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Flats",
        total_flats
    )

    c2.metric(
        "Occupied",
        occupied
    )

    c3.metric(
        "Vacant",
        vacant
    )

    st.info(
        f"Logged in as {st.session_state.username} ({st.session_state.role})"
    )

# ==========================================
# RESIDENTS
# ==========================================

elif menu == "Residents":

    st.title("👨 Residents")

    if st.session_state.role in [
        "Admin",
        "Committee"
    ]:

        with st.expander(
            "Add Resident"
        ):

            flat = st.text_input(
                "Flat Number"
            )

            owner = st.text_input(
                "Owner Name"
            )

            mobile = st.text_input(
                "Mobile"
            )

            email = st.text_input(
                "Email"
            )

            if st.button(
                "Save Resident"
            ):

                append_csv(
                    RESIDENTS_FILE,
                    [
                        flat,
                        owner,
                        mobile,
                        email
                    ]
                )

                st.success(
                    "Resident Added"
                )

                st.rerun()

    residents = read_csv(
        RESIDENTS_FILE
    )

    for row in residents:

        with st.container():

            c1, c2, c3 = st.columns(
                [4, 4, 1]
            )

            with c1:

                st.write(
                    f"🏠 {row['FlatNo']}"
                )

                st.write(
                    row["OwnerName"]
                )

            with c2:

                st.write(
                    row["Mobile"]
                )

                st.write(
                    row["Email"]
                )

            if (
                st.session_state.role
                == "Admin"
            ):

                with c3:

                    if st.button(
                        "Delete",
                        key=row["FlatNo"]
                    ):

                        all_rows = read_csv(
                            RESIDENTS_FILE
                        )

                        all_rows = [
                            x
                            for x in all_rows
                            if x["FlatNo"]
                            != row["FlatNo"]
                        ]

                        save_csv(
                            RESIDENTS_FILE,
                            all_rows,
                            [
                                "FlatNo",
                                "OwnerName",
                                "Mobile",
                                "Email"
                            ]
                        )

                        st.success(
                            "Deleted"
                        )

                        st.rerun()

            st.divider()
