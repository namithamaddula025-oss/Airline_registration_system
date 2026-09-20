-- Optional reference SQL for the standalone SQLite version.
-- The application creates this database automatically, so you normally do not need to run this file.

CREATE TABLE Passengers (
    PassengerID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Gender TEXT,
    Age INTEGER,
    Phone TEXT,
    Email TEXT
);

CREATE TABLE Flights (
    FlightID INTEGER PRIMARY KEY AUTOINCREMENT,
    FlightName TEXT NOT NULL,
    Source TEXT NOT NULL,
    Destination TEXT NOT NULL,
    DepartureTime TEXT,
    ArrivalTime TEXT,
    Price REAL
);

CREATE TABLE Staff (
    StaffID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT,
    Role TEXT,
    Phone TEXT
);

CREATE TABLE Bookings (
    BookingID INTEGER PRIMARY KEY AUTOINCREMENT,
    PassengerID INTEGER NOT NULL,
    FlightID INTEGER NOT NULL,
    BookingDate TEXT DEFAULT CURRENT_TIMESTAMP,
    SeatNumber TEXT,
    FOREIGN KEY (PassengerID) REFERENCES Passengers(PassengerID),
    FOREIGN KEY (FlightID) REFERENCES Flights(FlightID)
);

CREATE TABLE Payments (
    PaymentID INTEGER PRIMARY KEY AUTOINCREMENT,
    BookingID INTEGER NOT NULL,
    Amount REAL,
    PaymentDate TEXT DEFAULT CURRENT_TIMESTAMP,
    PaymentMethod TEXT,
    FOREIGN KEY (BookingID) REFERENCES Bookings(BookingID)
);
