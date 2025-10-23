-- ===============================================================
--  DELIVERY TRACKER - RDBMS SCHEMA (vFinal-7)
--  Optimized for performance, referential integrity, and analytics
--  PostgreSQL / MySQL Compatible
-- ===============================================================

-- ===============================================================
--  1. BUSINESS & PROJECT HIERARCHY
-- ===============================================================

CREATE TABLE User (
    `UserId` VARCHAR(50) NOT NULL,
    `userName` VARCHAR(200) NOT NULL,
    `password` VARCHAR(200) NOT NULL,
    `RoleId` VARCHAR(50) DEFAULT NULL,
    `BUId` VARCHAR(50) NOT NULL,
    `EmployeeId` VARCHAR(50) DEFAULT NULL,
    `otp` VARCHAR(10) DEFAULT NULL,
    `otp_expiry` DATETIME DEFAULT NULL,
    `emailID` VARCHAR(200) DEFAULT NULL,
    `FirstName` VARCHAR(100) DEFAULT NULL,
    `lastName` VARCHAR(100) DEFAULT NULL,
    `fullName` VARCHAR(200) DEFAULT NULL,
    PRIMARY KEY (`UserId`),
    UNIQUE KEY `ix_user_userName` (`userName`),
    INDEX `ix_user_UserId` (`UserId`),
    FOREIGN KEY (`RoleId`) REFERENCES `role_master`(`RoleId`),
    FOREIGN KEY (`BUId`) REFERENCES `business_unit`(`BUId`),
    FOREIGN KEY (`EmployeeId`) REFERENCES `employee`(`EmployeeId`)
);


CREATE TABLE BusinessUnit (
    BUId VARCHAR(50) PRIMARY KEY,
    BUName VARCHAR(150) NOT NULL,
    BUHeadId VARCHAR(50),
    Description TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_businessunit_head ON BusinessUnit(BUHeadId);

CREATE TABLE Project (
    ProjectId VARCHAR(50) PRIMARY KEY,
    BUId VARCHAR(50) NOT NULL REFERENCES BusinessUnit(BUId) ON DELETE CASCADE,
    ProjectName VARCHAR(150) NOT NULL,
    Description TEXT,
    PlannedStartDate DATE,
    PlannedEndDate DATE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_project_buid ON Project(BUId);

CREATE TABLE Milestone (
    MilestoneId VARCHAR(50) PRIMARY KEY,
    ProjectId VARCHAR(50) NOT NULL REFERENCES Project(ProjectId) ON DELETE CASCADE,
    Title VARCHAR(150) NOT NULL,
    Description TEXT,
    PlannedStartDate DATE,
    PlannedEndDate DATE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_milestone_projectid ON Milestone(ProjectId);

CREATE TABLE Task (
    TaskId VARCHAR(50) PRIMARY KEY,
    MilestoneId VARCHAR(50) NOT NULL REFERENCES Milestone(MilestoneId) ON DELETE CASCADE,
    Title VARCHAR(150) NOT NULL,
    Description TEXT,
    PlannedStartDate DATE,
    PlannedEndDate DATE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_task_milestoneid ON Task(MilestoneId);

CREATE TABLE Deliverable (
    DeliverableId VARCHAR(50) PRIMARY KEY,
    TaskId VARCHAR(50) NOT NULL REFERENCES Task(TaskId) ON DELETE CASCADE,
    Title VARCHAR(150) NOT NULL,
    Description TEXT,
    AssignedToId VARCHAR(50),
    ReviewerId VARCHAR(50),
    Priority VARCHAR(50),
    PlannedStartDate DATE,
    PlannedEndDate DATE,
    EstimatedHours DECIMAL(6,2) CHECK (EstimatedHours >= 0),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_deliverable_taskid ON Deliverable(TaskId);
CREATE INDEX idx_deliverable_assignedto ON Deliverable(AssignedToId);
CREATE INDEX idx_deliverable_reviewer ON Deliverable(ReviewerId);

-- ===============================================================
--  2. PROGRESS & ISSUE TRACKING
-- ===============================================================

CREATE TABLE DailyStatus (
    DailyStatusId VARCHAR(50) PRIMARY KEY,
    DeliverableId VARCHAR(50) NOT NULL REFERENCES Deliverable(DeliverableId) ON DELETE CASCADE,
    EmployeeId VARCHAR(50),
    WorkDate DATE NOT NULL,
    HoursSpent DECIMAL(5,2) CHECK (HoursSpent >= 0),
    Progress DECIMAL(5,2) CHECK (Progress BETWEEN 0 AND 100),
    Comment TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dailystatus_deliverable ON DailyStatus(DeliverableId);
CREATE INDEX idx_dailystatus_employee ON DailyStatus(EmployeeId);

CREATE TABLE Issue (
    IssueId VARCHAR(50) PRIMARY KEY,
    DeliverableId VARCHAR(50) NOT NULL REFERENCES Deliverable(DeliverableId) ON DELETE CASCADE,
    Title VARCHAR(150) NOT NULL,
    Description TEXT,
    ActionOwnerId VARCHAR(50),
    Priority VARCHAR(50),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_issue_deliverable ON Issue(DeliverableId);
CREATE INDEX idx_issue_actionowner ON Issue(ActionOwnerId);

CREATE TABLE IssueActivity (
    IssueActivityId VARCHAR(50) PRIMARY KEY,
    IssueId VARCHAR(50) NOT NULL REFERENCES Issue(IssueId) ON DELETE CASCADE,
    EmployeeId VARCHAR(50),
    ActivityDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Status VARCHAR(50) CHECK (Status IN ('Open','InProgress','Resolved','Closed')),
    Comment TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_issueactivity_issueid ON IssueActivity(IssueId);
CREATE INDEX idx_issueactivity_employee ON IssueActivity(EmployeeId);

CREATE TABLE Review (
    ReviewId VARCHAR(50) PRIMARY KEY,
    DeliverableId VARCHAR(50) NOT NULL REFERENCES Deliverable(DeliverableId) ON DELETE CASCADE,
    ReviewerId VARCHAR(50),
    Feedback TEXT,
    FeedbackDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Action VARCHAR(50) CHECK (Action IN ('Approved','Rejected','NeedsRework')),
    ActionDate DATE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_review_deliverable ON Review(DeliverableId);
CREATE INDEX idx_review_reviewer ON Review(ReviewerId);

-- ===============================================================
--  3. RATING SYSTEM (IMMEDIATE AFTER REVIEW)
-- ===============================================================

CREATE TABLE RatingAttributeMaster (
    AttributeId VARCHAR(50) PRIMARY KEY,
    AttributeName VARCHAR(100) NOT NULL,
    Description TEXT,
    Weight DECIMAL(5,2) DEFAULT 1.0 CHECK (Weight >= 0),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE DeliveryRating (
    RatingId VARCHAR(50) PRIMARY KEY,
    DeliverableId VARCHAR(50) NOT NULL REFERENCES Deliverable(DeliverableId) ON DELETE CASCADE,
    AttributeId VARCHAR(50) NOT NULL REFERENCES RatingAttributeMaster(AttributeId),
    RatedForId VARCHAR(50) NOT NULL,
    RatedById VARCHAR(50) NOT NULL,
    Score DECIMAL(4,2) CHECK (Score BETWEEN 0 AND 5),
    Comment TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ratedfor FOREIGN KEY (RatedForId) REFERENCES Employee(EmployeeId),
    CONSTRAINT fk_ratedby FOREIGN KEY (RatedById) REFERENCES Employee(EmployeeId)
);

CREATE INDEX idx_rating_deliverable ON DeliveryRating(DeliverableId);
CREATE INDEX idx_rating_ratedfor ON DeliveryRating(RatedForId);
CREATE INDEX idx_rating_attribute ON DeliveryRating(AttributeId);

-- ===============================================================
--  4. EMPLOYEE & ROLE MANAGEMENT
-- ===============================================================

CREATE TABLE Employee (
    EmployeeId VARCHAR(50) PRIMARY KEY,
    FullName VARCHAR(150) NOT NULL,
    Email VARCHAR(200) UNIQUE NOT NULL,
    BUId VARCHAR(50) REFERENCES BusinessUnit(BUId),
    HolidayCalendarId VARCHAR(50),
    Status VARCHAR(50) DEFAULT 'Active',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_employee_buid ON Employee(BUId);
CREATE INDEX idx_employee_status ON Employee(Status);

CREATE TABLE RoleMaster (
    RoleId VARCHAR(50) PRIMARY KEY,
    RoleName VARCHAR(100) NOT NULL,
    Description TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE EmployeeRole (
    EmployeeRoleId VARCHAR(50) PRIMARY KEY,
    EmployeeId VARCHAR(50) NOT NULL REFERENCES Employee(EmployeeId) ON DELETE CASCADE,
    RoleId VARCHAR(50) NOT NULL REFERENCES RoleMaster(RoleId),
    Active BOOLEAN DEFAULT TRUE,
    AssignedDate DATE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_employeerole_employee ON EmployeeRole(EmployeeId);
CREATE INDEX idx_employeerole_role ON EmployeeRole(RoleId);

-- ===============================================================
--  5. SKILLS & CERTIFICATIONS
-- ===============================================================

CREATE TABLE SkillMaster (
    SkillId VARCHAR(50) PRIMARY KEY,
    SkillName VARCHAR(100) NOT NULL,
    SkillLevel VARCHAR(50),
    Description TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE CertificationMaster (
    CertificationId VARCHAR(50) PRIMARY KEY,
    SkillId VARCHAR(50) REFERENCES SkillMaster(SkillId),
    CertificationName VARCHAR(150) NOT NULL,
    IssuingAuthority VARCHAR(100),
    ValidDurationDays INT CHECK (ValidDurationDays >= 0),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE EmployeeSkill (
    EmployeeSkillId VARCHAR(50) PRIMARY KEY,
    EmployeeId VARCHAR(50) NOT NULL REFERENCES Employee(EmployeeId),
    SkillId VARCHAR(50) NOT NULL REFERENCES SkillMaster(SkillId),
    IsPrimary BOOLEAN DEFAULT FALSE,
    ExperienceYears DECIMAL(4,1),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_employeeskill_employee ON EmployeeSkill(EmployeeId);
CREATE INDEX idx_employeeskill_skill ON EmployeeSkill(SkillId);

CREATE TABLE EmployeeCertification (
    EmployeeCertificationId VARCHAR(50) PRIMARY KEY,
    EmployeeId VARCHAR(50) NOT NULL REFERENCES Employee(EmployeeId),
    CertificationId VARCHAR(50) NOT NULL REFERENCES CertificationMaster(CertificationId),
    IssuedDate DATE,
    CertificateNumber VARCHAR(100),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_emp_cert_employee ON EmployeeCertification(EmployeeId);
CREATE INDEX idx_emp_cert_certid ON EmployeeCertification(CertificationId);

-- ===============================================================
--  6. RESOURCE CAPACITY & LEAVES
-- ===============================================================

CREATE TABLE EmployeeCapacity (
    EmployeeCapacityId VARCHAR(50) PRIMARY KEY,
    EmployeeId VARCHAR(50) NOT NULL REFERENCES Employee(EmployeeId),
    BUId VARCHAR(50) NOT NULL REFERENCES BusinessUnit(BUId),
    CapacityPerDayHours DECIMAL(4,1) CHECK (CapacityPerDayHours > 0),
    Location VARCHAR(100),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_emp_capacity_employee ON EmployeeCapacity(EmployeeId);

CREATE TABLE EmployeeLeave (
    LeaveId VARCHAR(50) PRIMARY KEY,
    EmployeeId VARCHAR(50) NOT NULL REFERENCES Employee(EmployeeId),
    LeaveDate DATE NOT NULL,
    LeaveType VARCHAR(50),
    Reason TEXT,
    ApprovedById VARCHAR(50),
    Status VARCHAR(50) CHECK (Status IN ('Pending','Approved','Rejected')),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_leave_employee ON EmployeeLeave(EmployeeId);
CREATE INDEX idx_leave_date ON EmployeeLeave(LeaveDate);

-- ===============================================================
--  7. HOLIDAY CALENDARS
-- ===============================================================

CREATE TABLE HolidayCalendar (
    HolidayCalendarId VARCHAR(50) PRIMARY KEY,
    CalendarName VARCHAR(100),
    Description TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Holiday (
    HolidayId VARCHAR(50) PRIMARY KEY,
    HolidayCalendarId VARCHAR(50) NOT NULL REFERENCES HolidayCalendar(HolidayCalendarId),
    Date DATE,
    HolidayName VARCHAR(150),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_holiday_calendar ON Holiday(HolidayCalendarId);
CREATE INDEX idx_holiday_date ON Holiday(Date);

-- ===============================================================
--  8. AUDIT LOG
-- ===============================================================

CREATE TABLE AuditLog (
    AuditId VARCHAR(50) PRIMARY KEY,
    EntityType VARCHAR(100),
    EntityId VARCHAR(50),
    Action VARCHAR(50),
    FieldChanged VARCHAR(100),
    OldValue TEXT,
    NewValue TEXT,
    ChangedBy VARCHAR(50) REFERENCES Employee(EmployeeId),
    ChangedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_entity ON AuditLog(EntityType, EntityId);
CREATE INDEX idx_audit_changedby ON AuditLog(ChangedBy);



