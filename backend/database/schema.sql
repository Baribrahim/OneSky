drop database if exists oneskyv1; 

create database oneskyv1;

use oneskyv1;

create table User
	(
	ID int primary key auto_increment,
	Email varchar(100) not null,
	Password varchar(100) not null,
	FirstName varchar(100) not null,
	LastName varchar(100) not null,
  DateCreated DATETIME DEFAULT CURRENT_TIMESTAMP,
  RankScore int DEFAULT 0,
  ProfileImgPath varchar(255) default "default.png"
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
	RequirementsProvided VARCHAR(2000) NOT NULL,
    RequirementsBring VARCHAR(2000) NOT NULL,
    ExpectedImpact varchar(2000) not null,
    Date date not null,
    StartTime time not null,
    EndTime time not null,
    Duration time not null,
    LocationCity varchar(255) not null,
    LocationPostcode varchar(10) not null,
    Address varchar(255) not null,
    Capacity int not null,
    Embedding text,
    Image_path varchar(255),
    Latitude DECIMAL(9,6) NOT NULL,
    Longitude DECIMAL(9,6) NOT NULL
    );
  
CREATE TABLE EventSchedule (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    EventID INT NOT NULL,
    Time TIME NOT NULL,
    Title VARCHAR(255) NOT NULL,
    Description VARCHAR(500) NOT NULL,
    FOREIGN KEY (EventID) REFERENCES Event(ID) ON DELETE CASCADE
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
  
-- Insert badges
INSERT INTO Badge (Name, Description, IconURL) VALUES
('Event Starter', 'Registered for your first upcoming event', '/src/assets/badges/firstStep.png'),
('Event Enthusiast', 'Registered for 5 upcoming events', '/src/assets/badges/eduEnthusiast.png'),
('First Step', 'Completed your first volunteering event', '/src/assets/badges/firstStep.png'),
('Volunteer Veteran', 'Completed 10 volunteering events', '/src/assets/badges/volunteerVetran.png'),
('Marathon Helper', 'Contributed 20+ total volunteering hours', '/src/assets/badges/marathonVolunteer.png'),
('Weekend Warrior', 'Completed an event on a Saturday or Sunday', '/src/assets/badges/weekendWarrior.png');

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


-- Bummy data for events

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(1,
'Thames Riverside Cleanup',
'Join our monthly Thames cleanup initiative! Help protect London’s vital waterway ecosystem while connecting with like-minded volunteers. This hands-on conservation effort improves local wildlife habitats and water quality. Volunteers will work together to remove litter, document wildlife, and collect data on pollution trends. By participating, you’ll contribute to a cleaner riverbank, support biodiversity, and raise awareness about the importance of sustainable practices. Whether you’re passionate about the environment or simply want to make a positive impact, this event offers a rewarding experience for all.',
'Litter Collection: Remove plastic bottles, cans, and debris from the riverbank; Wildlife Documentation: Record wildlife sightings and photograph marine life; Data Collection: Log types and quantities of litter to track pollution trends; Community Engagement: Raise awareness about river conservation',
'Safety equipment & gloves, litter pickers & bags, lunch & refreshments, transport from London',
'Weather-appropriate clothing, waterproof boots, sun hat & sunscreen, water bottle',
'Cleaner riverbank, improved biodiversity, and stronger community engagement.',
'2025-12-05', '09:00:00', '13:00:00', '04:00:00',
'London', 'E14 5HQ', 'Thames Riverside Park',
40, 'event-images/river.jpg', 51.5074, -0.0275);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(1, '09:00:00', 'Arrival & Registration', 'Meet at South Bank, sign in, and receive equipment'),
(1, '09:30:00', 'Cleanup Begins', 'Start litter collection and wildlife documentation'),
(1, '12:00:00', 'Lunch & Networking', 'Provided lunch and connect with fellow volunteers'),
(1, '13:00:00', 'Wrap-up', 'Final collection tally and return transport');


INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(1,
'Leeds Canal Cleanup',
'Join our Leeds canal cleanup initiative! This event is dedicated to improving the health and beauty of Leeds waterways while fostering community involvement. Volunteers will work together to remove litter, sort recyclables, and monitor wildlife along the canal paths. By participating, you’ll help create safer, cleaner spaces for pedestrians and wildlife, and raise awareness about the importance of protecting local ecosystems.',
'Litter Collection: Remove plastic bottles, cans, and debris from canal paths; Recycling Sorting: Separate recyclables from general waste; Wildlife Observation: Note any wildlife sightings and report unusual findings; Community Awareness: Engage with locals about canal conservation',
'Trash bags, gloves, litter pickers, refreshments, recycling bins',
'Comfortable walking shoes, weather-appropriate clothing, reusable water bottle',
'Cleaner canal paths, improved safety for pedestrians, and increased community awareness about environmental care.',
'2025-12-08', '10:00:00', '13:00:00', '03:00:00',
'Leeds', 'LS1 4AB', 'Leeds Canal Dock',
30, 'event-images/Canal-clean.jpg', 53.7940, -1.5476);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(2, '10:00:00', 'Arrival & Registration', 'Meet at Leeds Canal Dock, sign in, and receive equipment'),
(2, '10:15:00', 'Cleanup Begins', 'Start litter collection and recycling sorting'),
(2, '12:00:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(2, '12:30:00', 'Wrap-up', 'Final collection tally and group photo');


INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(1,
'Livingston Park Cleanup',
'Help restore Livingston’s beautiful green spaces by joining our park cleanup initiative. This event focuses on improving public areas for families and wildlife while fostering community spirit. Volunteers will remove litter, plant flowers, and sort recyclables to enhance the park’s natural beauty. By taking part, you’ll contribute to a cleaner, safer environment and help promote biodiversity in the local area.',
'Litter Collection: Remove plastic, cans, and other waste from park grounds; Flower Planting: Add color and biodiversity by planting seasonal flowers; Recycling Sorting: Separate recyclables from general waste; Wildlife Observation: Record sightings of birds and small mammals to monitor park health',
'Trash bags, gloves, litter pickers, refreshments, flower seedlings for planting',
'Comfortable outdoor clothing, sturdy shoes, reusable water bottle, gardening gloves (optional)',
'Cleaner and safer park environment, improved biodiversity through flower planting, and stronger community engagement.',
'2025-12-12', '09:00:00', '12:00:00', '03:00:00',
'Livingston', 'EH54 6AA', 'Almondvale Park',
25, 'event-images/park.jpg', 55.8865, -3.5210);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(3, '09:00:00', 'Arrival & Registration', 'Meet at Almondvale Park entrance, sign in, and receive equipment'),
(3, '09:15:00', 'Cleanup Begins', 'Start litter collection and recycling sorting'),
(3, '10:30:00', 'Flower Planting', 'Work together to plant flowers in designated areas'),
(3, '11:30:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(3, '12:00:00', 'Wrap-up', 'Final collection tally and group photo');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(1,
'Coastal Care Day',
'Join us for a day dedicated to cleaning Portobello Beach and protecting marine life. This event helps reduce ocean pollution and creates a safer environment for wildlife and beachgoers. Volunteers will collect litter, sort recyclables, and monitor coastal wildlife. By participating, you’ll help preserve the natural beauty of the beach and raise awareness about reducing plastic waste and protecting marine ecosystems.',
'Litter Collection: Remove plastic, cans, and other waste from the beach; Recycling Sorting: Separate recyclables from general waste; Wildlife Monitoring: Record sightings of seabirds and marine life; Awareness Campaign: Engage with visitors about reducing plastic use and protecting coastal ecosystems',
'Trash bags, gloves, litter pickers, refreshments, recycling bins',
'Weather-appropriate clothing, waterproof boots, reusable water bottle, sun protection (hat & sunscreen)',
'Cleaner beach, reduced marine pollution, improved biodiversity, and increased public awareness about ocean conservation.',
'2025-11-22', '09:00:00', '12:00:00', '03:00:00',
'Edinburgh', 'EH15 1HX', 'Portobello Beach',
40, 'event-images/beach.jpg', 55.9533, -3.1193);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(4, '09:00:00', 'Arrival & Registration', 'Meet at Portobello Beach entrance, sign in, and receive equipment'),
(4, '09:15:00', 'Cleanup Begins', 'Start litter collection and recycling sorting'),
(4, '11:00:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(4, '11:30:00', 'Wrap-up', 'Final collection tally and group photo');


INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(1,
'Brighton Beach Cleanup',
'Join our January Brighton Beach Cleanup to take part in a meaningful community initiative focused on protecting our coastline and supporting local wildlife. This event brings together volunteers, environmental advocates, and residents to promote a cleaner, healthier beach environment through collective action. Set against the scenic backdrop of Brighton Beach, the cleanup serves as a powerful reminder of our shared responsibility to care for natural spaces. It’s more than just a day at the beach—it’s a chance to contribute to long-term conservation efforts, foster environmental awareness, and strengthen community bonds. Whether you\'re passionate about sustainability or simply looking to make a positive impact, this event offers an opportunity to be part of something bigger. Your presence helps amplify the message that protecting our oceans starts with local action.',
'Litter Collection: Remove plastic, cans, and debris from the beach; Recycling Sorting: Separate recyclables from general waste; Wildlife Monitoring: Record sightings of seabirds and marine life; Awareness Campaign: Engage with visitors about reducing plastic use',
'Trash bags, gloves, litter pickers, refreshments, recycling bins',
'Weather-appropriate clothing, waterproof boots, reusable water bottle, sun protection',
'Cleaner beach, reduced marine pollution, improved biodiversity, and increased public awareness about ocean conservation.',
'2026-01-01', '09:00:00', '12:00:00', '03:00:00',
'Brighton', 'BN2 1TW', 'Brighton Pier',
35, 'event-images/beach.jpg', 50.8198, -0.1367);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(5, '09:00:00', 'Arrival & Registration', 'Meet at Brighton Pier entrance, sign in, and receive equipment'),
(5, '09:15:00', 'Cleanup Begins', 'Start litter collection and recycling sorting'),
(5, '11:00:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(5, '11:30:00', 'Wrap-up', 'Final collection tally and group photo');


-- Tree Planting (Cause 2)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(2,
'Leeds Green Belt Planting',
'Join us in restoring Leeds’ green belt by planting trees and improving local biodiversity. This event focuses on creating healthier ecosystems and combating climate change. Volunteers will plant saplings, mulch soil, and learn about sustainable forestry practices. By participating, you’ll help improve air quality and create greener spaces for future generations.',
'Tree Planting: Dig holes and plant saplings; Mulching: Spread mulch to protect roots and retain moisture; Watering: Ensure newly planted trees are hydrated; Environmental Education: Learn about the benefits of urban forestry and biodiversity',
'Tree saplings, mulch, gardening tools, gloves, refreshments',
'Comfortable outdoor clothing, sturdy shoes, reusable water bottle',
'Improved air quality, enhanced biodiversity, and stronger community involvement in environmental sustainability.',
'2025-12-09', '09:00:00', '17:00:00', '08:00:00',
'Leeds', 'LS6 2AB', 'Roundhay Park',
30, 'event-images/tree.jpg', 53.8381, -1.4933);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(6, '09:00:00', 'Arrival & Registration', 'Meet at Roundhay Park entrance, sign in, and receive equipment'),
(6, '09:30:00', 'Safety Briefing', 'Learn planting techniques and safety guidelines'),
(6, '10:00:00', 'Morning Planting Session', 'Start planting saplings and mulching soil'),
(6, '11:30:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(6, '12:00:00', 'Environmental Education', 'Learn about biodiversity and sustainable forestry'),
(6, '13:00:00', 'Afternoon Planting Session', 'Continue planting and watering trees'),
(6, '15:00:00', 'Community Engagement', 'Interact with locals and share conservation tips'),
(6, '16:30:00', 'Wrap-up & Farewell', 'Review progress, group photo, and return equipment');


INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(2,
'Livingston Woodland Project',
'Help expand Livingston’s woodland area by joining a community-led tree planting initiative dedicated to enhancing local biodiversity and green space. This event supports long-term environmental goals by increasing tree coverage, improving air quality, and creating habitats for native wildlife. Set in the heart of Livingston, the project encourages sustainable land management and highlights the importance of restoring natural ecosystems. It’s a chance to connect with others who care about the environment, contribute to climate resilience, and leave a lasting legacy for future generations. Whether you\'re an experienced conservationist or simply passionate about nature, your involvement helps promote ecological balance and strengthens community ties through shared action.',
'Tree Planting: Dig holes and plant saplings; Watering: Hydrate newly planted trees; Soil Preparation: Prepare ground for optimal growth; Community Education: Discuss benefits of woodland expansion',
'Tree saplings, gardening tools, gloves, refreshments',
'Outdoor clothing, sturdy boots, reusable water bottle',
'Enhanced biodiversity, improved soil health, and increased green spaces for community recreation.',
'2025-12-13', '10:00:00', '13:00:00', '03:00:00',
'Livingston', 'EH54 7AA', 'Deans Community Woodland',
25, 'event-images/tree2.jpg', 55.9000, -3.5500);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(7, '10:00:00', 'Arrival & Registration', 'Meet at Deans Community Woodland entrance, sign in, and receive equipment'),
(7, '10:15:00', 'Tree Planting', 'Begin planting and watering trees'),
(7, '11:30:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(7, '12:30:00', 'Wrap-up', 'Final watering and group photo');


INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(2,
'Manchester Tree Planting',
'Join us in creating greener urban spaces by supporting tree planting efforts in Manchester’s parks. This community initiative is part of a broader movement to improve urban environments, combat air pollution, and enhance local ecosystems. By increasing tree coverage in public spaces, the event contributes to climate resilience, supports biodiversity, and helps create healthier, more livable cities. Trees play a vital role in regulating temperature, improving air quality, and providing shelter for wildlife—making them essential to sustainable urban planning. This event is a chance to connect with others who care about the environment, take part in meaningful action, and help shape a greener future for Manchester.',
'Digging: Prepare soil and create planting holes; Tree Planting: Position and secure saplings; Watering: Hydrate newly planted trees; Mulching: Apply mulch for soil protection',
'Tree saplings, mulch, gardening tools, gloves, refreshments',
'Comfortable outdoor clothing, sturdy shoes, reusable water bottle',
'Greener urban spaces, improved air quality, and increased community participation in environmental care.',
'2025-12-30', '10:00:00', '13:00:00', '03:00:00',
'Manchester', 'M1 2AB', 'Whitworth Park',
30, 'event-images/woodland.jpg', 53.4648, -2.2294);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(8, '10:00:00', 'Arrival & Registration', 'Meet at Whitworth Park entrance, sign in, and receive equipment'),
(8, '10:15:00', 'Tree Planting', 'Begin digging and planting'),
(8, '11:30:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(8, '12:30:00', 'Wrap-up', 'Water trees and review progress');


INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(2,
'Roots for the Future',
'Join us in planting trees at Victoria Park to create a greener, healthier environment for London. This event focuses on combating climate change and improving urban biodiversity. Volunteers will dig, plant, and water trees while learning about sustainable forestry practices.',
'Digging: Prepare soil and create planting holes; Tree Planting: Position and secure saplings; Watering: Hydrate newly planted trees; Mulching: Apply mulch for soil protection',
'Tree saplings, mulch, gardening tools, gloves, refreshments',
'Comfortable outdoor clothing, sturdy shoes, reusable water bottle',
'Greener urban spaces, improved air quality, and stronger community engagement in sustainability.',
'2025-11-06', '10:00:00', '13:00:00', '03:00:00',
'London', 'E3 5TB', 'Victoria Park',
35, 'event-images/roots.jpg', 51.5363, -0.0330);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(9, '10:00:00', 'Arrival & Registration', 'Meet at Victoria Park entrance, sign in, and receive equipment'),
(9, '10:15:00', 'Tree Planting', 'Begin digging and planting'),
(9, '11:30:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(9, '12:30:00', 'Wrap-up', 'Water trees and review progress');

-- Food Bank Support (Cause 3)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(3,
'London Food Sorting',
'Join us at East End Food Bank to sort and pack food donations for families in need. This event ensures that essential supplies are organized and distributed efficiently. Volunteers will label, pack, and prepare food parcels while learning about food security challenges in London.',
'Labeling: Mark boxes with correct contents; Packing: Organize food items into parcels; Quality Check: Ensure items are safe and within date; Distribution Prep: Arrange parcels for delivery',
'Packing materials, gloves, refreshments',
'Comfortable clothing, closed-toe shoes, ability to lift boxes',
'Faster food distribution, reduced waste, and improved support for vulnerable families.',
'2025-12-07', '09:00:00', '12:00:00', '03:00:00',
'London', 'E1 6AB', 'East End Food Bank',
20, 'event-images/food-bank.jpg', 51.5200, -0.0710);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(10, '09:00:00', 'Arrival & Registration', 'Sign in and receive instructions'),
(10, '09:15:00', 'Sorting Begins', 'Label and pack food items'),
(10, '11:00:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(10, '11:30:00', 'Wrap-up', 'Organize parcels for distribution');


INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(3,
'Leeds Food Drive',
'Support Leeds Community Kitchen by assisting in food collection and packing. Volunteers will sort donations, pack parcels, and help prepare supplies for families in need. This event promotes community solidarity and ensures timely food distribution.',
'Sorting: Organize donated food items; Packing: Prepare parcels for families; Quality Check: Inspect items for safety; Inventory: Record quantities for tracking',
'Packing materials, gloves, refreshments',
'Organized mindset, comfortable clothing, reusable water bottle',
'Support for families in need, improved food security, and stronger community engagement.',
'2025-12-10', '09:00:00', '17:00:00', '08:00:00',
'Leeds', 'LS2 8AA', 'Leeds Community Kitchen',
25, 'event-images/foodbank2.jpg', 53.8010, -1.5470);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(11, '09:00:00', 'Arrival & Registration', 'Sign in and receive instructions'),
(11, '09:30:00', 'Safety & Hygiene Briefing', 'Learn food safety and handling guidelines'),
(11, '10:00:00', 'Morning Sorting Session', 'Organize donated food items by category'),
(11, '11:30:00', 'Packing Session', 'Prepare parcels for families in need'),
(11, '12:30:00', 'Lunch & Networking', 'Enjoy provided lunch and connect with volunteers'),
(11, '13:30:00', 'Quality Check & Inventory', 'Inspect items and record quantities for tracking'),
(11, '15:00:00', 'Afternoon Packing Session', 'Finalize parcels and prepare for distribution'),
(11, '16:30:00', 'Wrap-up & Farewell', 'Review progress, group photo, and clean-up');


INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(3,
'Livingston Food Hub',
'Join us at Livingston Food Hub to help distribute food parcels to families in need. Volunteers will pack, organize, and assist with handing out supplies. This event strengthens community support and ensures timely access to essential resources.',
'Packing: Prepare food parcels; Sorting: Organize items by category; Distribution: Assist in handing out parcels; Inventory: Track supplies for future planning',
'Packing materials, gloves, refreshments',
'Friendly attitude, comfortable clothing, reusable water bottle',
'Improved food security, reduced hunger, and stronger community connections.',
'2025-12-14', '11:00:00', '14:00:00', '03:00:00',
'Livingston', 'EH54 8AA', 'Livingston Food Hub',
20, 'event-images/foodbank3.jpg', 55.8990, -3.5200);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(12, '11:00:00', 'Arrival & Registration', 'Sign in and receive instructions'),
(12, '11:15:00', 'Packing Begins', 'Organize and prepare parcels'),
(12, '12:30:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(12, '13:00:00', 'Wrap-up', 'Assist with distribution and inventory');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(3,
'January Food Parcel Prep',
'Support our January food parcel preparation event in Glasgow and help strengthen food security for families facing hardship. This community initiative brings people together to ensure essential supplies reach those who need them most, fostering a spirit of care, solidarity, and social responsibility. Held in partnership with local organizations, the event highlights the importance of accessible support systems and the role of collective action in addressing food inequality. It’s an opportunity to contribute to a compassionate cause, build community connections, and promote a culture of giving and inclusion. Whether you\'re passionate about social impact or simply want to lend a helping hand, your involvement helps make a tangible difference in the lives of others.',
'Sorting: Organize donated food items; Packing: Prepare parcels for families; Quality Check: Inspect items for safety; Inventory: Record quantities for tracking',
'Packing materials, gloves, refreshments',
'Comfortable clothing, closed-toe shoes, reusable water bottle',
'Support for families in need, improved food security, and stronger community engagement.',
'2026-01-14', '10:00:00', '13:00:00', '03:00:00',
'Glasgow', 'G1 1XX', 'Glasgow Community Kitchen',
25, 'event-images/foodbank3.jpg', 55.8607, -4.2518);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(13, '10:00:00', 'Arrival & Registration', 'Sign in and receive instructions'),
(13, '10:15:00', 'Sorting Begins', 'Organize and pack food items'),
(13, '11:30:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(13, '12:30:00', 'Wrap-up', 'Finalize parcels and inventory');


-- Homeless Outreach (Cause 4)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(4,
'London Winter Care Drive',
'Support our winter outreach at Hope Shelter by helping distribute warm clothing and blankets to individuals experiencing homelessness. This compassionate initiative aims to provide comfort, dignity, and essential protection against the harsh winter conditions. By participating, you’ll be part of a community effort to address immediate needs and raise awareness about the challenges faced by vulnerable populations. The event fosters a spirit of empathy and solidarity, reminding us of the importance of collective care and social responsibility. Your involvement helps ensure that those most at risk receive the support they need to stay safe, warm, and seen during the colder months.',
'Packing: Prepare care packages with warm clothes and blankets; Distribution: Hand out packages to individuals; Inventory: Track remaining supplies; Community Support: Engage with recipients respectfully',
'Warm clothes, blankets, hygiene items, refreshments',
'Compassionate attitude, comfortable clothing, reusable water bottle',
'Better winter safety, improved quality of life, and stronger community support for vulnerable individuals.',
'2025-12-08', '12:00:00', '15:00:00', '03:00:00',
'London', 'E2 7AB', 'Hope Shelter',
30, '', 51.5290, -0.0700);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(14, '12:00:00', 'Arrival & Registration', 'Sign in and receive instructions'),
(14, '12:15:00', 'Packing Begins', 'Prepare care packages'),
(14, '13:30:00', 'Distribution', 'Hand out packages to recipients'),
(14, '14:30:00', 'Wrap-up', 'Organize remaining supplies');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(4,
'Leeds Hot Meal Service',
'Join us at St George’s Centre for a community meal service supporting individuals experiencing homelessness. This event offers more than just a hot meal—it creates a warm, welcoming space where people can feel seen, respected, and cared for. Through shared effort and compassion, volunteers help foster a sense of dignity and connection for those facing difficult circumstances. The initiative highlights the importance of inclusive support systems and the power of community in addressing social challenges. Whether you\'re passionate about social justice or simply want to make a difference, your presence helps build a more caring and resilient community.',
'Cooking: Help prepare nutritious meals; Serving: Plate and distribute meals to guests; Clean-up: Assist with post-meal cleaning; Guest Engagement: Provide friendly conversation and support',
'Ingredients, utensils, gloves, refreshments',
'Basic kitchen skills, comfortable clothing, reusable water bottle',
'Improved nutrition, enhanced dignity, and stronger community support for homeless individuals.',
'2025-11-11', '13:00:00', '16:00:00', '03:00:00',
'Leeds', 'LS3 1AA', 'St George’s Centre',
25, 'event-images/hot-meal.jpg', 53.8015, -1.5580);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(15, '13:00:00', 'Arrival & Registration', 'Sign in and receive instructions'),
(15, '13:15:00', 'Meal Prep', 'Assist with cooking and plating'),
(15, '14:00:00', 'Serving', 'Distribute meals to guests'),
(15, '15:00:00', 'Wrap-up', 'Clean up and thank volunteers');


INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(4,
'Livingston Care Package Prep',
'Support Livingston’s homeless outreach by contributing to the preparation of hygiene kits for individuals facing housing insecurity. This initiative plays a vital role in promoting dignity, health, and wellbeing among vulnerable members of the community. By helping organize essential supplies, the event strengthens local support networks and highlights the importance of accessible, compassionate care. It’s a meaningful opportunity to take part in a collective effort that addresses immediate needs while fostering long-term community resilience. Your involvement helps ensure that those experiencing homelessness receive the basic items they need to feel safe, clean, and cared for.',
'Sorting: Organize hygiene items; Packing: Assemble care kits; Inventory: Track supplies; Teamwork: Collaborate with other volunteers',
'Hygiene items, packing materials, gloves, refreshments',
'Organized mindset, comfortable clothing, reusable water bottle',
'Improved hygiene access, better health outcomes, and increased support for vulnerable individuals.',
'2025-11-15', '10:00:00', '13:00:00', '03:00:00',
'Livingston', 'EH54 9AA', 'Community Hall',
20, 'event-images/care-package2.jpg', 55.9005, -3.5300);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(16, '10:00:00', 'Arrival & Registration', 'Sign in and receive instructions'),
(16, '10:15:00', 'Packing Begins', 'Assemble hygiene kits'),
(16, '11:30:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(16, '12:30:00', 'Wrap-up', 'Organize supplies and clean up');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(4,
'Birmingham Homeless Care Drive',
'Join us at Hope Shelter in Birmingham to distribute care packages to homeless individuals. Volunteers will pack and hand out essential items while offering warmth and compassion to those in need.',
'Packing: Assemble care packages with warm clothes and hygiene items; Distribution: Hand out packages to recipients; Guest Engagement: Provide friendly conversation and support; Inventory: Track supplies for future outreach',
'Warm clothes, hygiene items, gloves, refreshments',
'Compassionate attitude, comfortable clothing, reusable water bottle',
'Improved quality of life, increased dignity, and stronger community support for homeless individuals.',
'2025-10-28', '12:00:00', '15:00:00', '03:00:00',
'Birmingham', 'B1 1AA', 'Hope Shelter',
30, '', 52.4790, -1.9025);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(17, '12:00:00', 'Arrival & Registration', 'Sign in and receive instructions'),
(17, '12:15:00', 'Packing Begins', 'Assemble care packages'),
(17, '13:30:00', 'Distribution', 'Hand out packages to recipients'),
(17, '14:30:00', 'Wrap-up', 'Organize remaining supplies and clean up');

-- Animal Shelter Assistance (Cause 5)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(5,
'London Pet Adoption Day',
'Support Happy Paws Shelter by taking part in a heartwarming pet adoption event that helps animals find safe, loving homes. This initiative promotes responsible pet ownership and raises awareness about the importance of animal welfare in the community. By creating a welcoming and well-organized environment, the event encourages meaningful connections between potential adopters and shelter animals. It''s a chance to contribute to a cause that not only transforms the lives of pets but also brings joy and companionship to families. Whether you''re an animal lover or simply want to support a good cause, your involvement helps ensure every pet has the opportunity to be cared for and cherished.',
'Pet Handling: Assist with walking and calming animals; Visitor Guidance: Help families meet adoptable pets; Adoption Support: Provide information and assist with paperwork',
'Leashes, pet supplies, refreshments, adoption forms',
'Comfortable with animals, friendly attitude, reusable water bottle',
'Increased pet adoptions, improved shelter visibility, and stronger community engagement.',
'2025-12-09', '09:00:00', '17:00:00', '08:00:00',
'London', 'E3 4AB', 'Happy Paws Shelter',
15, 'event-images/adopt.jpg', 51.5360, -0.0330);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(18, '09:00:00', 'Arrival & Registration', 'Meet at Happy Paws Shelter, sign in, and receive instructions'),
(18, '09:30:00', 'Safety & Handling Briefing', 'Learn pet handling techniques and visitor interaction guidelines'),
(18, '10:00:00', 'Morning Adoption Support', 'Assist families meeting pets and guide through adoption process'),
(18, '11:30:00', 'Pet Care Session', 'Walk and calm animals, ensure hydration and comfort'),
(18, '12:30:00', 'Lunch & Networking', 'Enjoy provided lunch and connect with volunteers'),
(18, '13:30:00', 'Afternoon Adoption Support', 'Continue helping visitors and processing adoption paperwork'),
(18, '15:00:00', 'Community Engagement', 'Share animal welfare tips and promote responsible pet ownership'),
(18, '16:30:00', 'Wrap-up & Farewell', 'Finalize adoptions, clean up, and group photo');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(5,
'Livingston Shelter Support',
'Join us at Livingston Animal Centre to support daily shelter operations that help ensure the wellbeing of animals in care. This event promotes animal welfare by maintaining a clean, safe, and nurturing environment for pets awaiting adoption. Through community involvement, the initiative highlights the importance of responsible pet care and the role volunteers play in supporting local shelters. It''s a chance to make a meaningful impact, connect with fellow animal lovers, and contribute to a compassionate cause.',
'Dog Walking: Take dogs for exercise and socialization; Cleaning: Maintain cleanliness of cages and common areas; Feeding: Assist with feeding routines',
'Leashes, cleaning supplies, pet food, refreshments',
'Physically active, comfortable with animals, reusable water bottle',
'Improved shelter operations, healthier animals, and increased volunteer support.',
'2025-10-16', '10:00:00', '13:00:00', '03:00:00',
'Livingston', 'EH54 5AA', 'Livingston Animal Centre',
15, 'event-images/shelter.jpg', 55.8860, -3.5200);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(19, '10:00:00', 'Arrival & Registration', 'Meet at Livingston Animal Centre, receive instructions'),
(19, '10:15:00', 'Tasks Begin', 'Walk dogs and clean enclosures'),
(19, '11:30:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(19, '12:30:00', 'Wrap-up', 'Final cleaning and group photo');


INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(5,
'Paws & Play Adoption Fair',
'Help families meet adoptable pets at Happy Paws Shelter by supporting a fun and interactive event that connects potential adopters with animals in need of loving homes. This initiative promotes responsible pet ownership and encourages community involvement in animal welfare. By creating a welcoming atmosphere, the event helps build meaningful connections between people and pets, while raising awareness about the importance of adoption and compassionate care. It''s a chance to make a lasting difference in the lives of both animals and families.',
'Visitor Guidance: Welcome and assist families; Pet Handling: Ensure animals are calm and safe; Adoption Support: Provide information and help with forms',
'Leashes, refreshments, adoption forms, pet supplies',
'Comfortable with animals, friendly attitude, reusable water bottle',
'More pets find loving homes, increased shelter visibility, and stronger community engagement.',
'2025-11-09', '11:00:00', '15:00:00', '04:00:00',
'London', 'E3 4AB', 'Happy Paws Shelter',
15, 'event-images/adopt.jpg', 51.5360, -0.0330);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(20, '09:00:00', 'Arrival & Registration', 'Meet at Happy Paws Shelter, sign in, and receive instructions'),
(20, '09:30:00', 'Safety & Handling Briefing', 'Learn pet handling techniques and visitor interaction guidelines'),
(20, '10:00:00', 'Morning Adoption Support', 'Assist families meeting pets and guide through adoption process'),
(20, '11:30:00', 'Pet Care Session', 'Walk and calm animals, ensure hydration and comfort'),
(20, '12:30:00', 'Lunch & Networking', 'Enjoy provided lunch and connect with volunteers'),
(20, '13:30:00', 'Afternoon Adoption Support', 'Continue helping visitors and processing adoption paperwork'),
(20, '15:00:00', 'Community Engagement', 'Share animal welfare tips and promote responsible pet ownership'),
(20, '16:30:00', 'Wrap-up & Farewell', 'Finalize adoptions, clean up, and group photo');


INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(5,
'Furry Friends Care Day',
'Support Leeds Animal Rescue by contributing to daily care efforts that help maintain a clean, safe, and nurturing environment for rescued animals. This initiative highlights the importance of animal welfare and the role of community support in providing comfort and stability to pets in need. By taking part, volunteers help ensure that animals receive the attention and care they deserve while promoting a culture of compassion and responsibility. It''s a meaningful way to make a difference in the lives of vulnerable animals and support the work of local rescue efforts.',
'Feeding: Provide food and water to animals; Cleaning: Sanitize cages and common areas; Enrichment: Help with toys and comfort items',
'Pet food, cleaning supplies, gloves, refreshments',
'Animal-friendly attitude, comfortable clothing, reusable water bottle',
'Better animal welfare, cleaner shelter environment, and increased volunteer support.',
'2025-11-12', '09:00:00', '12:00:00', '03:00:00',
'Leeds', 'LS4 2AA', 'Leeds Animal Rescue',
20, 'event-images/pets.jpg', 53.8090, -1.5800);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(21, '09:00:00', 'Arrival & Registration', 'Meet at Leeds Animal Rescue, receive instructions'),
(21, '09:15:00', 'Tasks Begin', 'Feed animals and clean enclosures'),
(21, '11:00:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(21, '11:30:00', 'Wrap-up', 'Final cleaning and group photo');

-- Senior Care Visits (Cause 6)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(6,
'London Senior Social',
'Spend time with elderly residents at Rosewood Care Home by taking part in a meaningful initiative that fosters companionship, joy, and emotional wellbeing. This event helps reduce loneliness among seniors by creating opportunities for connection through conversation, shared activities, and presence. It’s a chance to brighten someone’s day, build intergenerational bonds, and contribute to a more caring and inclusive community. Whether you\'re passionate about social impact or simply enjoy engaging with others, your involvement makes a heartfelt difference.',
'Games: Play board games and cards; Reading: Read books and newspapers aloud; Chatting: Share stories and listen to residents',
'Games, books, refreshments',
'Friendly and patient attitude, comfortable clothing',
'Reduced loneliness, improved mental well-being, and stronger intergenerational connections.',
'2025-12-10', '14:00:00', '17:00:00', '03:00:00',
'London', 'E5 6AB', 'Rosewood Care Home',
12, 'event-images/seniors.jpg', 51.5580, -0.0570);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(22, '14:00:00', 'Arrival & Registration', 'Meet at Rosewood Care Home, receive instructions'),
(22, '14:15:00', 'Activities Begin', 'Engage in games and reading'),
(22, '15:30:00', 'Refreshment Break', 'Enjoy snacks with residents'),
(22, '16:30:00', 'Wrap-up', 'Final conversations and group photo');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(6,
'Leeds Music Afternoon',
'Bring joy to seniors at Meadow View Care Home through music by participating in a vibrant and uplifting event that supports mental wellness and emotional connection. This initiative uses the power of music to create a lively, engaging atmosphere where residents can relax, reminisce, and feel valued. Whether through singing, playing instruments, or simply sharing the moment, volunteers help foster a sense of community and brighten the day for elderly residents. It’s a meaningful way to promote wellbeing and build intergenerational bonds through creativity and care.',
'Playing Instruments: Perform familiar tunes; Singing: Lead sing-alongs with residents; Interaction: Encourage participation and conversation',
'Musical instruments, song sheets, refreshments',
'Musical skills preferred, friendly attitude, reusable water bottle',
'Improved mental health, increased happiness, and stronger community bonds.',
'2025-12-13', '15:00:00', '18:00:00', '03:00:00',
'Leeds', 'LS5 3AA', 'Meadow View Care Home',
10, 'event-images/seniors-music.jpg', 53.8095, -1.5850);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(23, '15:00:00', 'Arrival & Registration', 'Meet at Meadow View Care Home, receive instructions'),
(23, '15:15:00', 'Music Begins', 'Perform and engage with residents'),
(23, '16:30:00', 'Refreshment Break', 'Enjoy snacks with residents'),
(23, '17:30:00', 'Wrap-up', 'Final songs and group photo');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(6,
'Livingston Holiday Card Day',
'Create and deliver holiday cards to seniors at Community Arts Centre by participating in a thoughtful initiative that spreads seasonal cheer and emotional warmth. This event fosters connection and joy by sharing personalized messages with elderly residents, many of whom may feel isolated during the holidays. Through creativity and kindness, volunteers help brighten spirits and remind seniors that they are remembered and valued. It’s a simple yet powerful way to promote inclusion, compassion, and community care during the festive season.',
'Crafting: Design and decorate holiday cards; Writing: Add thoughtful messages; Delivery: Hand out cards to seniors',
'Craft supplies, card stock, refreshments',
'Creative mindset, friendly attitude, reusable water bottle',
'Increased happiness, reduced isolation, and stronger community connections.',
'2025-12-17', '10:00:00', '13:00:00', '03:00:00',
'Livingston', 'EH54 4AA', 'Community Arts Centre',
15, 'event-images/card-day.jpg', 55.8890, -3.5200);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(24, '10:00:00', 'Arrival & Registration', 'Meet at Community Arts Centre, receive instructions'),
(24, '10:15:00', 'Card Making', 'Craft and write holiday cards'),
(24, '11:30:00', 'Refreshment Break', 'Enjoy snacks and drinks'),
(24, '12:30:00', 'Wrap-up', 'Deliver cards and group photo');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(6,
'New Year Senior Visit',
'Celebrate the New Year by spending time with elderly residents at Manchester Care Home through a heartwarming initiative that fosters connection, joy, and emotional wellbeing. This event helps reduce loneliness among seniors by creating meaningful moments through conversation, storytelling, and shared activities. It’s a chance to start the year with kindness, build intergenerational relationships, and contribute to a more compassionate and inclusive community. Your presence can make a lasting difference in someone’s day.',
'Games: Play board games and puzzles with residents; Storytelling: Share stories and listen to life experiences; Companionship: Engage in friendly conversation and build connections',
'Games, refreshments, activity materials',
'Friendly attitude, patience, comfortable clothing',
'Reduced loneliness, improved emotional well-being, and stronger intergenerational connections.',
'2026-01-18', '14:00:00', '17:00:00', '03:00:00',
'Manchester', 'M4 5AZ', 'Manchester Care Home',
15, 'event-images/seniors.jpg', 53.4839, -2.2446);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(25, '14:00:00', 'Arrival & Welcome', 'Meet staff and receive instructions'),
(25, '14:15:00', 'Activities Begin', 'Engage in games and conversations'),
(25, '15:30:00', 'Refreshment Break', 'Enjoy snacks with residents'),
(25, '16:30:00', 'Wrap-up', 'Group photo and farewell');

-- Mental Health Awareness (Cause 7)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(7,
'London Mindfulness Workshop',
'Support mental well-being by assisting in a guided mindfulness session at the Wellness Centre. Volunteers will help set up the space, guide participants through breathing exercises, and distribute wellness materials. This event promotes relaxation and stress reduction in a supportive environment.',
'Setup: Arrange mats and seating; Activity Support: Guide breathing and mindfulness exercises; Materials: Distribute handouts and wellness kits; Engagement: Encourage participation and answer questions',
'Mats, wellness kits, handouts, refreshments',
'Comfortable clothing, good communication skills, calm demeanor',
'Improved mental well-being, reduced stress, and increased awareness of mindfulness practices.',
'2025-12-11', '10:00:00', '13:00:00', '03:00:00',
'London', 'E6 7AB', 'Wellness Centre',
20, 'event-images/mental-health.jpg', 51.5270, 0.0520);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(26, '10:00:00', 'Arrival & Setup', 'Prepare the space and materials'),
(26, '10:15:00', 'Workshop Begins', 'Guide mindfulness activities'),
(26, '12:00:00', 'Refreshment Break', 'Enjoy snacks and drinks'),
(26, '12:30:00', 'Wrap-up', 'Collect materials and debrief');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(7,
'Leeds Mental Health Booth',
'Raise awareness about mental health by running an information booth in City Square. Volunteers will distribute leaflets, engage with visitors, and answer questions about local mental health resources. This event helps reduce stigma and promotes access to support.',
'Booth Setup: Arrange table and materials; Outreach: Distribute leaflets and talk to visitors; Engagement: Answer questions and share resources; Feedback: Collect visitor responses',
'Leaflets, brochures, booth signage, refreshments',
'Friendly attitude, good communication skills, weather-appropriate clothing',
'Increased mental health awareness, reduced stigma, and better access to support services.',
'2025-10-14', '11:00:00', '15:00:00', '04:00:00',
'Leeds', 'LS6 4AA', 'City Square',
15, 'event-images/mindful.jpg', 53.8060, -1.5480);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(27, '11:00:00', 'Setup', 'Prepare booth and materials'),
(27, '11:30:00', 'Outreach Begins', 'Engage with visitors'),
(27, '14:00:00', 'Refreshment Break', 'Enjoy snacks and drinks'),
(27, '14:30:00', 'Wrap-up', 'Collect feedback and pack up');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(7,
'Livingston Stress Relief Day',
'Help organize stress-relief activities at the Community Hall to promote mental wellness. Volunteers will assist with yoga setup, distribute materials, and support participants during relaxation exercises. This event encourages healthy coping strategies and community connection.',
'Setup: Arrange yoga mats and seating; Distribution: Hand out wellness materials; Support: Guide participants through exercises; Engagement: Encourage participation and answer questions',
'Yoga mats, wellness kits, handouts, refreshments',
'Organized mindset, comfortable clothing, friendly attitude',
'Reduced stress levels, improved mental wellness, and stronger community support.',
'2025-12-18', '09:00:00', '12:00:00', '03:00:00',
'Livingston', 'EH54 3AA', 'Community Hall',
20, 'event-images/stress.jpg', 55.8850, -3.5150);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(28, '09:00:00', 'Setup', 'Prepare space and materials'),
(28, '09:30:00', 'Activities Begin', 'Support yoga and relaxation sessions'),
(28, '11:00:00', 'Refreshment Break', 'Enjoy snacks and drinks'),
(28, '11:30:00', 'Wrap-up', 'Collect materials and debrief');

-- STEM Mentorship (Cause 8)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(8,
'Code & Create',
'Teach basic coding to children at Tech Hub using Scratch. Volunteers will guide exercises, troubleshoot issues, and encourage creativity. This event promotes digital literacy and inspires future tech innovators.',
'Guidance: Help children navigate Scratch; Troubleshooting: Assist with coding errors; Engagement: Encourage creativity and exploration; Wrap-up: Review projects and celebrate progress',
'Laptops, Scratch guides, refreshments',
'Basic coding knowledge, patience, enthusiasm',
'Improved digital literacy, increased interest in coding, and empowered young learners.',
'2025-12-12', '13:00:00', '16:00:00', '03:00:00',
'London', 'E7 8AB', 'Tech Hub',
15, 'event-images/code.jpg', 51.5470, 0.0250);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(29, '13:00:00', 'Setup', 'Prepare laptops and materials'),
(29, '13:15:00', 'Workshop Begins', 'Guide Scratch activities'),
(29, '15:00:00', 'Refreshment Break', 'Enjoy snacks and drinks'),
(29, '15:30:00', 'Wrap-up', 'Review projects and celebrate');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(8,
'Build-a-Bot Challenge',
'Guide students in building simple robots at the Innovation Lab. Volunteers will explain steps, troubleshoot issues, and encourage teamwork. This event fosters hands-on STEM learning and problem-solving skills.',
'Instruction: Explain robot-building steps; Support: Help troubleshoot assembly issues; Engagement: Encourage teamwork and creativity; Wrap-up: Showcase completed robots',
'Robot kits, tools, instruction sheets, refreshments',
'STEM knowledge, teamwork skills, enthusiasm',
'Hands-on STEM learning, improved problem-solving, and increased interest in robotics.',
'2025-12-15', '10:00:00', '13:00:00', '03:00:00',
'Leeds', 'LS7 5AA', 'Innovation Lab',
15, 'event-images/build-a-bot.jpg', 53.8120, -1.5400);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(30, '10:00:00', 'Setup', 'Prepare kits and tools'),
(30, '10:15:00', 'Workshop Begins', 'Guide robot assembly'),
(30, '12:00:00', 'Refreshment Break', 'Enjoy snacks and drinks'),
(30, '12:30:00', 'Wrap-up', 'Showcase robots and celebrate');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(8,
'Livingston STEM Career Talk',
'Share insights into STEM careers at the Science Centre. Volunteers will give talks, answer questions, and inspire students to pursue science and technology fields. This event promotes career awareness and mentorship.',
'Presentation: Share career journeys and advice; Q&A: Answer student questions; Engagement: Encourage interest in STEM fields; Wrap-up: Provide resources and contacts',
'Presentation materials, refreshments',
'STEM professionals preferred, public speaking skills',
'Increased STEM awareness, inspired students, and stronger mentorship connections.',
'2025-12-19', '11:00:00', '13:00:00', '02:00:00',
'Livingston', 'EH54 2AA', 'Science Centre',
20, 'event-images/career-talk.jpg', 55.8830, -3.5100);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(31, '11:00:00', 'Setup', 'Prepare presentation space'),
(31, '11:15:00', 'Career Talks', 'Share insights and answer questions'),
(31, '12:30:00', 'Wrap-up', 'Provide resources and contacts');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(8,
'Edinburgh STEM Robotics Workshop',
'Teach kids to build simple robots at Tech Innovation Hub. Volunteers will guide assembly, troubleshoot issues, and encourage exploration. This event promotes hands-on learning and sparks interest in engineering.',
'Assembly: Guide robot building steps; Troubleshooting: Help fix issues; Engagement: Encourage creativity and teamwork; Wrap-up: Showcase completed robots',
'Robot kits, tools, instruction sheets, refreshments',
'Basic robotics knowledge, patience, enthusiasm',
'Hands-on STEM learning, increased interest in engineering, and empowered young learners.',
'2025-12-23', '13:00:00', '16:00:00', '03:00:00',
'Edinburgh', 'EH8 9YL', 'Tech Innovation Hub',
15, 'event-images/robotics.jpg', 55.9450, -3.1860);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(32, '13:00:00', 'Setup', 'Prepare kits and tools'),
(32, '13:15:00', 'Workshop Begins', 'Guide robot assembly'),
(32, '15:00:00', 'Refreshment Break', 'Enjoy snacks and drinks'),
(32, '15:30:00', 'Wrap-up', 'Showcase robots and celebrate');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(8,
'STEM Coding Kickoff',
'Start the year with a STEM Coding Kickoff event in Birmingham. Volunteers will guide children through basic coding exercises using Scratch and share insights about careers in technology. This event promotes digital literacy and inspires future innovators.',
'Coding Exercises: Help children complete Scratch challenges; Mentorship: Share experiences and answer questions; Career Talk: Introduce STEM career paths',
'Laptops, Scratch materials, refreshments',
'Basic coding knowledge, enthusiasm, comfortable clothing',
'Improved digital literacy, increased interest in STEM careers, and empowered youth.',
'2026-01-21', '13:00:00', '16:00:00', '03:00:00',
'Birmingham', 'B1 1AA', 'Tech Hub',
20, 'event-images/code.jpg', 52.4862, -1.8904);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(33, '13:00:00', 'Arrival & Setup', 'Meet at Tech Hub and prepare materials'),
(33, '13:15:00', 'Coding Begins', 'Guide children through exercises'),
(33, '15:00:00', 'Refreshment Break', 'Enjoy snacks and drinks'),
(33, '15:30:00', 'Career Talk', 'Share insights and answer questions');


-- Blood Donation Drive (Cause 9)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(9,
'Give Life London',
'Assist in organizing a blood donation event at City Hall. Volunteers will register donors, provide refreshments, and ensure a smooth experience. This event helps increase the local blood supply and save lives.',
'Registration: Sign in donors and verify info; Support: Guide donors through the process; Refreshments: Serve snacks and drinks; Wrap-up: Organize materials and thank participants',
'Registration forms, refreshments, signage',
'Friendly attitude, organized mindset, comfortable clothing',
'Increased blood supply, life-saving donations, and stronger community health support.',
'2025-12-13', '09:00:00', '13:00:00', '04:00:00',
'London', 'E8 9AB', 'City Hall',
25, 'event-images/blood-donation.jpg', 51.5450, -0.0600);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(34, '09:00:00', 'Setup', 'Prepare registration area and refreshments'),
(34, '09:15:00', 'Event Begins', 'Register and support donors'),
(34, '12:00:00', 'Refreshment Break', 'Serve snacks and drinks'),
(34, '12:30:00', 'Wrap-up', 'Organize materials and thank donors');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(9,
'Heroes in Leeds: Blood Drive',
'Help with donor registration and refreshments at the Community Centre. Volunteers will guide donors, serve snacks, and ensure a welcoming environment. This event supports life-saving blood donations.',
'Registration: Sign in donors and verify info; Support: Guide donors through the process; Refreshments: Serve snacks and drinks; Wrap-up: Organize materials and thank participants',
'Registration forms, refreshments, signage',
'Organized mindset, friendly attitude, comfortable clothing',
'Life-saving donations, increased blood supply, and stronger community health support.',
'2025-12-16', '10:00:00', '14:00:00', '04:00:00',
'Leeds', 'LS8 6AA', 'Community Centre',
20, 'event-images/blood-donation2.jpg', 53.8200, -1.5200);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(35, '10:00:00', 'Setup', 'Prepare registration area and refreshments'),
(35, '10:15:00', 'Event Begins', 'Register and support donors'),
(35, '13:00:00', 'Refreshment Break', 'Serve snacks and drinks'),
(35, '13:30:00', 'Wrap-up', 'Organize materials and thank donors');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(9,
'Birmingham Blood Donation Day',
'Assist in organizing a blood donation event at City Hall. Volunteers will register donors, provide refreshments, and ensure a smooth experience. This event helps increase the local blood supply and save lives.',
'Registration: Sign in donors and verify info; Support: Guide donors through the process; Refreshments: Serve snacks and drinks; Wrap-up: Organize materials and thank participants',
'Registration forms, refreshments, signage',
'Friendly attitude, organized mindset, comfortable clothing',
'Increased blood supply, life-saving donations, and stronger community health support.',
'2025-12-29', '09:00:00', '13:00:00', '04:00:00',
'Birmingham', 'B2 4QA', 'City Hall',
25, 'event-images/blood-donation3.jpg', 52.4790, -1.9020);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(36, '09:00:00', 'Setup', 'Prepare registration area and refreshments'),
(36, '09:15:00', 'Event Begins', 'Register and support donors'),
(36, '12:00:00', 'Refreshment Break', 'Serve snacks and drinks'),
(36, '12:30:00', 'Wrap-up', 'Organize materials and thank donors');

-- Disaster Relief Aid (Cause 10)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(10,
'London Relief Kit Assembly',
'Join us at the Relief Centre to assemble emergency kits for disaster victims. Volunteers will pack supplies, label boxes, and prepare kits for distribution. This event supports rapid response and recovery efforts.',
'Packing: Organize supplies into kits; Labeling: Mark boxes with contents; Inventory: Track quantities; Wrap-up: Prepare kits for transport',
'Packing materials, labels, refreshments',
'Able to lift boxes, organized mindset, comfortable clothing',
'Faster disaster response, improved aid delivery, and stronger community resilience.',
'2025-12-14', '10:00:00', '13:00:00', '03:00:00',
'London', 'E9 1AB', 'Relief Centre',
30, 'event-images/releif-rally.jpg', 51.5450, -0.0450);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(37, '10:00:00', 'Setup', 'Prepare packing area and materials'),
(37, '10:15:00', 'Assembly Begins', 'Pack and label kits'),
(37, '12:00:00', 'Refreshment Break', 'Enjoy snacks and drinks'),
(37, '12:30:00', 'Wrap-up', 'Organize kits for transport');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(10,
'Leeds Emergency Shelter Setup',
'Help set up temporary shelters at the Relief Operations Hub. Volunteers will assemble tents, arrange bedding, and prepare spaces for displaced families. This event improves readiness and comfort during emergencies.',
'Assembly: Set up tents and shelters; Bedding: Arrange sleeping areas; Organization: Prepare layout for families; Wrap-up: Review setup and safety',
'Tents, bedding, tools, refreshments',
'Physically fit, organized mindset, comfortable clothing',
'Improved disaster readiness, safer temporary housing, and stronger emergency response.',
'2025-12-17', '08:00:00', '12:00:00', '04:00:00',
'Leeds', 'LS9 7AA', 'Relief Operations Hub',
25, 'event-images/shelter-setup.jpg', 53.8000, -1.5200);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(38, '08:00:00', 'Setup', 'Prepare shelter materials'),
(38, '08:15:00', 'Assembly Begins', 'Set up tents and bedding'),
(38, '11:00:00', 'Refreshment Break', 'Enjoy snacks and drinks'),
(38, '11:30:00', 'Wrap-up', 'Review setup and safety');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(10,
'Relief Rally Manchester',
'Join us at the Relief Centre to assemble emergency kits for disaster victims. Volunteers will pack supplies, label boxes, and prepare kits for distribution. This event supports rapid response and recovery efforts.',
'Packing: Organize supplies into kits; Labeling: Mark boxes with contents; Inventory: Track quantities; Wrap-up: Prepare kits for transport',
'Packing materials, labels, refreshments',
'Able to lift boxes, organized mindset, comfortable clothing',
'Faster disaster response, improved aid delivery, and stronger community resilience.',
'2025-12-31', '10:00:00', '13:00:00', '03:00:00',
'Manchester', 'M3 4AB', 'Relief Centre',
30, 'event-images/aid-in-action.jpg', 53.4800, -2.2500);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(39, '10:00:00', 'Setup', 'Prepare packing area and materials'),
(39, '10:15:00', 'Assembly Begins', 'Pack and label kits'),
(39, '12:00:00', 'Refreshment Break', 'Enjoy snacks and drinks'),
(39, '12:30:00', 'Wrap-up', 'Organize kits for transport');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(10,
'Aid in Action: Livingston',
'Distribute essential supplies to affected families at the Community Relief Centre. Volunteers will load trucks, hand out kits, and support logistics. This event ensures timely aid delivery and community recovery.',
'Loading: Organize supplies for transport; Distribution: Hand out kits to families; Support: Assist with logistics and coordination; Wrap-up: Review delivery and feedback',
'Relief kits, transport materials, refreshments',
'Organized mindset, friendly attitude, comfortable clothing',
'Timely aid delivery, improved disaster recovery, and stronger community support.',
'2025-12-21', '09:00:00', '13:00:00', '04:00:00',
'Livingston', 'EH54 0AA', 'Community Relief Centre',
25, 'event-images/releif-rally.jpg', 55.8820, -3.5050);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(40, '09:00:00', 'Setup', 'Prepare supplies and logistics'),
(40, '09:15:00', 'Distribution Begins', 'Hand out kits and support families'),
(40, '12:00:00', 'Refreshment Break', 'Enjoy snacks and drinks'),
(40, '12:30:00', 'Wrap-up', 'Review delivery and feedback');

INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(10,
'Emergency Kit Assembly',
'Join our Emergency Kit Assembly event in Edinburgh to prepare essential supplies for disaster relief. Volunteers will pack kits with food, hygiene items, and first aid materials to support families during emergencies.',
'Packing: Assemble emergency kits with essential items; Labeling: Mark boxes for distribution; Inventory: Track supplies for logistics',
'Packing materials, gloves, refreshments',
'Able to lift boxes, comfortable clothing, reusable water bottle',
'Faster disaster response, improved preparedness, and support for affected families.',
'2025-10-25', '10:00:00', '13:00:00', '03:00:00',
'Edinburgh', 'EH1 1YZ', 'Relief Centre',
30, '', 55.9533, -3.1883);

INSERT INTO EventSchedule (EventID, Time, Title, Description) VALUES
(41, '10:00:00', 'Arrival & Registration', 'Sign in and receive instructions'),
(41, '10:15:00', 'Packing Begins', 'Assemble and label kits'),
(41, '11:30:00', 'Refreshment Break', 'Enjoy provided snacks and drinks'),
(41, '12:30:00', 'Wrap-up', 'Finalize inventory and prepare for dispatch');


-- Dummy Data for Users
INSERT INTO User (Email, Password, FirstName, LastName)
VALUES
  ('a@test.com', '12345678', 'Alice', 'Smith');

-- Dummy Data for Teams
INSERT INTO Team (Name, Description, Department, Capacity, OwnerUserID, JoinCode, IsActive)
VALUES
('Alpha Innovators', 'Product development team focused on emerging technologies.', 'R&D', 12, 1, 'A1B2C3D4', 1),
('Beta Builders', 'Team responsible for backend infrastructure and API management.', 'Engineering', 10, 1, 'B3C4D5E6', 1),
('Creative Crew', 'Design team creating UX/UI assets and branding materials.', 'Design', 8, 1, 'C5D6E7F8', 1),
('Delta Data', 'Analytics team working on data modeling and performance metrics.', 'Data Science', 9, 1, 'D7E8F9G0', 1),
('Echo Executives', 'Leadership group coordinating company-wide strategy.', 'Management', 5, 1, 'E9F0G1H2', 1)