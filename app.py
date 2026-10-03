import streamlit as st
import pandas as pd
import csv
import os

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="HIT Green Housing",
    page_icon="🏢",
    layout="wide"
)

# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

div[data-testid="stMetric"]{
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# PATHS
# ==================================================

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.csv")
RESIDENTS_FILE = os.path.join(DATA_DIR, "residents.csv")

# ==================================================
# CREATE FILES
# ==================================================

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

# ==================================================
# HELPERS
# ==================================================

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

        writer = csv.writer(f)
        writer.writerow(row)


def save_csv(file_name, rows, headers):

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
        writer.writerows(rows)

# ==================================================
# SESSION
# ==================================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.flatno = ""

# ==================================================
# LOGIN
# ==================================================

if not st.session_state.logged_in:

    st.title("🏢 HIT Green Housing")

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        users = read_csv(
            USERS_FILE
        )

        for user in users:

            if (
                user["username"] == username
                and user["password"] == password
            ):

                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.role = user["role"]
                st.session_state.flatno = user["flatno"]

                st.rerun()

        st.error("Invalid Credentials")

    st.stop()

# ==================================================
# SIDEBAR
# ==================================================

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

# ==================================================
# DASHBOARD
# ==================================================

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

# ==================================================
# RESIDENTS
# ==================================================

elif menu == "Residents":

    st.title("👨 Resident Directory")

    # ------------------------------------------
    # Add Resident
    # ------------------------------------------

    if st.session_state.role in [
        "Admin",
        "Committee"
    ]:

        with st.expander("➕ Add Resident"):

            col1, col2 = st.columns(2)

            with col1:

                flat = st.text_input(
                    "Flat Number"
                )

                owner = st.text_input(
                    "Owner Name"
                )

                tenant = st.text_input(
                    "Tenant Name"
                )

            with col2:

                garage = st.text_input(
                    "Garage Number"
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
                        tenant,
                        garage,
                        mobile,
                        email
                    ]
                )

                st.success(
                    "Resident Added Successfully"
                )

                st.rerun()

    # ------------------------------------------
    # Display Residents
    # ------------------------------------------

    residents = read_csv(
        RESIDENTS_FILE
    )

    if residents:

        df = pd.DataFrame(residents)

        st.subheader(
            "Resident Directory"
        )

        search = st.text_input(
            "🔍 Search Flat / Owner / Tenant"
        )

        if search:

            df = df[
                df.astype(str)
                  .apply(
                      lambda row:
                      row.str.contains(
                          search,
                          case=False,
                          na=False
                      )
                  )
                  .any(axis=1)
            ]

        st.dataframe(
           df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "FlatNo": "🏠 Flat No",
                "OwnerName": "👤 Owner Name",
                "TenantName": "👨‍👩‍👧 Tenant Name",
                "GarageNo": "🚗 Garage No",
                "Mobile": "📱 Mobile",
                "Email": "📧 Email"
            }
        )

        # --------------------------------------
        # Delete Resident
        # --------------------------------------

        if st.session_state.role == "Admin":

            st.divider()

            st.subheader(
                "🗑 Delete Resident"
            )

            flat_to_delete = st.selectbox(
                "Select Flat",
                df["FlatNo"].tolist()
            )

            if st.button(
                "Delete Resident"
            ):

                all_rows = read_csv(
                    RESIDENTS_FILE
                )

                all_rows = [
                    row
                    for row in all_rows
                    if row["FlatNo"]
                    != flat_to_delete
                ]

                save_csv(
                    RESIDENTS_FILE,
                    all_rows,
                    [
                        "FlatNo",
                        "OwnerName",
                        "TenantName",
                        "GarageNo",
                        "Mobile",
                        "Email"
                    ]
                )

                st.success(
                    f"{flat_to_delete} deleted successfully"
                )

                st.rerun()

    else:

        st.info(
            "No residents found."
        )

        # ==========================================
        # DELETE
        # ==========================================

        if (
            st.session_state.role
            == "Admin"
        ):

            st.subheader(
                "🗑 Delete Resident"
            )

            flat_to_delete = st.selectbox(
                "Select Flat",
                df["FlatNo"].tolist()
            )

            if st.button(
                "Delete Resident"
            ):

                all_rows = read_csv(
                    RESIDENTS_FILE
                )

                all_rows = [
                    row
                    for row in all_rows
                    if row["FlatNo"]
                    != flat_to_delete
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
                    f"{flat_to_delete} deleted successfully"
                )

                st.rerun()
