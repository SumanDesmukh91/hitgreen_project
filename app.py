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
MAINT_FILE = os.path.join(DATA_DIR, "maintenance.csv")

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
    MAINT_FILE,
    [
        "FlatNo",
        "Month",
        "Year",
        "AmountPaid",
        "VoucherNo",
        "PaymentDate",
        "Status"
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
        "Residents",
        "Maintenance",
        "Defaulters Report"
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

    maintenance = read_csv(MAINT_FILE)

    collection = sum(
    float(x["AmountPaid"] or 0)
    for x in maintenance
    )

    c1, c2, c3, c4 = st.columns(4)

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
    
    c4.metric(
        "Collection",
        f"₹ {collection:,.0f}"
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
# ==================================================
# MAINTENANCE
# ==================================================

elif menu == "Maintenance":

    st.title("💰 Maintenance Management")

    if st.session_state.role in [
        "Admin",
        "Committee"
    ]:

        with st.expander(
            "➕ Add Maintenance Payment"
        ):

            residents = read_csv(
                RESIDENTS_FILE
            )

            flat_list = sorted(
                [
                    x["FlatNo"]
                    for x in residents
                ]
            )

            flat = st.selectbox(
                "Flat Number",
                flat_list
                if flat_list
                else ["No Flats"]
            )

            col1, col2 = st.columns(2)

            with col1:

                month = st.selectbox(
                    "Month",
                    [
                        "January",
                        "February",
                        "March",
                        "April",
                        "May",
                        "June",
                        "July",
                        "August",
                        "September",
                        "October",
                        "November",
                        "December"
                    ]
                )

            with col2:

                year = st.number_input(
                    "Year",
                    value=2026,
                    step=1
                )

            amount = st.number_input(
                "Amount Paid",
                min_value=0.0,
                value=1200.0
            )

            voucher = st.text_input(
                "Voucher Number"
            )

            status = st.selectbox(
                "Status",
                [
                    "Paid",
                    "Pending"
                ]
            )

            if st.button(
                "Save Maintenance"
            ):

                append_csv(
                    MAINT_FILE,
                    [
                        flat,
                        month,
                        year,
                        amount,
                        voucher,
                        pd.Timestamp.now().strftime(
                            "%d-%m-%Y"
                        ),
                        status
                    ]
                )

                st.success(
                    "Maintenance Saved Successfully"
                )

                st.rerun()

    st.subheader(
        "📋 Maintenance Records"
    )

    maintenance = read_csv(
        MAINT_FILE
    )

    if maintenance:

        df = pd.DataFrame(
            maintenance
        )

        search = st.text_input(
            "🔍 Search Flat"
        )

        if search:

            df = df[
                df["FlatNo"]
                .astype(str)
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        total_collection = (
            pd.to_numeric(
                df["AmountPaid"],
                errors="coerce"
            )
            .fillna(0)
            .sum()
        )

        st.metric(
            "Total Collection",
            f"₹ {total_collection:,.0f}"
        )

    else:

        st.info(
            "No maintenance records found."
        )
# ==================================================
# DEFAULTERS REPORT
# ==================================================

elif menu == "Defaulters Report":

    st.title("⚠️ Defaulters Report")

    MONTHLY_MAINTENANCE = 1200

    residents = read_csv(RESIDENTS_FILE)
    maintenance = read_csv(MAINT_FILE)

    current_month = pd.Timestamp.now().month
    current_year = pd.Timestamp.now().year

    months_to_check = []

    # Last 2 months only

    for i in range(1, 3):

        month_num = current_month - i
        year_num = current_year

        if month_num <= 0:
            month_num += 12
            year_num -= 1

        month_name = pd.Timestamp(
            year=year_num,
            month=month_num,
            day=1
        ).strftime("%B")

        months_to_check.append(
            (
                month_name,
                str(year_num)
            )
        )

    defaulters = []

    for resident in residents:

        flat = resident["FlatNo"]

        due_months = []

        for month_name, year_name in months_to_check:

            payment_found = any(

                rec["FlatNo"] == flat and
                rec["Month"] == month_name and
                str(rec["Year"]) == year_name and
                rec["Status"] == "Paid"

                for rec in maintenance

            )

            if not payment_found:

                due_months.append(
                    f"{month_name}-{year_name}"
                )

        if due_months:

            due_amount = (
                len(due_months)
                * MONTHLY_MAINTENANCE
            )

            defaulters.append(
                {
                    "FlatNo": flat,
                    "OwnerName": resident["OwnerName"],
                    "Due Months": ", ".join(
                        due_months
                    ),
                    "Due Count": len(
                        due_months
                    ),
                    "Due Amount": due_amount
                }
            )

    if defaulters:

        df = pd.DataFrame(
            defaulters
        )

        total_due = (
            df["Due Amount"]
            .sum()
        )

        total_defaulters = len(df)

        c1, c2 = st.columns(2)

        c1.metric(
            "Defaulter Flats",
            total_defaulters
        )

        c2.metric(
            "Total Outstanding",
            f"₹ {total_due:,.0f}"
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        if st.button(
            "Download Defaulters CSV"
        ):

            csv_data = df.to_csv(
                index=False
            )

            st.download_button(
                label="Download Report",
                data=csv_data,
                file_name="defaulters_report.csv",
                mime="text/csv"
            )

    else:

        st.success(
            "✅ No Defaulters Found"
        )
