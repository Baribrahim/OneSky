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
	RequirementsProvided VARCHAR(2000) NOT NULL,
    RequirementsBring VARCHAR(2000) NOT NULL,
    Schedule varchar(2000) not null,
    ExpectedImpact varchar(2000) not null,
    Date date not null,
    StartTime time not null,
    EndTime time not null,
    Duration time not null,
    LocationCity varchar(255) not null,
    LocationPostcode varchar(10) not null,
    Address varchar(255) not null,
    Capacity int not null,
    Image_path varchar(255),
    Latitude DECIMAL(9,6) NOT NULL,
    Longitude DECIMAL(9,6) NOT NULL
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
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, Schedule, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES

(1,
'Thames Riverside Cleanup',
'Join our monthly Thames cleanup initiative! Help protect London’s vital waterway ecosystem while connecting with like-minded volunteers. This hands-on conservation effort improves local wildlife habitats and water quality. Volunteers will work together to remove litter, document wildlife, and collect data on pollution trends. By participating, you’ll contribute to a cleaner riverbank, support biodiversity, and raise awareness about the importance of sustainable practices. Whether you’re passionate about the environment or simply want to make a positive impact, this event offers a rewarding experience for all.',
'Litter Collection: Remove plastic bottles, cans, and debris from the riverbank; Wildlife Documentation: Record wildlife sightings and photograph marine life; Data Collection: Log types and quantities of litter to track pollution trends; Community Engagement: Raise awareness about river conservation',
'Safety equipment & gloves, litter pickers & bags, lunch & refreshments, transport from London',
'Weather-appropriate clothing, waterproof boots, sun hat & sunscreen, water bottle',
'09:00 Arrival & Registration – Meet at South Bank, sign in, and receive equipment; 09:30 Cleanup Begins – Start litter collection and wildlife documentation; 12:00 Lunch & Networking – Provided lunch and connect with fellow volunteers; 13:00 Wrap-up – Final collection tally and return transport',
'Cleaner riverbank, improved biodiversity, and stronger community engagement.',
'2025-12-05', '09:00:00', '13:00:00', '04:00:00',
'London', 'E14 5HQ', 'Thames Riverside Park',
40, 'event-images/river.jpg', 51.5074, -0.0275),


(1,
'Leeds Canal Cleanup',
'Join our Leeds canal cleanup initiative! This event is dedicated to improving the health and beauty of Leeds waterways while fostering community involvement. Volunteers will work together to remove litter, sort recyclables, and monitor wildlife along the canal paths. By participating, you’ll help create safer, cleaner spaces for pedestrians and wildlife, and raise awareness about the importance of protecting local ecosystems.',
'Litter Collection: Remove plastic bottles, cans, and debris from canal paths; Recycling Sorting: Separate recyclables from general waste; Wildlife Observation: Note any wildlife sightings and report unusual findings; Community Awareness: Engage with locals about canal conservation',
'Trash bags, gloves, litter pickers, refreshments, recycling bins',
'Comfortable walking shoes, weather-appropriate clothing, reusable water bottle',
'10:00 Arrival & Registration – Meet at Leeds Canal Dock, sign in, and receive equipment; 10:15 Cleanup Begins – Start litter collection and recycling sorting; 12:00 Refreshment Break – Enjoy provided snacks and drinks; 12:30 Wrap-up – Final collection tally and group photo',
'Cleaner canal paths, improved safety for pedestrians, and increased community awareness about environmental care.',
'2025-12-08', '10:00:00', '13:00:00', '03:00:00',
'Leeds', 'LS1 4AB', 'Leeds Canal Dock',
30, 'event-images/Canal-clean.jpg', 53.7940, -1.5476),


(1,
'Livingston Park Cleanup',
'Help restore Livingston’s beautiful green spaces by joining our park cleanup initiative. This event focuses on improving public areas for families and wildlife while fostering community spirit. Volunteers will remove litter, plant flowers, and sort recyclables to enhance the park’s natural beauty. By taking part, you’ll contribute to a cleaner, safer environment and help promote biodiversity in the local area.',
'Litter Collection: Remove plastic, cans, and other waste from park grounds; Flower Planting: Add color and biodiversity by planting seasonal flowers; Recycling Sorting: Separate recyclables from general waste; Wildlife Observation: Record sightings of birds and small mammals to monitor park health',
'Trash bags, gloves, litter pickers, refreshments, flower seedlings for planting',
'Comfortable outdoor clothing, sturdy shoes, reusable water bottle, gardening gloves (optional)',
'09:00 Arrival & Registration – Meet at Almondvale Park entrance, sign in, and receive equipment; 09:15 Cleanup Begins – Start litter collection and recycling sorting; 10:30 Flower Planting – Work together to plant flowers in designated areas; 11:30 Refreshment Break – Enjoy provided snacks and drinks; 12:00 Wrap-up – Final collection tally and group photo',
'Cleaner and safer park environment, improved biodiversity through flower planting, and stronger community engagement.',
'2025-12-12', '09:00:00', '12:00:00', '03:00:00',
'Livingston', 'EH54 6AA', 'Almondvale Park',
25, 'event-images/park.jpg', 55.8865, -3.5210),

(1,
'Coastal Care Day',
'Join us for a day dedicated to cleaning Portobello Beach and protecting marine life. This event helps reduce ocean pollution and creates a safer environment for wildlife and beachgoers. Volunteers will collect litter, sort recyclables, and monitor coastal wildlife. By participating, you’ll help preserve the natural beauty of the beach and raise awareness about reducing plastic waste and protecting marine ecosystems.',
'Litter Collection: Remove plastic, cans, and other waste from the beach; Recycling Sorting: Separate recyclables from general waste; Wildlife Monitoring: Record sightings of seabirds and marine life; Awareness Campaign: Engage with visitors about reducing plastic use and protecting coastal ecosystems',
'Trash bags, gloves, litter pickers, refreshments, recycling bins',
'Weather-appropriate clothing, waterproof boots, reusable water bottle, sun protection (hat & sunscreen)',
'09:00 Arrival & Registration – Meet at Portobello Beach entrance, sign in, and receive equipment; 09:15 Cleanup Begins – Start litter collection and recycling sorting; 11:00 Refreshment Break – Enjoy provided snacks and drinks; 11:30 Wrap-up – Final collection tally and group photo',
'Cleaner beach, reduced marine pollution, improved biodiversity, and increased public awareness about ocean conservation.',
'2025-11-22', '09:00:00', '12:00:00', '03:00:00',
'Edinburgh', 'EH15 1HX', 'Portobello Beach',
40, 'event-images/beach.jpg', 55.9533, -3.1193),


(1,
'Brighton Beach Cleanup',
'Join our January Brighton Beach Cleanup to help remove litter and protect coastal wildlife. Volunteers will work together to clean the shoreline, sort recyclables, and raise awareness about ocean conservation. This event promotes environmental stewardship and community engagement.',
'Litter Collection: Remove plastic, cans, and debris from the beach; Recycling Sorting: Separate recyclables from general waste; Wildlife Monitoring: Record sightings of seabirds and marine life; Awareness Campaign: Engage with visitors about reducing plastic use',
'Trash bags, gloves, litter pickers, refreshments, recycling bins',
'Weather-appropriate clothing, waterproof boots, reusable water bottle, sun protection',
'09:00 Arrival & Registration – Meet at Brighton Pier entrance, sign in, and receive equipment; 09:15 Cleanup Begins – Start litter collection and recycling sorting; 11:00 Refreshment Break – Enjoy provided snacks and drinks; 11:30 Wrap-up – Final collection tally and group photo',
'Cleaner beach, reduced marine pollution, improved biodiversity, and increased public awareness about ocean conservation.',
'2026-01-01', '09:00:00', '12:00:00', '03:00:00',
'Brighton', 'BN2 1TW', 'Brighton Pier',
35, 'event-images/beach.jpg', 50.8198, -0.1367);


-- Tree Planting (Cause 2)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, Schedule, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(2,
'Leeds Green Belt Planting',
'Join us in restoring Leeds’ green belt by planting trees and improving local biodiversity. This event focuses on creating healthier ecosystems and combating climate change. Volunteers will plant saplings, mulch soil, and learn about sustainable forestry practices. By participating, you’ll help improve air quality and create greener spaces for future generations.',
'Tree Planting: Dig holes and plant saplings; Mulching: Spread mulch to protect roots and retain moisture; Watering: Ensure newly planted trees are hydrated; Environmental Education: Learn about the benefits of urban forestry and biodiversity',
'Tree saplings, mulch, gardening tools, gloves, refreshments',
'Comfortable outdoor clothing, sturdy shoes, reusable water bottle',
'09:00 Arrival & Registration – Meet at Roundhay Park entrance, sign in, and receive equipment; 09:15 Tree Planting – Begin planting saplings and mulching; 11:00 Refreshment Break – Enjoy provided snacks and drinks; 11:30 Wrap-up – Water trees and review progress',
'Improved air quality, enhanced biodiversity, and stronger community involvement in environmental sustainability.',
'2025-12-09', '09:00:00', '12:00:00', '03:00:00',
'Leeds', 'LS6 2AB', 'Roundhay Park',
30, 'event-images/tree.jpg', 53.8381, -1.4933),

(2,
'Livingston Woodland Project',
'Help expand Livingston’s woodland area by planting trees and supporting local wildlife habitats. This event aims to increase green coverage and promote biodiversity. Volunteers will plant and water trees while learning about the importance of sustainable land management.',
'Tree Planting: Dig holes and plant saplings; Watering: Hydrate newly planted trees; Soil Preparation: Prepare ground for optimal growth; Community Education: Discuss benefits of woodland expansion',
'Tree saplings, gardening tools, gloves, refreshments',
'Outdoor clothing, sturdy boots, reusable water bottle',
'10:00 Arrival & Registration – Meet at Deans Community Woodland entrance, sign in, and receive equipment; 10:15 Tree Planting – Begin planting and watering trees; 11:30 Refreshment Break – Enjoy provided snacks and drinks; 12:30 Wrap-up – Final watering and group photo',
'Enhanced biodiversity, improved soil health, and increased green spaces for community recreation.',
'2025-12-13', '10:00:00', '13:00:00', '03:00:00',
'Livingston', 'EH54 7AA', 'Deans Community Woodland',
25, 'event-images/tree2.jpg', 55.9000, -3.5500),

(2,
'Manchester Tree Planting',
'Join us in creating greener urban spaces by planting trees in Manchester’s parks. This event helps combat air pollution and provides shade and habitats for wildlife. Volunteers will dig, plant, and water trees while learning about the role of trees in climate resilience.',
'Digging: Prepare soil and create planting holes; Tree Planting: Position and secure saplings; Watering: Hydrate newly planted trees; Mulching: Apply mulch for soil protection',
'Tree saplings, mulch, gardening tools, gloves, refreshments',
'Comfortable outdoor clothing, sturdy shoes, reusable water bottle',
'10:00 Arrival & Registration – Meet at Whitworth Park entrance, sign in, and receive equipment; 10:15 Tree Planting – Begin digging and planting; 11:30 Refreshment Break – Enjoy provided snacks and drinks; 12:30 Wrap-up – Water trees and review progress',
'Greener urban spaces, improved air quality, and increased community participation in environmental care.',
'2025-12-30', '10:00:00', '13:00:00', '03:00:00',
'Manchester', 'M1 2AB', 'Whitworth Park',
30, 'event-images/woodland.jpg', 53.4648, -2.2294),

(2,
'Roots for the Future',
'Join us in planting trees at Victoria Park to create a greener, healthier environment for London. This event focuses on combating climate change and improving urban biodiversity. Volunteers will dig, plant, and water trees while learning about sustainable forestry practices.',
'Digging: Prepare soil and create planting holes; Tree Planting: Position and secure saplings; Watering: Hydrate newly planted trees; Mulching: Apply mulch for soil protection',
'Tree saplings, mulch, gardening tools, gloves, refreshments',
'Comfortable outdoor clothing, sturdy shoes, reusable water bottle',
'10:00 Arrival & Registration – Meet at Victoria Park entrance, sign in, and receive equipment; 10:15 Tree Planting – Begin digging and planting; 11:30 Refreshment Break – Enjoy provided snacks and drinks; 12:30 Wrap-up – Water trees and review progress',
'Greener urban spaces, improved air quality, and stronger community engagement in sustainability.',
'2025-11-06', '10:00:00', '13:00:00', '03:00:00',
'London', 'E3 5TB', 'Victoria Park',
35, 'event-images/roots.jpg', 51.5363, -0.0330);

-- Food Bank Support (Cause 3)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, Schedule, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(3,
'London Food Sorting',
'Join us at East End Food Bank to sort and pack food donations for families in need. This event ensures that essential supplies are organized and distributed efficiently. Volunteers will label, pack, and prepare food parcels while learning about food security challenges in London.',
'Labeling: Mark boxes with correct contents; Packing: Organize food items into parcels; Quality Check: Ensure items are safe and within date; Distribution Prep: Arrange parcels for delivery',
'Packing materials, gloves, refreshments',
'Comfortable clothing, closed-toe shoes, ability to lift boxes',
'09:00 Arrival & Registration – Sign in and receive instructions; 09:15 Sorting Begins – Label and pack food items; 11:00 Refreshment Break – Enjoy provided snacks and drinks; 11:30 Wrap-up – Organize parcels for distribution',
'Faster food distribution, reduced waste, and improved support for vulnerable families.',
'2025-12-07', '09:00:00', '12:00:00', '03:00:00',
'London', 'E1 6AB', 'East End Food Bank',
20, 'event-images/food-bank.jpg', 51.5200, -0.0710),

(3,
'Leeds Food Drive',
'Support Leeds Community Kitchen by assisting in food collection and packing. Volunteers will sort donations, pack parcels, and help prepare supplies for families in need. This event promotes community solidarity and ensures timely food distribution.',
'Sorting: Organize donated food items; Packing: Prepare parcels for families; Quality Check: Inspect items for safety; Inventory: Record quantities for tracking',
'Packing materials, gloves, refreshments',
'Organized mindset, comfortable clothing, reusable water bottle',
'10:00 Arrival & Registration – Sign in and receive instructions; 10:15 Sorting Begins – Organize and pack food items; 11:30 Refreshment Break – Enjoy provided snacks and drinks; 12:30 Wrap-up – Finalize parcels and inventory',
'Support for families in need, improved food security, and stronger community engagement.',
'2025-12-10', '10:00:00', '13:00:00', '03:00:00',
'Leeds', 'LS2 8AA', 'Leeds Community Kitchen',
25, 'event-images/foodbank2.jpg', 53.8010, -1.5470),

(3,
'Livingston Food Hub',
'Join us at Livingston Food Hub to help distribute food parcels to families in need. Volunteers will pack, organize, and assist with handing out supplies. This event strengthens community support and ensures timely access to essential resources.',
'Packing: Prepare food parcels; Sorting: Organize items by category; Distribution: Assist in handing out parcels; Inventory: Track supplies for future planning',
'Packing materials, gloves, refreshments',
'Friendly attitude, comfortable clothing, reusable water bottle',
'11:00 Arrival & Registration – Sign in and receive instructions; 11:15 Packing Begins – Organize and prepare parcels; 12:30 Refreshment Break – Enjoy provided snacks and drinks; 13:00 Wrap-up – Assist with distribution and inventory',
'Improved food security, reduced hunger, and stronger community connections.',
'2025-12-14', '11:00:00', '14:00:00', '03:00:00',
'Livingston', 'EH54 8AA', 'Livingston Food Hub',
20, 'event-images/foodbank3.jpg', 55.8990, -3.5200),

(3,
'January Food Parcel Prep',
'Support our January food parcel preparation event in Glasgow to help families in need. Volunteers will sort donations, pack parcels, and assist with organizing supplies for distribution. This event strengthens food security and promotes community care.',
'Sorting: Organize donated food items; Packing: Prepare parcels for families; Quality Check: Inspect items for safety; Inventory: Record quantities for tracking',
'Packing materials, gloves, refreshments',
'Comfortable clothing, closed-toe shoes, reusable water bottle',
'10:00 Arrival & Registration – Sign in and receive instructions; 10:15 Sorting Begins – Organize and pack food items; 11:30 Refreshment Break – Enjoy provided snacks and drinks; 12:30 Wrap-up – Finalize parcels and inventory',
'Support for families in need, improved food security, and stronger community engagement.',
'2026-01-14', '10:00:00', '13:00:00', '03:00:00',
'Glasgow', 'G1 1XX', 'Glasgow Community Kitchen',
25, 'event-images/foodbank3.jpg', 55.8607, -4.2518);


-- Homeless Outreach (Cause 4)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, Schedule, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(4,
'London Winter Care Drive',
'Help distribute warm clothes and blankets to homeless individuals at Hope Shelter. Volunteers will pack care packages and assist with distribution to ensure vulnerable people stay safe during winter.',
'Packing: Prepare care packages with warm clothes and blankets; Distribution: Hand out packages to individuals; Inventory: Track remaining supplies; Community Support: Engage with recipients respectfully',
'Warm clothes, blankets, hygiene items, refreshments',
'Compassionate attitude, comfortable clothing, reusable water bottle',
'12:00 Arrival & Registration – Sign in and receive instructions; 12:15 Packing Begins – Prepare care packages; 13:30 Distribution – Hand out packages to recipients; 14:30 Wrap-up – Organize remaining supplies',
'Better winter safety, improved quality of life, and stronger community support for vulnerable individuals.',
'2025-12-08', '12:00:00', '15:00:00', '03:00:00',
'London', 'E2 7AB', 'Hope Shelter',
30, '', 51.5290, -0.0700),

(4,
'Leeds Hot Meal Service',
'Join us at St George’s Centre to serve hot meals to homeless individuals. Volunteers will assist with cooking, plating, and serving food while creating a welcoming environment for those in need.',
'Cooking: Help prepare nutritious meals; Serving: Plate and distribute meals to guests; Clean-up: Assist with post-meal cleaning; Guest Engagement: Provide friendly conversation and support',
'Ingredients, utensils, gloves, refreshments',
'Basic kitchen skills, comfortable clothing, reusable water bottle',
'13:00 Arrival & Registration – Sign in and receive instructions; 13:15 Meal Prep – Assist with cooking and plating; 14:00 Serving – Distribute meals to guests; 15:00 Wrap-up – Clean up and thank volunteers',
'Improved nutrition, enhanced dignity, and stronger community support for homeless individuals.',
'2025-12-11', '13:00:00', '16:00:00', '03:00:00',
'Leeds', 'LS3 1AA', 'St George’s Centre',
25, 'event-images/hot-meal.jpg', 53.8015, -1.5580),

(4,
'Livingston Care Package Prep',
'Support Livingston’s homeless outreach by preparing hygiene kits for distribution. Volunteers will sort items, pack kits, and help organize supplies for future events.',
'Sorting: Organize hygiene items; Packing: Assemble care kits; Inventory: Track supplies; Teamwork: Collaborate with other volunteers',
'Hygiene items, packing materials, gloves, refreshments',
'Organized mindset, comfortable clothing, reusable water bottle',
'10:00 Arrival & Registration – Sign in and receive instructions; 10:15 Packing Begins – Assemble hygiene kits; 11:30 Refreshment Break – Enjoy provided snacks and drinks; 12:30 Wrap-up – Organize supplies and clean up',
'Improved hygiene access, better health outcomes, and increased support for vulnerable individuals.',
'2025-12-15', '10:00:00', '13:00:00', '03:00:00',
'Livingston', 'EH54 9AA', 'Community Hall',
20, 'event-images/care-package2.jpg', 55.9005, -3.5300),

(4,
'Birmingham Homeless Care Drive',
'Join us at Hope Shelter in Birmingham to distribute care packages to homeless individuals. Volunteers will pack and hand out essential items while offering warmth and compassion to those in need.',
'Packing: Assemble care packages with warm clothes and hygiene items; Distribution: Hand out packages to recipients; Guest Engagement: Provide friendly conversation and support; Inventory: Track supplies for future outreach',
'Warm clothes, hygiene items, gloves, refreshments',
'Compassionate attitude, comfortable clothing, reusable water bottle',
'12:00 Arrival & Registration – Sign in and receive instructions; 12:15 Packing Begins – Assemble care packages; 13:30 Distribution – Hand out packages to recipients; 14:30 Wrap-up – Organize remaining supplies and clean up',
'Improved quality of life, increased dignity, and stronger community support for homeless individuals.',
'2025-12-28', '12:00:00', '15:00:00', '03:00:00',
'Birmingham', 'B1 1AA', 'Hope Shelter',
30, '', 52.4790, -1.9025);

-- Animal Shelter Assistance (Cause 5)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, Schedule, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(5, 'London Pet Adoption Day',
'Support Happy Paws Shelter by assisting with a pet adoption event. Volunteers will help guide visitors, handle pets, and ensure a smooth adoption process. This event promotes responsible pet ownership and helps animals find loving homes.',
'Pet Handling: Assist with walking and calming animals; Visitor Guidance: Help families meet adoptable pets; Adoption Support: Provide information and assist with paperwork',
'Leashes, pet supplies, refreshments, adoption forms',
'Comfortable with animals, friendly attitude, reusable water bottle',
'11:00 Arrival & Registration – Meet at Happy Paws Shelter, receive instructions; 11:15 Event Begins – Guide visitors and assist with pet handling; 13:00 Refreshment Break – Enjoy provided snacks and drinks; 14:30 Wrap-up – Final adoptions and cleanup',
'Increased pet adoptions, improved shelter visibility, and stronger community engagement.',
'2025-12-09', '11:00:00', '15:00:00', '04:00:00', 'London', 'E3 4AB', 'Happy Paws Shelter', 15, 'event-images/adopt.jpg', 51.5360, -0.0330),

(5, 'Livingston Shelter Support',
'Join us at Livingston Animal Centre to assist with daily shelter tasks. Volunteers will walk dogs, clean enclosures, and help maintain a safe and healthy environment for animals.',
'Dog Walking: Take dogs for exercise and socialization; Cleaning: Maintain cleanliness of cages and common areas; Feeding: Assist with feeding routines',
'Leashes, cleaning supplies, pet food, refreshments',
'Physically active, comfortable with animals, reusable water bottle',
'10:00 Arrival & Registration – Meet at Livingston Animal Centre, receive instructions; 10:15 Tasks Begin – Walk dogs and clean enclosures; 11:30 Refreshment Break – Enjoy provided snacks and drinks; 12:30 Wrap-up – Final cleaning and group photo',
'Improved shelter operations, healthier animals, and increased volunteer support.',
'2025-12-16', '10:00:00', '13:00:00', '03:00:00', 'Livingston', 'EH54 5AA', 'Livingston Animal Centre', 15, 'event-images/shelter.jpg', 55.8860, -3.5200),

(5, 'Paws & Play Adoption Fair',
'Help families meet adoptable pets at Happy Paws Shelter. Volunteers will guide visitors, handle pets, and support the adoption process during this fun and interactive event.',
'Visitor Guidance: Welcome and assist families; Pet Handling: Ensure animals are calm and safe; Adoption Support: Provide information and help with forms',
'Leashes, refreshments, adoption forms, pet supplies',
'Comfortable with animals, friendly attitude, reusable water bottle',
'11:00 Arrival & Registration – Meet at Happy Paws Shelter, receive instructions; 11:15 Event Begins – Guide visitors and assist with pet handling; 13:00 Refreshment Break – Enjoy provided snacks and drinks; 14:30 Wrap-up – Final adoptions and cleanup',
'More pets find loving homes, increased shelter visibility, and stronger community engagement.',
'2025-11-09', '11:00:00', '15:00:00', '04:00:00', 'London', 'E3 4AB', 'Happy Paws Shelter', 15, 'event-images/adopt.jpg', 51.5360, -0.0330),

(5, 'Furry Friends Care Day',
'Support Leeds Animal Rescue by assisting with feeding and cleaning tasks. Volunteers will help maintain a clean and nurturing environment for rescued animals.',
'Feeding: Provide food and water to animals; Cleaning: Sanitize cages and common areas; Enrichment: Help with toys and comfort items',
'Pet food, cleaning supplies, gloves, refreshments',
'Animal-friendly attitude, comfortable clothing, reusable water bottle',
'09:00 Arrival & Registration – Meet at Leeds Animal Rescue, receive instructions; 09:15 Tasks Begin – Feed animals and clean enclosures; 11:00 Refreshment Break – Enjoy provided snacks and drinks; 11:30 Wrap-up – Final cleaning and group photo',
'Better animal welfare, cleaner shelter environment, and increased volunteer support.',
'2025-11-12', '09:00:00', '12:00:00', '03:00:00', 'Leeds', 'LS4 2AA', 'Leeds Animal Rescue', 20, 'event-images/pets.jpg', 53.8090, -1.5800);

-- Senior Care Visits (Cause 6)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, Schedule, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(6, 'London Senior Social',
'Spend time with elderly residents at Rosewood Care Home. Volunteers will engage in games, reading, and conversation to brighten the day of seniors and reduce loneliness.',
'Games: Play board games and cards; Reading: Read books and newspapers aloud; Chatting: Share stories and listen to residents',
'Games, books, refreshments',
'Friendly and patient attitude, comfortable clothing',
'14:00 Arrival & Registration – Meet at Rosewood Care Home, receive instructions; 14:15 Activities Begin – Engage in games and reading; 15:30 Refreshment Break – Enjoy snacks with residents; 16:30 Wrap-up – Final conversations and group photo',
'Reduced loneliness, improved mental well-being, and stronger intergenerational connections.',
'2025-12-10', '14:00:00', '17:00:00', '03:00:00', 'London', 'E5 6AB', 'Rosewood Care Home', 12, 'event-images/seniors.jpg', 51.5580, -0.0570),

(6, 'Leeds Music Afternoon',
'Bring joy to seniors at Meadow View Care Home through music. Volunteers will play instruments, sing, and create a lively atmosphere that promotes mental wellness.',
'Playing Instruments: Perform familiar tunes; Singing: Lead sing-alongs with residents; Interaction: Encourage participation and conversation',
'Musical instruments, song sheets, refreshments',
'Musical skills preferred, friendly attitude, reusable water bottle',
'15:00 Arrival & Registration – Meet at Meadow View Care Home, receive instructions; 15:15 Music Begins – Perform and engage with residents; 16:30 Refreshment Break – Enjoy snacks with residents; 17:30 Wrap-up – Final songs and group photo',
'Improved mental health, increased happiness, and stronger community bonds.',
'2025-12-13', '15:00:00', '18:00:00', '03:00:00', 'Leeds', 'LS5 3AA', 'Meadow View Care Home', 10, 'event-images/seniors-music.jpg', 53.8095, -1.5850),

(6, 'Livingston Holiday Card Day',
'Create and deliver holiday cards to seniors at Community Arts Centre. Volunteers will craft personalized messages and spread seasonal cheer to elderly residents.',
'Crafting: Design and decorate holiday cards; Writing: Add thoughtful messages; Delivery: Hand out cards to seniors',
'Craft supplies, card stock, refreshments',
'Creative mindset, friendly attitude, reusable water bottle',
'10:00 Arrival & Registration – Meet at Community Arts Centre, receive instructions; 10:15 Card Making – Craft and write holiday cards; 11:30 Refreshment Break – Enjoy snacks and drinks; 12:30 Wrap-up – Deliver cards and group photo',
'Increased happiness, reduced isolation, and stronger community connections.',
'2025-12-17', '10:00:00', '13:00:00', '03:00:00', 'Livingston', 'EH54 4AA', 'Community Arts Centre', 15, 'event-images/card-day.jpg', 55.8890, -3.5200),

(6,
'New Year Senior Visit',
'Celebrate the New Year by spending time with elderly residents at Manchester Care Home. Volunteers will engage in games, storytelling, and friendly conversations to brighten the day of seniors and reduce loneliness.',
'Games: Play board games and puzzles with residents; Storytelling: Share stories and listen to life experiences; Companionship: Engage in friendly conversation and build connections',
'Games, refreshments, activity materials',
'Friendly attitude, patience, comfortable clothing',
'14:00 Arrival & Welcome – Meet staff and receive instructions; 14:15 Activities Begin – Engage in games and conversations; 15:30 Refreshment Break – Enjoy snacks with residents; 16:30 Wrap-up – Group photo and farewell',
'Reduced loneliness, improved emotional well-being, and stronger intergenerational connections.',
'2026-01-18', '14:00:00', '17:00:00', '03:00:00',
'Manchester', 'M4 5AZ', 'Manchester Care Home',
15, 'event-images/seniors.jpg', 53.4839, -2.2446);


-- Mental Health Awareness (Cause 7)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, Schedule, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(7,
'London Mindfulness Workshop',
'Support mental well-being by assisting in a guided mindfulness session at the Wellness Centre. Volunteers will help set up the space, guide participants through breathing exercises, and distribute wellness materials. This event promotes relaxation and stress reduction in a supportive environment.',
'Setup: Arrange mats and seating; Activity Support: Guide breathing and mindfulness exercises; Materials: Distribute handouts and wellness kits; Engagement: Encourage participation and answer questions',
'Mats, wellness kits, handouts, refreshments',
'Comfortable clothing, good communication skills, calm demeanor',
'10:00 Arrival & Setup – Prepare the space and materials; 10:15 Workshop Begins – Guide mindfulness activities; 12:00 Refreshment Break – Enjoy snacks and drinks; 12:30 Wrap-up – Collect materials and debrief',
'Improved mental well-being, reduced stress, and increased awareness of mindfulness practices.',
'2025-12-11', '10:00:00', '13:00:00', '03:00:00',
'London', 'E6 7AB', 'Wellness Centre',
20, 'event-images/mental-health.jpg', 51.5270, 0.0520),

(7,
'Leeds Mental Health Booth',
'Raise awareness about mental health by running an information booth in City Square. Volunteers will distribute leaflets, engage with visitors, and answer questions about local mental health resources. This event helps reduce stigma and promotes access to support.',
'Booth Setup: Arrange table and materials; Outreach: Distribute leaflets and talk to visitors; Engagement: Answer questions and share resources; Feedback: Collect visitor responses',
'Leaflets, brochures, booth signage, refreshments',
'Friendly attitude, good communication skills, weather-appropriate clothing',
'11:00 Setup – Prepare booth and materials; 11:30 Outreach Begins – Engage with visitors; 14:00 Refreshment Break – Enjoy snacks and drinks; 14:30 Wrap-up – Collect feedback and pack up',
'Increased mental health awareness, reduced stigma, and better access to support services.',
'2025-12-14', '11:00:00', '15:00:00', '04:00:00',
'Leeds', 'LS6 4AA', 'City Square',
15, 'event-images/mindful.jpg', 53.8060, -1.5480),

(7,
'Livingston Stress Relief Day',
'Help organize stress-relief activities at the Community Hall to promote mental wellness. Volunteers will assist with yoga setup, distribute materials, and support participants during relaxation exercises. This event encourages healthy coping strategies and community connection.',
'Setup: Arrange yoga mats and seating; Distribution: Hand out wellness materials; Support: Guide participants through exercises; Engagement: Encourage participation and answer questions',
'Yoga mats, wellness kits, handouts, refreshments',
'Organized mindset, comfortable clothing, friendly attitude',
'09:00 Setup – Prepare space and materials; 09:30 Activities Begin – Support yoga and relaxation sessions; 11:00 Refreshment Break – Enjoy snacks and drinks; 11:30 Wrap-up – Collect materials and debrief',
'Reduced stress levels, improved mental wellness, and stronger community support.',
'2025-12-18', '09:00:00', '12:00:00', '03:00:00',
'Livingston', 'EH54 3AA', 'Community Hall',
20, 'event-images/stress.jpg', 55.8850, -3.5150);

-- STEM Mentorship (Cause 8)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, Schedule, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(8,
'Code & Create',
'Teach basic coding to children at Tech Hub using Scratch. Volunteers will guide exercises, troubleshoot issues, and encourage creativity. This event promotes digital literacy and inspires future tech innovators.',
'Guidance: Help children navigate Scratch; Troubleshooting: Assist with coding errors; Engagement: Encourage creativity and exploration; Wrap-up: Review projects and celebrate progress',
'Laptops, Scratch guides, refreshments',
'Basic coding knowledge, patience, enthusiasm',
'13:00 Setup – Prepare laptops and materials; 13:15 Workshop Begins – Guide Scratch activities; 15:00 Refreshment Break – Enjoy snacks and drinks; 15:30 Wrap-up – Review projects and celebrate',
'Improved digital literacy, increased interest in coding, and empowered young learners.',
'2025-12-12', '13:00:00', '16:00:00', '03:00:00',
'London', 'E7 8AB', 'Tech Hub',
15, 'event-images/code.jpg', 51.5470, 0.0250),

(8,
'Build-a-Bot Challenge',
'Guide students in building simple robots at the Innovation Lab. Volunteers will explain steps, troubleshoot issues, and encourage teamwork. This event fosters hands-on STEM learning and problem-solving skills.',
'Instruction: Explain robot-building steps; Support: Help troubleshoot assembly issues; Engagement: Encourage teamwork and creativity; Wrap-up: Showcase completed robots',
'Robot kits, tools, instruction sheets, refreshments',
'STEM knowledge, teamwork skills, enthusiasm',
'10:00 Setup – Prepare kits and tools; 10:15 Workshop Begins – Guide robot assembly; 12:00 Refreshment Break – Enjoy snacks and drinks; 12:30 Wrap-up – Showcase robots and celebrate',
'Hands-on STEM learning, improved problem-solving, and increased interest in robotics.',
'2025-12-15', '10:00:00', '13:00:00', '03:00:00',
'Leeds', 'LS7 5AA', 'Innovation Lab',
15, 'event-images/build-a-bot.jpg', 53.8120, -1.5400),

(8,
'Livingston STEM Career Talk',
'Share insights into STEM careers at the Science Centre. Volunteers will give talks, answer questions, and inspire students to pursue science and technology fields. This event promotes career awareness and mentorship.',
'Presentation: Share career journeys and advice; Q&A: Answer student questions; Engagement: Encourage interest in STEM fields; Wrap-up: Provide resources and contacts',
'Presentation materials, refreshments',
'STEM professionals preferred, public speaking skills',
'11:00 Setup – Prepare presentation space; 11:15 Career Talks – Share insights and answer questions; 12:30 Wrap-up – Provide resources and contacts',
'Increased STEM awareness, inspired students, and stronger mentorship connections.',
'2025-12-19', '11:00:00', '13:00:00', '02:00:00',
'Livingston', 'EH54 2AA', 'Science Centre',
20, 'event-images/career-talk.jpg', 55.8830, -3.5100),

(8,
'Edinburgh STEM Robotics Workshop',
'Teach kids to build simple robots at Tech Innovation Hub. Volunteers will guide assembly, troubleshoot issues, and encourage exploration. This event promotes hands-on learning and sparks interest in engineering.',
'Assembly: Guide robot building steps; Troubleshooting: Help fix issues; Engagement: Encourage creativity and teamwork; Wrap-up: Showcase completed robots',
'Robot kits, tools, instruction sheets, refreshments',
'Basic robotics knowledge, patience, enthusiasm',
'13:00 Setup – Prepare kits and tools; 13:15 Workshop Begins – Guide robot assembly; 15:00 Refreshment Break – Enjoy snacks and drinks; 15:30 Wrap-up – Showcase robots and celebrate',
'Hands-on STEM learning, increased interest in engineering, and empowered young learners.',
'2025-12-23', '13:00:00', '16:00:00', '03:00:00',
'Edinburgh', 'EH8 9YL', 'Tech Innovation Hub',
15, 'event-images/robotics.jpg', 55.9450, -3.1860),

(8,
'STEM Coding Kickoff',
'Start the year with a STEM Coding Kickoff event in Birmingham. Volunteers will guide children through basic coding exercises using Scratch and share insights about careers in technology. This event promotes digital literacy and inspires future innovators.',
'Coding Exercises: Help children complete Scratch challenges; Mentorship: Share experiences and answer questions; Career Talk: Introduce STEM career paths',
'Laptops, Scratch materials, refreshments',
'Basic coding knowledge, enthusiasm, comfortable clothing',
'13:00 Arrival & Setup – Meet at Tech Hub and prepare materials; 13:15 Coding Begins – Guide children through exercises; 15:00 Refreshment Break – Enjoy snacks and drinks; 15:30 Career Talk – Share insights and answer questions',
'Improved digital literacy, increased interest in STEM careers, and empowered youth.',
'2026-01-21', '13:00:00', '16:00:00', '03:00:00',
'Birmingham', 'B1 1AA', 'Tech Hub',
20, 'event-images/code.jpg', 52.4862, -1.8904);


-- Blood Donation Drive (Cause 9)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, Schedule, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(9,
'Give Life London',
'Assist in organizing a blood donation event at City Hall. Volunteers will register donors, provide refreshments, and ensure a smooth experience. This event helps increase the local blood supply and save lives.',
'Registration: Sign in donors and verify info; Support: Guide donors through the process; Refreshments: Serve snacks and drinks; Wrap-up: Organize materials and thank participants',
'Registration forms, refreshments, signage',
'Friendly attitude, organized mindset, comfortable clothing',
'09:00 Setup – Prepare registration area and refreshments; 09:15 Event Begins – Register and support donors; 12:00 Refreshment Break – Serve snacks and drinks; 12:30 Wrap-up – Organize materials and thank donors',
'Increased blood supply, life-saving donations, and stronger community health support.',
'2025-12-13', '09:00:00', '13:00:00', '04:00:00',
'London', 'E8 9AB', 'City Hall',
25, 'event-images/blood-donation.jpg', 51.5450, -0.0600),

(9,
'Heroes in Leeds: Blood Drive',
'Help with donor registration and refreshments at the Community Centre. Volunteers will guide donors, serve snacks, and ensure a welcoming environment. This event supports life-saving blood donations.',
'Registration: Sign in donors and verify info; Support: Guide donors through the process; Refreshments: Serve snacks and drinks; Wrap-up: Organize materials and thank participants',
'Registration forms, refreshments, signage',
'Organized mindset, friendly attitude, comfortable clothing',
'10:00 Setup – Prepare registration area and refreshments; 10:15 Event Begins – Register and support donors; 13:00 Refreshment Break – Serve snacks and drinks; 13:30 Wrap-up – Organize materials and thank donors',
'Life-saving donations, increased blood supply, and stronger community health support.',
'2025-12-16', '10:00:00', '14:00:00', '04:00:00',
'Leeds', 'LS8 6AA', 'Community Centre',
20, 'event-images/blood-donation2.jpg', 53.8200, -1.5200),

(9,
'Birmingham Blood Donation Day',
'Assist in organizing a blood donation event at City Hall. Volunteers will register donors, provide refreshments, and ensure a smooth experience. This event helps increase the local blood supply and save lives.',
'Registration: Sign in donors and verify info; Support: Guide donors through the process; Refreshments: Serve snacks and drinks; Wrap-up: Organize materials and thank participants',
'Registration forms, refreshments, signage',
'Friendly attitude, organized mindset, comfortable clothing',
'09:00 Setup – Prepare registration area and refreshments; 09:15 Event Begins – Register and support donors; 12:00 Refreshment Break – Serve snacks and drinks; 12:30 Wrap-up – Organize materials and thank donors',
'Increased blood supply, life-saving donations, and stronger community health support.',
'2025-12-29', '09:00:00', '13:00:00', '04:00:00',
'Birmingham', 'B2 4QA', 'City Hall',
25, 'event-images/blood-donation3.jpg', 52.4790, -1.9020);

-- Disaster Relief Aid (Cause 10)
INSERT INTO Event (
  CauseID, Title, About, Activities, RequirementsProvided, RequirementsBring, Schedule, ExpectedImpact,
  Date, StartTime, EndTime, Duration, LocationCity, LocationPostcode, Address,
  Capacity, Image_path, Latitude, Longitude
) VALUES
(10,
'London Relief Kit Assembly',
'Join us at the Relief Centre to assemble emergency kits for disaster victims. Volunteers will pack supplies, label boxes, and prepare kits for distribution. This event supports rapid response and recovery efforts.',
'Packing: Organize supplies into kits; Labeling: Mark boxes with contents; Inventory: Track quantities; Wrap-up: Prepare kits for transport',
'Packing materials, labels, refreshments',
'Able to lift boxes, organized mindset, comfortable clothing',
'10:00 Setup – Prepare packing area and materials; 10:15 Assembly Begins – Pack and label kits; 12:00 Refreshment Break – Enjoy snacks and drinks; 12:30 Wrap-up – Organize kits for transport',
'Faster disaster response, improved aid delivery, and stronger community resilience.',
'2025-12-14', '10:00:00', '13:00:00', '03:00:00',
'London', 'E9 1AB', 'Relief Centre',
30, 'event-images/releif-rally.jpg', 51.5450, -0.0450),

(10,
'Leeds Emergency Shelter Setup',
'Help set up temporary shelters at the Relief Operations Hub. Volunteers will assemble tents, arrange bedding, and prepare spaces for displaced families. This event improves readiness and comfort during emergencies.',
'Assembly: Set up tents and shelters; Bedding: Arrange sleeping areas; Organization: Prepare layout for families; Wrap-up: Review setup and safety',
'Tents, bedding, tools, refreshments',
'Physically fit, organized mindset, comfortable clothing',
'08:00 Setup – Prepare shelter materials; 08:15 Assembly Begins – Set up tents and bedding; 11:00 Refreshment Break – Enjoy snacks and drinks; 11:30 Wrap-up – Review setup and safety',
'Improved disaster readiness, safer temporary housing, and stronger emergency response.',
'2025-12-17', '08:00:00', '12:00:00', '04:00:00',
'Leeds', 'LS9 7AA', 'Relief Operations Hub',
25, 'event-images/shelter-setup.jpg', 53.8000, -1.5200),

(10,
'Relief Rally Manchester',
'Join us at the Relief Centre to assemble emergency kits for disaster victims. Volunteers will pack supplies, label boxes, and prepare kits for distribution. This event supports rapid response and recovery efforts.',
'Packing: Organize supplies into kits; Labeling: Mark boxes with contents; Inventory: Track quantities; Wrap-up: Prepare kits for transport',
'Packing materials, labels, refreshments',
'Able to lift boxes, organized mindset, comfortable clothing',
'10:00 Setup – Prepare packing area and materials; 10:15 Assembly Begins – Pack and label kits; 12:00 Refreshment Break – Enjoy snacks and drinks; 12:30 Wrap-up – Organize kits for transport',
'Faster disaster response, improved aid delivery, and stronger community resilience.',
'2025-12-31', '10:00:00', '13:00:00', '03:00:00',
'Manchester', 'M3 4AB', 'Relief Centre',
30, 'event-images/aid-in-action.jpg', 53.4800, -2.2500),

(10,
'Aid in Action: Livingston',
'Distribute essential supplies to affected families at the Community Relief Centre. Volunteers will load trucks, hand out kits, and support logistics. This event ensures timely aid delivery and community recovery.',
'Loading: Organize supplies for transport; Distribution: Hand out kits to families; Support: Assist with logistics and coordination; Wrap-up: Review delivery and feedback',
'Relief kits, transport materials, refreshments',
'Organized mindset, friendly attitude, comfortable clothing',
'09:00 Setup – Prepare supplies and logistics; 09:15 Distribution Begins – Hand out kits and support families; 12:00 Refreshment Break – Enjoy snacks and drinks; 12:30 Wrap-up – Review delivery and feedback',
'Timely aid delivery, improved disaster recovery, and stronger community support.',
'2025-12-21', '09:00:00', '13:00:00', '04:00:00',
'Livingston', 'EH54 0AA', 'Community Relief Centre',
25, 'event-images/releif-rally.jpg', 55.8820, -3.5050),

(10,
'Emergency Kit Assembly',
'Join our Emergency Kit Assembly event in Edinburgh to prepare essential supplies for disaster relief. Volunteers will pack kits with food, hygiene items, and first aid materials to support families during emergencies.',
'Packing: Assemble emergency kits with essential items; Labeling: Mark boxes for distribution; Inventory: Track supplies for logistics',
'Packing materials, gloves, refreshments',
'Able to lift boxes, comfortable clothing, reusable water bottle',
'10:00 Arrival & Registration – Sign in and receive instructions; 10:15 Packing Begins – Assemble and label kits; 11:30 Refreshment Break – Enjoy provided snacks and drinks; 12:30 Wrap-up – Finalize inventory and prepare for dispatch',
'Faster disaster response, improved preparedness, and support for affected families.',
'2026-01-25', '10:00:00', '13:00:00', '03:00:00',
'Edinburgh', 'EH1 1YZ', 'Relief Centre',
30, '', 55.9533, -3.1883);


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