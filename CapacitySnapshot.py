class CapacitySnapshot:
    def __init__(self, service_name, waiting_time_mins=0, pts_waiting=0, pts_in_dept=0):
        self.name = str(service_name)
        self.waiting_time_mins = int(waiting_time_mins)
        self.patients_waiting = int(pts_waiting)
        self.patients_in_dept = int(pts_in_dept)

    def __repr__(self):
        return f"<CapacitySnapshot Name={self.name} WaitingTime={self.waiting_time_mins} mins " \
               f"PatientsWaiting={self.patients_waiting} PatientsInDepartment={self.patients_in_dept}>"
