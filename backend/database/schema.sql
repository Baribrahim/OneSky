drop database if exists oneskyv1; 

create database oneskyv1;

use oneskyv1;

create table User
	(
	ID int primary key auto_increment,
	Email varchar(100) not null,
	Password varchar(100) not null,
	FirstName varchar(100) not null,
	LastName varchar(100) not null
	);

create table Cause
	(
    ID int primary key auto_increment,
    Name varchar(255) not null,
    Description varchar(1000) not null
    );
    
create table `Event`
	(
    ID int primary key auto_increment,
    CauseID int,
    Foreign Key(CauseID) references Cause(ID),
    Title varchar(255) not null,
    About varchar(2000) not null,
    Activities varchar(2000) not null,
    Requirements varchar(2000) not null,
    Schedule varchar(2000) not null,
    ExpectedImpact varchar(2000) not null,
    Date date not null,
    StartTime time not null,
    EndTime time not null,
    Duration time not null,
    LocationCity varchar(255) not null,
    LocationPostcode varchar(10) not null,
    Address varchar(255) not null,
    Capacity int not null
    );
    
Create table Tag
	(
    ID int primary key auto_increment,
    TagName varchar(255) not null
    );
    
create table CauseTag
	(
    TagID int,
    Foreign Key(TagID) references Tag(ID),
    CauseID int,
    Foreign Key(CauseID) references Cause(ID)
    );
    
create table EventRegistration
	(
    ID int primary key auto_increment,
    EventID int,
    Foreign Key(EventID) references Event(ID),
    UserID int,
    Foreign Key(UserID) references User(ID)
    );
    
-- INSERTING values for DB functionality testing purposes [THIS CAN BE IGNORED/DELETED]

INSERT INTO Cause (Name, Description) VALUES
("Environment", "Activities related to protecting and improving the environment"),
("Charity", "Supporting local communities with resources and aid"),
("Community", "Projects that bring people together to improve neighborhoods"),
("Elderly Care", "Supporting elderly citizens with companionship and activities"),
("Education", "Workshops and programs that promote learning"),
("Food Security", "Providing food and nutrition support to those in need"),
("Sustainability", "Long-term solutions for greener communities");

insert into Event (CauseID, Title, About, Activities, Requirements, Schedule, ExpectedImpact, Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address, Capacity)
values (7, "Tree Planting Drive", "Join us to plant trees in the community park.", "Tree planting, soil preparation", "Bring gloves, water bottle", "Morning shift", "Greener community spaces", "2025-10-15", "09:00:00", "12:00:00", "03:00:00", "London", "E1 6AN", "Community Park, Main Street", 50),
(3, "Community Clean-Up", "Join volunteers in making local streets cleaner and safer.", "Litter collection, recycling sorting, graffiti removal.", "Wear gloves and comfortable shoes; bring reusable bags.", "Morning shift: 09:00–12:00.", "A cleaner neighborhood and increased awareness of waste management.", "2025-10-30", "09:00:00", "12:00:00", "03:00:00", "London", "N1 4HR", "Shoreditch Park, London", 40),
(6, "Food Bank Drive", "Help sort and distribute food donations to families in need.", "Sorting donations, packaging parcels, assisting visitors.", "Respect safety guidelines, be able to lift light boxes.", "Afternoon shift: 13:00–17:00.", "Support for low-income families and reduction in food waste.", "2025-11-05", "13:00:00", "17:00:00", "04:00:00","London", "E2 7JD", "East End Community Centre", 25),
(1, "Tree Planting & Nature Walk", "Celebrate green spaces by planting trees and learning about local wildlife.", "Tree planting, guided eco-walk, soil preparation.", "Bring water bottle, wear outdoor clothes and sturdy shoes.", "Morning + Afternoon sessions.", "Improved biodiversity and greener community areas.", "2025-11-09", "10:00:00", "15:00:00", "05:00:00", "London", "SE10 8RS", "Greenwich Park", 60),
(5, "Youth Coding Workshop", "Support local teens in learning the basics of programming.", "Intro to Python, teamwork challenges, project presentations.", "Basic computer literacy, willingness to help students.", "Evening workshop series.", "Empowerment of youth through digital literacy.", "2025-11-20", "17:30:00", "20:30:00", "03:00:00", "London", "W2 5HS", "Paddington Library, London", 20),
(2, "Clothing Donation Sorting", "Assist in sorting and organizing donated clothes for shelters.", "Sorting, folding, labeling items, helping staff load vehicles.", "Ability to stand for a few hours, attention to detail.", "Morning shift.", "Better distribution of resources to homeless communities.", "2025-12-02", "09:30:00", "12:30:00", "03:00:00", "London", "SW1A 2AB", "Victoria Community Hub", 35),
(4, "Senior Companionship Day", "Spend quality time with elderly residents in care homes.", "Conversations, games, reading, light assistance.", "Friendly attitude, patience, and willingness to engage.", "Afternoon visit.", "Reduce loneliness and increase happiness for seniors.", "2025-12-10", "14:00:00", "17:00:00", "03:00:00", "London", "NW8 6AA", "St John’s Care Home, London", 15)
;

-- Query Code for Search Functionality BY DATE (A SPECIFIC DATE)
SELECT 
	e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime, e.LocationCity, e.Address, e.Capacity, c.Name AS CauseName
FROM Event e
JOIN Cause c ON e.CauseID = c.ID
WHERE e.Date = '2025-10-15';

-- Query Code for Search Functionality BY DATE (WITHIN A DATE RANGE)
SELECT 
    e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime, e.LocationCity, e.Address, e.Capacity,
    c.Name AS CauseName
FROM Event e
JOIN Cause c ON e.CauseID = c.ID
WHERE e.Date BETWEEN '2025-10-01' AND '2025-10-31'
ORDER BY e.Date, e.StartTime;

-- Query Code for Search Functionality BY LOCATION (SINGLE CITY)
SELECT
	E.ID, E.Title, E.Date, E.StartTime, E.EndTime, E.LocationCity, E.Address, C.Name AS CauseName
FROM Event E
JOIN Cause C ON E.CauseID = C.ID
WHERE E.LocationCity = "London";

-- Query Code for Search Functionality BY LOCATION (MULTIPLE CITIES)
SELECT
	E.ID, E.Title, E.Date, E.StartTime, E.EndTime, E.LocationCity, E.Address, C.Name AS CauseName
FROM Event E
JOIN Cause C ON E.CauseID = C.ID
WHERE E.LocationCity IN ("London", "Southampton", "Portsmouth", "Leeds", "Livingston", "Birmingham", "Bristol");

-- Query Code for Filtering (?) BY LOCATION & DATE
SELECT 
    e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime, e.LocationCity, e.Address, e.Capacity, c.Name AS CauseName
FROM Event e
JOIN Cause c ON e.CauseID = c.ID
WHERE e.Date = '2025-10-15' AND e.LocationCity = 'London';

-- Query Code for Searching for ALL UPCOMING EVENTS
SELECT
	e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime, e.LocationCity, e.Address, e.Capacity, c.Name AS CauseName
FROM Event e
JOIN Cause c ON e.CauseID = C.ID
WHERE e.Date >= CURDATE()
ORDER BY e.Date ASC, e.StartTime ASC;

-- IGNORE
SELECT *
FROM Event, Cause

