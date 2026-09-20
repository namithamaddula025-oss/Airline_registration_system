import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

DB_FILE = "airline.db"

def connect_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Passengers (
            PassengerID INTEGER PRIMARY KEY AUTOINCREMENT,
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL,
            Gender TEXT,
            Age INTEGER,
            Phone TEXT,
            Email TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Flights (
            FlightID INTEGER PRIMARY KEY AUTOINCREMENT,
            FlightName TEXT NOT NULL,
            Source TEXT NOT NULL,
            Destination TEXT NOT NULL,
            DepartureTime TEXT,
            ArrivalTime TEXT,
            Price REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Staff (
            StaffID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Role TEXT,
            Phone TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Bookings (
            BookingID INTEGER PRIMARY KEY AUTOINCREMENT,
            PassengerID INTEGER NOT NULL,
            FlightID INTEGER NOT NULL,
            BookingDate TEXT DEFAULT CURRENT_TIMESTAMP,
            SeatNumber TEXT,
            FOREIGN KEY (PassengerID) REFERENCES Passengers(PassengerID),
            FOREIGN KEY (FlightID) REFERENCES Flights(FlightID)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Payments (
            PaymentID INTEGER PRIMARY KEY AUTOINCREMENT,
            BookingID INTEGER NOT NULL,
            Amount REAL,
            PaymentDate TEXT DEFAULT CURRENT_TIMESTAMP,
            PaymentMethod TEXT,
            FOREIGN KEY (BookingID) REFERENCES Bookings(BookingID)
        )
    """)

    # Add sample data only on first run
    if cur.execute("SELECT COUNT(*) FROM Passengers").fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO Passengers
            (FirstName, LastName, Gender, Age, Phone, Email)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("John", "Doe", "Male", 30, "9876543210", "john@example.com"))

    if cur.execute("SELECT COUNT(*) FROM Flights").fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO Flights
            (FlightName, Source, Destination, DepartureTime, ArrivalTime, Price)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("Air India 101", "Delhi", "Mumbai",
              "2026-04-01 10:00", "2026-04-01 12:00", 5000))

    if cur.execute("SELECT COUNT(*) FROM Staff").fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO Staff (Name, Role, Phone)
            VALUES (?, ?, ?)
        """, ("Ravi Kumar", "Pilot", "9123456789"))

    if cur.execute("SELECT COUNT(*) FROM Bookings").fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO Bookings (PassengerID, FlightID, SeatNumber)
            VALUES (1, 1, 'A1')
        """)

    if cur.execute("SELECT COUNT(*) FROM Payments").fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO Payments (BookingID, Amount, PaymentMethod)
            VALUES (1, 5000, 'Card')
        """)

    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="Airline Registration System", page_icon="✈️", layout="wide")
st.title("✈️ Airline Registration System")


menu = ["Passengers", "Flights", "Bookings", "Payments", "Dashboard"]
choice = st.sidebar.radio("Navigation", menu)

conn = connect_db()

if choice == "Passengers":
    st.header("👤 Passenger Management")
    tab1, tab2 = st.tabs(["Add Passenger", "View Passengers"])

    with tab1:
        fname = st.text_input("First Name")
        lname = st.text_input("Last Name")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.number_input("Age", 1, 100, 18)
        phone = st.text_input("Phone")
        email = st.text_input("Email")

        if st.button("Add Passenger"):
            if not fname.strip() or not lname.strip():
                st.error("First Name and Last Name are required.")
            else:
                try:
                    conn.execute("""
                        INSERT INTO Passengers
                        (FirstName, LastName, Gender, Age, Phone, Email)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (fname, lname, gender, age, phone, email))
                    conn.commit()
                    st.success("✅ Passenger Added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding passenger: {e}")

    with tab2:
        df = pd.read_sql_query("SELECT * FROM Passengers", conn)
        st.dataframe(df, use_container_width=True)

elif choice == "Flights":
    st.header("✈️ Flight Management")
    tab1, tab2 = st.tabs(["Add Flight", "View Flights"])

    with tab1:
        fname = st.text_input("Flight Name")
        src = st.text_input("Source")
        dest = st.text_input("Destination")
        dep_date = st.date_input("Departure Date")
        dep_time = st.time_input("Departure Time")
        arr_date = st.date_input("Arrival Date")
        arr_time = st.time_input("Arrival Time")
        price = st.number_input("Price", min_value=0.0, step=100.0)

        if st.button("Add Flight"):
            if not fname.strip() or not src.strip() or not dest.strip():
                st.error("Flight Name, Source and Destination are required.")
            else:
                dep = datetime.combine(dep_date, dep_time).strftime("%Y-%m-%d %H:%M")
                arr = datetime.combine(arr_date, arr_time).strftime("%Y-%m-%d %H:%M")
                try:
                    conn.execute("""
                        INSERT INTO Flights
                        (FlightName, Source, Destination, DepartureTime, ArrivalTime, Price)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (fname, src, dest, dep, arr, price))
                    conn.commit()
                    st.success("✅ Flight Added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding flight: {e}")

    with tab2:
        df = pd.read_sql_query("SELECT * FROM Flights", conn)
        st.dataframe(df, use_container_width=True)

elif choice == "Bookings":
    st.header("📘 Booking Management")
    tab1, tab2 = st.tabs(["Book Ticket", "View Bookings"])

    with tab1:
        passengers = pd.read_sql_query(
            "SELECT PassengerID, FirstName, LastName FROM Passengers", conn)
        flights = pd.read_sql_query(
            "SELECT FlightID, FlightName FROM Flights", conn)

        if passengers.empty or flights.empty:
            st.warning("Add at least one passenger and one flight first.")
        else:
            passenger_options = {
                f"{r.PassengerID} - {r.FirstName} {r.LastName}": int(r.PassengerID)
                for r in passengers.itertuples()
            }
            flight_options = {
                f"{r.FlightID} - {r.FlightName}": int(r.FlightID)
                for r in flights.itertuples()
            }

            p_label = st.selectbox("Select Passenger", list(passenger_options.keys()))
            f_label = st.selectbox("Select Flight", list(flight_options.keys()))
            seat = st.text_input("Seat Number")

            if st.button("Book"):
                try:
                    conn.execute("""
                        INSERT INTO Bookings (PassengerID, FlightID, SeatNumber)
                        VALUES (?, ?, ?)
                    """, (passenger_options[p_label], flight_options[f_label], seat))
                    conn.commit()
                    st.success("✅ Booking Confirmed!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error booking ticket: {e}")

    with tab2:
        df = pd.read_sql_query("""
            SELECT B.BookingID, P.FirstName, P.LastName,
                   F.FlightName, F.Source, F.Destination,
                   B.SeatNumber, B.BookingDate
            FROM Bookings B
            JOIN Passengers P ON B.PassengerID = P.PassengerID
            JOIN Flights F ON B.FlightID = F.FlightID
            ORDER BY B.BookingID DESC
        """, conn)
        st.dataframe(df, use_container_width=True)

elif choice == "Payments":
    st.header("💳 Payment Management")
    tab1, tab2 = st.tabs(["Make Payment", "View Payments"])

    with tab1:
        bookings = pd.read_sql_query("""
            SELECT B.BookingID, P.FirstName, F.FlightName
            FROM Bookings B
            JOIN Passengers P ON B.PassengerID = P.PassengerID
            JOIN Flights F ON B.FlightID = F.FlightID
        """, conn)

        if bookings.empty:
            st.warning("Create a booking first.")
        else:
            booking_options = {
                f"Booking {r.BookingID} - {r.FirstName} - {r.FlightName}": int(r.BookingID)
                for r in bookings.itertuples()
            }
            label = st.selectbox("Booking", list(booking_options.keys()))
            amount = st.number_input("Amount", min_value=0.0, step=100.0)
            method = st.selectbox("Payment Method", ["Cash", "Card", "UPI"])

            if st.button("Pay"):
                try:
                    conn.execute("""
                        INSERT INTO Payments (BookingID, Amount, PaymentMethod)
                        VALUES (?, ?, ?)
                    """, (booking_options[label], amount, method))
                    conn.commit()
                    st.success("✅ Payment Done!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing payment: {e}")

    with tab2:
        df = pd.read_sql_query("""
            SELECT Pay.PaymentID, Pay.BookingID,
                   P.FirstName, F.FlightName,
                   Pay.Amount, Pay.PaymentDate, Pay.PaymentMethod
            FROM Payments Pay
            JOIN Bookings B ON Pay.BookingID = B.BookingID
            JOIN Passengers P ON B.PassengerID = P.PassengerID
            JOIN Flights F ON B.FlightID = F.FlightID
            ORDER BY Pay.PaymentID DESC
        """, conn)
        st.dataframe(df, use_container_width=True)

elif choice == "Dashboard":
    st.header("📊 Dashboard")

    col1, col2, col3 = st.columns(3)
    passengers_count = conn.execute("SELECT COUNT(*) FROM Passengers").fetchone()[0]
    flights_count = conn.execute("SELECT COUNT(*) FROM Flights").fetchone()[0]
    bookings_count = conn.execute("SELECT COUNT(*) FROM Bookings").fetchone()[0]

    col1.metric("Passengers", passengers_count)
    col2.metric("Flights", flights_count)
    col3.metric("Bookings", bookings_count)

    st.subheader("Recent Bookings")
    df = pd.read_sql_query("""
        SELECT B.BookingID, P.FirstName, P.LastName, F.FlightName,
               B.SeatNumber, B.BookingDate
        FROM Bookings B
        JOIN Passengers P ON B.PassengerID = P.PassengerID
        JOIN Flights F ON B.FlightID = F.FlightID
        ORDER BY B.BookingID DESC
        LIMIT 5
    """, conn)
    st.dataframe(df, use_container_width=True)

conn.close()
