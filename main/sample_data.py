from main.database import SessionLocal, engine, Base
from main import models
import datetime

def create_sample():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # BusinessUnit
    if db.query(models.BusinessUnit).count() == 0:
        bu = models.BusinessUnit(BUId="BU-001", BUName="Analytics BU", Description="Analytics")
        db.add(bu)
    # Project
    if db.query(models.Project).count() == 0:
        p = models.Project(ProjectId="PRJ-001", BUId="BU-001", ProjectName="Project A")
        db.add(p)
    # Deliverable
    if db.query(models.Deliverable).count() == 0:
        d = models.Deliverable(DeliverableId="DEL-001", ProjectId="PRJ-001", Title="Deliverable 1")
        db.add(d)
    # Employees
    if db.query(models.Employee).count() == 0:
        e1 = models.Employee(EmployeeId="EMP-001", FullName="Alice Dev", Email="alice@example.com", BUId="BU-001")
        e2 = models.Employee(EmployeeId="EMP-002", FullName="Bob Rev", Email="bob@example.com", BUId="BU-001")
        db.add_all([e1, e2])
    # Skills
    if db.query(models.SkillMaster).count() == 0:
        s1 = models.SkillMaster(SkillId="SK-001", SkillName="Python", SkillLevel="Expert")
        s2 = models.SkillMaster(SkillId="SK-002", SkillName="SQL", SkillLevel="Intermediate")
        db.add_all([s1, s2])
    # Certifications
    if db.query(models.CertificationMaster).count() == 0:
        c = models.CertificationMaster(CertificationId="CERT-001", CertificationName="GCP Cert")
        db.add(c)
    db.commit()
    db.close()
    print("Sample data created. Run the app and check /docs")

if __name__ == '__main__':
    create_sample()
