import time
import requests
import os
class Employee:
    def __init__(self, code, name, role, dept):
        self.code = code
        self.name = name
        self.role = role
        self.dept = dept

class Performance:
    def __init__(self, employee_person, grade, remarks, extra_bonus):
        self.employee_person = employee_person
        self.grade = grade
        self.remarks = remarks
        self.extra_bonus = extra_bonus

employees = {
    "E201": Employee("E201", "Alice Johnson", "Product Manager", "Design"),
    "E202": Employee("E202", "Bob Brown", "Project Manager", "Development"),
}

performances = {
    "E201": Performance(employees["E201"], 4.7, "Outstanding leadership", 3000),
    "E202": Performance(employees["E202"], 4.0, "Very good project execution", 2500),
}