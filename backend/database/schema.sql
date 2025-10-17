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