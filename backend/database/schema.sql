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
    
create table Event
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
    
create table Badge (
  ID INT PRIMARY KEY AUTO_INCREMENT,
  Name VARCHAR(100) NOT NULL UNIQUE,
  Description VARCHAR(255) NOT NULL,
  IconURL VARCHAR(500)
);

create table UserBadge (
  ID INT PRIMARY KEY AUTO_INCREMENT,
  UserID INT NOT NULL,
  BadgeID INT NOT NULL,
  FOREIGN KEY (UserID) REFERENCES User(ID),
  FOREIGN KEY (BadgeID) REFERENCES Badge(ID)
);

create table Team
(
  ID int primary key auto_increment,
  Name varchar(120) not null,
  Description varchar(1000),
  Department varchar(120),
  Capacity int,
  OwnerUserID int not null,
  foreign key (OwnerUserID) references User(ID),
  JoinCode char(8) not null,
  unique (JoinCode),
  IsActive tinyint(1) not null default 1
);

create table Team
(
  ID int primary key auto_increment,
  Name varchar(120) not null,
  Description varchar(1000),
  Department varchar(120),
  Capacity int,
  OwnerUserID int not null,
  foreign key (OwnerUserID) references User(ID),
  JoinCode char(8) not null,
  unique (JoinCode),
  IsActive tinyint not null default 1
);

create table TeamMembership
	(
	ID int primary key auto_increment,
	UserID int,
    FOREIGN KEY (UserID) references User(ID),
    TeamID int,
    FOREIGN KEY (TeamID) references Team(ID)
	);
    
create table TeamEventRegistration
	(
	ID int primary key auto_increment,
	EventID int,
    FOREIGN KEY (EventID) references Event(ID),
    TeamID int,
    FOREIGN KEY (TeamID) references Team(ID)
	);

-- Dummy data for events --
   
# Insert tags
INSERT INTO Tag (TagName) VALUES
('Environment'),
('Education'),
('Community'),
('Animal Welfare'),
('Health & Well-being'),
('Disaster Relief'),
('Homelessness'),
('Mental Health'),
('Food Security'),
('STEM & Technology');

    
# Insert causes
INSERT INTO Cause (Name, Description) VALUES
('Beach Cleanup', 'A community-driven initiative to clean up local beaches and raise awareness about marine pollution.'),
('Tree Planting', 'Help restore green spaces by planting trees in local parks and communities.'),
('Food Bank Support', 'Assist in sorting, packing, and distributing food to families in need.'),
('Homeless Outreach', 'Distribute essential supplies and provide support to homeless individuals.'),
('Animal Shelter Assistance', 'Support local shelters by caring for animals and helping with adoptions.'),
('Senior Care Visits', 'Spend time with elderly individuals to provide companionship and assistance.'),
('Mental Health Awareness', 'Promote mental well-being through workshops and community outreach.'),
('STEM Mentorship', 'Guide students in science, technology, engineering, and math subjects.'),
('Blood Donation Drive', 'Organize and assist in blood donation events to save lives.'),
('Disaster Relief Aid', 'Volunteer to help communities recover from natural disasters.');


INSERT INTO CauseTag (TagID, CauseID) VALUES
-- Beach Cleanup
(1, 1), (3, 1),
-- Tree Planting
(1, 2), (3, 2),
-- Food Bank Support
(9, 3), (3, 3),
-- Homeless Outreach
(7, 4), (3, 4),
-- Animal Shelter Assistance
(4, 5), (3, 5),
-- Senior Care Visits
(5, 6), (3, 6),
-- Mental Health Awareness
(8, 7), (3, 7),
-- STEM Mentorship
(2, 8), (10, 8), (3, 8),
-- Blood Donation Drive
(5, 9), (3, 9),
-- Disaster Relief Aid
(6, 10), (3, 10);

INSERT INTO Event (CauseID, Title, About, Activities, Requirements, Schedule, ExpectedImpact, Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address, Capacity) VALUES
-- Beach Cleanup (Cause 1)
(1, 'Thames Riverside Cleanup', 'Help clean up the Thames riverbank.', 'Collect litter, sort recyclables.', 'Wear boots and gloves.', 'Meet at 9am, finish by 12pm.', 'Cleaner riverbank and improved biodiversity.', '2025-12-05', '09:00:00', '12:00:00', '03:00:00', 'London', 'E14 5HQ', 'Thames Riverside Park', 40),
(1, 'Leeds Canal Cleanup', 'Join us to clean Leeds canal paths.', 'Picking litter, recycling.', 'Comfortable walking outdoors.', 'Shift from 10am to 1pm.', 'Cleaner waterways and safer paths.', '2025-12-08', '10:00:00', '13:00:00', '03:00:00', 'Leeds', 'LS1 4AB', 'Leeds Canal Dock', 30),
(1, 'Livingston Park Cleanup', 'Help restore Livingston’s green spaces.', 'Collecting trash, planting flowers.', 'Bring gloves and water.', 'Event runs from 9am to 12pm.', 'Improved park environment.', '2025-12-12', '09:00:00', '12:00:00', '03:00:00', 'Livingston', 'EH54 6AA', 'Almondvale Park', 25),
(1, 'Edinburgh Beach Cleanup', 'Join us to clean Portobello Beach and protect marine life.', 'Collect litter, sort recyclables.', 'Wear boots and gloves.', 'Meet at 9am, finish by 12pm.', 'Cleaner beach and improved biodiversity.', '2025-12-22', '09:00:00', '12:00:00', '03:00:00', 'Edinburgh', 'EH15 1HX', 'Portobello Beach', 40),
(1, 'Riverbank Revival', 'Help clean up the Thames riverbank.', 'Collect litter, sort recyclables.', 'Wear boots and gloves.', 'Meet at 9am, finish by 12pm.', 'Cleaner riverbank and improved biodiversity.', '2025-11-05', '09:00:00', '12:00:00', '03:00:00', 'London', 'E14 5HQ', 'Thames Riverside Park', 40),
(1, 'Coastal Care Day', 'Join us to clean Portobello Beach and protect marine life.', 'Collect litter, sort recyclables.', 'Wear boots and gloves.', 'Meet at 9am, finish by 12pm.', 'Cleaner beach and improved biodiversity.', '2025-11-22', '09:00:00', '12:00:00', '03:00:00', 'Edinburgh', 'EH15 1HX', 'Portobello Beach', 40),
-- Tree Planting (Cause 2)
(2, 'London Tree Planting Day', 'Plant trees in Victoria Park.', 'Digging, planting, watering.', 'Wear sturdy shoes.', 'Meet at 10am, finish by 1pm.', 'Greener urban spaces.', '2025-12-06', '10:00:00', '13:00:00', '03:00:00', 'London', 'E3 5TB', 'Victoria Park', 35),
(2, 'Leeds Green Belt Planting', 'Help plant trees in Leeds green belt.', 'Planting saplings, mulching.', 'Outdoor work readiness.', 'Shift from 9am to 12pm.', 'Improved air quality.', '2025-12-09', '09:00:00', '12:00:00', '03:00:00', 'Leeds', 'LS6 2AB', 'Roundhay Park', 30),
(2, 'Livingston Woodland Project', 'Expand Livingston’s woodland area.', 'Planting and watering trees.', 'Bring gloves and boots.', 'Event runs from 10am to 1pm.', 'Enhanced biodiversity.', '2025-12-13', '10:00:00', '13:00:00', '03:00:00', 'Livingston', 'EH54 7AA', 'Deans Community Woodland', 25),
(2, 'Manchester Tree Planting', 'Help plant trees in local parks.', 'Digging, planting, watering.', 'Wear sturdy shoes.', 'Meet at 10am, finish by 1pm.', 'Greener urban spaces.', '2025-12-30', '10:00:00', '13:00:00', '03:00:00', 'Manchester', 'M1 2AB', 'Whitworth Park', 30),
(2, 'Roots for the Future', 'Plant trees in Victoria Park.', 'Digging, planting, watering.', 'Wear sturdy shoes.', 'Meet at 10am, finish by 1pm.', 'Greener urban spaces.', '2025-11-06', '10:00:00', '13:00:00', '03:00:00', 'London', 'E3 5TB', 'Victoria Park', 35),
(2, 'Urban Forest Day', 'Help plant trees in Leeds green belt.', 'Planting saplings, mulching.', 'Outdoor work readiness.', 'Shift from 9am to 12pm.', 'Improved air quality.', '2025-11-09', '09:00:00', '12:00:00', '03:00:00', 'Leeds', 'LS6 2AB', 'Roundhay Park', 30),
-- Food Bank Support (Cause 3)
(3, 'London Food Sorting', 'Sort and pack food donations.', 'Labeling, packing boxes.', 'Able to lift boxes.', 'Shift from 9am to 12pm.', 'Faster food distribution.', '2025-12-07', '09:00:00', '12:00:00', '03:00:00', 'London', 'E1 6AB', 'East End Food Bank', 20),
(3, 'Leeds Food Drive', 'Assist in food collection and packing.', 'Sorting, packing.', 'Organized and detail-oriented.', 'Shift from 10am to 1pm.', 'Support for families in need.', '2025-12-10', '10:00:00', '13:00:00', '03:00:00', 'Leeds', 'LS2 8AA', 'Leeds Community Kitchen', 25),
(3, 'Livingston Food Hub', 'Help distribute food parcels.', 'Packing and handing out parcels.', 'Friendly and helpful.', 'Event runs from 11am to 2pm.', 'Improved food security.', '2025-12-14', '11:00:00', '14:00:00', '03:00:00', 'Livingston', 'EH54 8AA', 'Livingston Food Hub', 20),
-- Homeless Outreach (Cause 4)
(4, 'London Winter Care Drive', 'Distribute warm clothes and blankets.', 'Packing and distribution.', 'Compassionate volunteers.', 'Shift from 12pm to 3pm.', 'Better winter safety.', '2025-12-08', '12:00:00', '15:00:00', '03:00:00', 'London', 'E2 7AB', 'Hope Shelter', 30),
(4, 'Leeds Hot Meal Service', 'Serve meals to homeless individuals.', 'Cooking, serving.', 'Basic kitchen skills.', 'Shift from 1pm to 4pm.', 'Improved nutrition.', '2025-12-11', '13:00:00', '16:00:00', '03:00:00', 'Leeds', 'LS3 1AA', 'St George’s Centre', 25),
(4, 'Livingston Care Package Prep', 'Prepare hygiene kits for distribution.', 'Sorting and packing.', 'Organized volunteers.', 'Event runs from 10am to 1pm.', 'Improved hygiene access.', '2025-12-15', '10:00:00', '13:00:00', '03:00:00', 'Livingston', 'EH54 9AA', 'Community Hall', 20),
(4, 'Birmingham Homeless Care Drive', 'Distribute care packages to homeless individuals.', 'Packing and distribution.', 'Compassionate volunteers.', 'Shift from 12pm to 3pm.', 'Improved quality of life.', '2025-12-28', '12:00:00', '15:00:00', '03:00:00', 'Birmingham', 'B1 1AA', 'Hope Shelter', 30),
-- Animal Shelter Assistance (Cause 5)
(5, 'London Pet Adoption Day', 'Assist with pet adoption event.', 'Handling pets, guiding visitors.', 'Comfortable with animals.', 'Shift from 11am to 3pm.', 'Increased adoptions.', '2025-12-09', '11:00:00', '15:00:00', '04:00:00', 'London', 'E3 4AB', 'Happy Paws Shelter', 15),
(5, 'Leeds Animal Care Day', 'Help clean and feed animals.', 'Feeding, cleaning cages.', 'Animal-friendly volunteers.', 'Shift from 9am to 12pm.', 'Better animal welfare.', '2025-12-12', '09:00:00', '12:00:00', '03:00:00', 'Leeds', 'LS4 2AA', 'Leeds Animal Rescue', 20),
(5, 'Livingston Shelter Support', 'Assist with daily shelter tasks.', 'Walking dogs, cleaning.', 'Physically active volunteers.', 'Event runs from 10am to 1pm.', 'Improved shelter operations.', '2025-12-16', '10:00:00', '13:00:00', '03:00:00', 'Livingston', 'EH54 5AA', 'Livingston Animal Centre', 15),
(5, 'Paws & Play Adoption Fair', 'Help families meet adoptable pets.', 'Guiding visitors, pet handling.', 'Comfortable with animals.', 'Shift from 11am to 3pm.', 'More pets find homes.', '2025-11-09', '11:00:00', '15:00:00', '04:00:00', 'London', 'E3 4AB', 'Happy Paws Shelter', 15),
(5, 'Furry Friends Care Day', 'Assist with feeding and cleaning.', 'Feeding, cleaning cages.', 'Animal-friendly volunteers.', 'Shift from 9am to 12pm.', 'Better animal welfare.', '2025-11-12', '09:00:00', '12:00:00', '03:00:00', 'Leeds', 'LS4 2AA', 'Leeds Animal Rescue', 20),
-- Senior Care Visits (Cause 6)
(6, 'London Senior Social', 'Spend time with elderly residents.', 'Games, reading, chatting.', 'Friendly and patient.', 'Shift from 2pm to 5pm.', 'Reduced loneliness.', '2025-12-10', '14:00:00', '17:00:00', '03:00:00', 'London', 'E5 6AB', 'Rosewood Care Home', 12),
(6, 'Leeds Music Afternoon', 'Play music for seniors.', 'Playing instruments, singing.', 'Musical skills a plus.', 'Shift from 3pm to 6pm.', 'Improved mental health.', '2025-12-13', '15:00:00', '18:00:00', '03:00:00', 'Leeds', 'LS5 3AA', 'Meadow View Care Home', 10),
(6, 'Livingston Holiday Card Day', 'Make holiday cards for seniors.', 'Crafting and delivering cards.', 'Creative volunteers.', 'Event runs from 10am to 1pm.', 'Increased happiness.', '2025-12-17', '10:00:00', '13:00:00', '03:00:00', 'Livingston', 'EH54 4AA', 'Community Arts Centre', 15),
-- Mental Health Awareness (Cause 7)
(7, 'London Mindfulness Workshop', 'Assist in mindfulness session.', 'Setting up, guiding activities.', 'Good communication skills.', 'Shift from 10am to 1pm.', 'Improved mental well-being.', '2025-12-11', '10:00:00', '13:00:00', '03:00:00', 'London', 'E6 7AB', 'Wellness Centre', 20),
(7, 'Leeds Mental Health Booth', 'Run an info booth on mental health.', 'Distributing leaflets, engaging visitors.', 'Friendly volunteers.', 'Shift from 11am to 3pm.', 'Increased awareness.', '2025-12-14', '11:00:00', '15:00:00', '04:00:00', 'Leeds', 'LS6 4AA', 'City Square', 15),
(7, 'Livingston Stress Relief Day', 'Help organize stress-relief activities.', 'Yoga setup, distributing materials.', 'Organized volunteers.', 'Event runs from 9am to 12pm.', 'Reduced stress levels.', '2025-12-18', '09:00:00', '12:00:00', '03:00:00', 'Livingston', 'EH54 3AA', 'Community Hall', 20),
-- STEM Mentorship (Cause 8)
(8, 'Code & Create', 'Teach basic coding to children.', 'Guiding Scratch exercises.', 'Basic coding knowledge.', 'Shift from 1pm to 4pm.', 'Improved digital literacy.', '2025-12-12', '13:00:00', '16:00:00', '03:00:00', 'London', 'E7 8AB', 'Tech Hub', 15),
(8, 'Build-a-Bot Challenge', 'Guide students in building robots.', 'Explaining steps, troubleshooting.', 'STEM knowledge helpful.', 'Shift from 10am to 1pm.', 'Hands-on STEM learning.', '2025-12-15', '10:00:00', '13:00:00', '03:00:00', 'Leeds', 'LS7 5AA', 'Innovation Lab', 15),
(8, 'Livingston STEM Career Talk', 'Share STEM career insights.', 'Giving talks, answering questions.', 'STEM professionals preferred.', 'Event runs from 11am to 1pm.', 'Increased STEM awareness.', '2025-12-19', '11:00:00', '13:00:00', '02:00:00', 'Livingston', 'EH54 2AA', 'Science Centre', 20),
(8, 'Edinburgh STEM Robotics Workshop', 'Teach kids to build simple robots.', 'Guiding assembly, troubleshooting.', 'Basic robotics knowledge.', 'Shift from 1pm to 4pm.', 'Hands-on STEM learning.', '2025-12-23', '13:00:00', '16:00:00', '03:00:00', 'Edinburgh', 'EH8 9YL', 'Tech Innovation Hub', 15),
-- Blood Donation Drive (Cause 9)
(9, 'Give Life London', 'Assist in organizing a blood donation event.', 'Registering donors, refreshments.', 'Friendly volunteers.', 'Shift from 9am to 1pm.', 'Increased blood supply.', '2025-12-13', '09:00:00', '13:00:00', '04:00:00', 'London', 'E8 9AB', 'City Hall', 25),
(9, 'Heroes in Leeds: Blood Drive', 'Help with donor registration.', 'Guiding donors, serving snacks.', 'Organized volunteers.', 'Shift from 10am to 2pm.', 'Life-saving donations.', '2025-12-16', '10:00:00', '14:00:00', '04:00:00', 'Leeds', 'LS8 6AA', 'Community Centre', 20),
(9, 'Livingston Lifesavers', 'Support local blood donation event.', 'Assisting staff, donor care.', 'Friendly and calm demeanor.', 'Event runs from 11am to 3pm.', 'Improved healthcare support.', '2025-12-20', '11:00:00', '15:00:00', '04:00:00', 'Livingston', 'EH54 1AA', 'Town Hall', 20),
(9, 'Birmingham Blood Donation Day', 'Assist in organizing a blood donation event.', 'Registering donors, refreshments.', 'Friendly volunteers.', 'Shift from 9am to 1pm.', 'Increased blood supply.', '2025-12-29', '09:00:00', '13:00:00', '04:00:00', 'Birmingham', 'B2 4QA', 'City Hall', 25),
-- Disaster Relief Aid (Cause 10)
(10, 'London Relief Kit Assembly', 'Assemble emergency kits for disaster victims.', 'Packing supplies, labeling boxes.', 'Able to lift boxes.', 'Shift from 10am to 1pm.', 'Faster disaster response.', '2025-12-14', '10:00:00', '13:00:00', '03:00:00', 'London', 'E9 1AB', 'Relief Centre', 30),
(10, 'Leeds Emergency Shelter Setup', 'Help set up temporary shelters.', 'Assembling tents, arranging bedding.', 'Physically fit volunteers.', 'Shift from 8am to 12pm.', 'Improved disaster readiness.', '2025-12-17', '08:00:00', '12:00:00', '04:00:00', 'Leeds', 'LS9 7AA', 'Relief Operations Hub', 25),
(10, 'Relief Rally Manchester', 'Assemble emergency kits for disaster victims.', 'Packing supplies, labeling boxes.', 'Able to lift boxes.', 'Shift from 10am to 1pm.', 'Faster disaster response.', '2025-12-31', '10:00:00', '13:00:00', '03:00:00', 'Manchester', 'M3 4AB', 'Relief Centre', 30),
(10, 'Aid in Action: Livingston', 'Distribute essential supplies to affected families.', 'Loading trucks, handing out kits.', 'Organized volunteers.', 'Event runs from 9am to 1pm.', 'Timely aid delivery.', '2025-12-21', '09:00:00', '13:00:00', '04:00:00', 'Livingston', 'EH54 0AA', 'Community Relief Centre', 25);

-- Dummy Data for Users
INSERT INTO User (Email, Password, FirstName, LastName)
VALUES
  ('a@test.com', '12345678', 'Alice', 'Smith'),

-- Dummy Data for Teams
INSERT INTO Team (Name, Description, Department, Capacity, OwnerUserID, JoinCode, IsActive)
VALUES
('Alpha Innovators', 'Product development team focused on emerging technologies.', 'R&D', 12, 1, 'A1B2C3D4', 1),
('Beta Builders', 'Team responsible for backend infrastructure and API management.', 'Engineering', 10, 1, 'B3C4D5E6', 1),
('Creative Crew', 'Design team creating UX/UI assets and branding materials.', 'Design', 8, 1, 'C5D6E7F8', 1),
('Delta Data', 'Analytics team working on data modeling and performance metrics.', 'Data Science', 9, 1, 'D7E8F9G0', 1),
('Echo Executives', 'Leadership group coordinating company-wide strategy.', 'Management', 5, 1, 'E9F0G1H2', 1)

