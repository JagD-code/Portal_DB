from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
import json
import csv
import logging
from pathlib import Path

class Role(Enum):
    student = 1
    dept_staff = 2
    HOD = 3
    Principal = 4

    def __str__(self):
        return self.name.replace('_',' ').title()

class Operations(Enum):
    view = "Viewed"
    modify = "Modified"
    export = "Exported"
    delete = "Deleted"
    grade_entry = "Entered Grades"
    attendance_entry = "Attendance marked"

class Auditlog:
    timestamp : datetime
    user_id : int
    role : Role
    operation : Operations
    record_id : Optional[int]
    department : str
    details : str
    success : bool

class StudentRecord:
    id: int
    student_id: int
    name: str
    department: str
    year: int
    semester: int
    timestamp: datetime
    modified_timestamp: Optional[datetime]
    modified_by: str
    data: dict  
    version_history: List[dict]

class User:
    id : int
    username : str
    role : Role
    name : str
    department : str
    contact : str

class EducationalDataSystem:
    def __init__(self):
        self.users : Dict[int, User] = {}
        self.student_records : Dict[int, StudentRecord]
        self.departments : Dict[str, Set[str]] = {}
        self.audit_logs : List[Auditlog] = []

        logging.basicConfig(
            filename = 'data_access.log',
            level = logging.INFO,
            format = '%(asctime)s - %(message)s'
        )
    
    def _log_operation(self, user_id: int, operation: Operations,
                       record_id: Optional[int], details: str, success: bool)-> None:
        user = self.users.get(user_id)
        if not user:
            return
        
        audit_entry = Auditlog(
            timestamp = datetime.now()
            user_id = user_id,
            role = user.role,
            operation = Operation,
            record_id = record_id,
            department = user.department,
            details = details,
            success = success
        )
        self.audit_logs.append(audit_entry)

        log_message = (f"{user.role} {user.name} ({user.department}) - {operation.value} - "
                       f"Record {record_id} - {details} - {'Success' if success else 'Failed'}")
        logging.info(log_message)
    
    def can_access_record(self, user: User, record: StudentRecord) -> bool:
        match user.role:
            case Role.student:
                return user.id == record.student_id

            case Role.dept_staff:
                return user.department == record.department
        
            case Role.HOD:
                return user.department == record.department
        
            case Role.Principal:
                return True
            
        return False

    def can_modify_record(self , user:User , record:StudentRecord) -> bool:
        match user.role:
            case Role.student:
                return False
            
            case Role.dept_staff:
                return user.department == record.department
            
            case Role.HOD:
                return user.department == record.department
            
            case Role.Principal:
                return True
        
        return False

    def add_student_record(self , student_data : dict) -> int:
        record_id = len(self.student_records) + 1
        self.student_records[record_id] = StudentRecord(
            id = record_id,
            student_id = student_data['student_id'],
            name = student_data['name'],
            department = student_data['department'],
            year = student_data['year'],
            semester = student_data['semester'],
            timestamp = datetime.now(),
            modified_timestamp = None,
            modified_by = None,
            data = {
                'grades': {},
                'attendance': {},
                
            },
            version_history = []
        )
        return record_id
    
    def modify_student_record(self,user_id : int , record_id : int,
                              modifications : dict , modification_type : str) -> bool:
        if user_id not in self.users or record_id not in self.student_records:
            self._log_operation(user_id , Operations.modify , record_id,
                                "Invalid user or record" , False)
            
            return False
        
        user = self.users[user_id]
        record = self.student_record[record_id]

        if not self.can_modify_record(user , record):
            self.__log__operation(user_id , Operations.modify , record_id ,
                                  "Permission denies" ,  False)
            
            return False
        
        record.version_history.append({
            'data' : record.data.copy(),
            'modified_by' : record.modified_by,
            'timestamp' : record.modified_timestamp or record.timestamp
        })

        match modification_type:
            case "grades":
                if user.role in [Role.dept_staff , Role.HOD , Role.Principal]:
                    record.data['grades'].update(modifications)
                    operation = Operations.grade_entry
                else:
                    return False
            
            case "attendance":
                if user.role in [Role.dept_staff , Role.HOD , Role.Principal]:
                    record.data['attendance'].update(modifications)
                    operation = Operations.attendance_entry
                else:
                    return False
            
            case _:
                return False
        
        record.modified_timestamp = datetime.now()
        record.modified_by = user_id

        self._log_operation(user_id , operation , record_id ,
                            f"Modified {modification_type} : {modifications}" , True)
        return True
    
    def export_data(self , user_id : int , format : str = 'json' ,
                    export_type : str = 'full' , filepath: str = None) -> str:
        if user_id not in self.users:
            self._log_operation(user_id , Operations.export , None,
                                "Invalid user" ,  False)
            return None
        user = self.users[user_id]
        accessible_records = [
            record for record in self.student_records.values()
            if self.can_access_record(user , record)
        ]
        if not accessible_records:
            self._log_operation(user_id , Operations.export , None,
                                "No record to export" , False)
            return None
        
        export_data = []
        for record in accessible_records:
            if export_type == 'grades':
                export_data.append({
                    'student_id' : record.student_id,
                    'name' : record.name,
                    'department' : record.department,
                    'year' : record.year,
                    'semester' : record.semester,
                    'grades' : record.data['grades']
                })
            elif export_type == 'attendance':
                export_data.append({
                    'student_id' : record.student_id,
                    'name' : record_name , 
                    'department' :  record.department ,
                    'attendance' : record.data['attendance']
                })
            else:
                export_data.append({
                    'student_id' : record.student_id,
                    'name' : record.name,
                    'department' : record.department ,
                    'year':record.year,
                    'semester' : record.semester,
                    'data' : record.data
                })
        if not filepath:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file = f"{user.department}_{export_type}_export_{timestamp}.{format}"

        try:
            if format == 'json':
                with open(filepath , 'w')as f:
                    json.dump(export_data , f , indent = 2)
            elif format == 'csv':
                with open(filepath , 'w' , newline = '') as f:
                    if export_data:
                        writer = csv.DictWriter(f , fieldnames = export_data[0].keys())
                        writer.writeheader()
                        writer.writerows(export_data)

            self._log_operation(user_id , Operations.export , None,
                                f"Exported {len(export_data)} record to {filepath}", True)
            return filepath
        except Exception as e:
            self._log_operation(user_id , Operations.export , None,
                                f"Export failed : {str(e)}" , False)
            return None

def main():
    eds = EducationalDataSystem()
    student_data = {}
    record_id = eds.add_student_record(student_data)
    eds.modify_student_record()
    export_path = eds.export_data()
    for entry in eds.audit_logs:
        print(f"{entry.timestamp} : {entry.role} {entry.operation.value} - {entry.details}")


                                
                
    

        