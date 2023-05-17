# 📅 Django Enterprise Schedule Management (xflow) 

xflow is a powerful tool designed to enable managers and team leaders to effectively manage the schedules of their team members. This tool gives a comprehensive view of the calendar and allows team members to request remote work days. Managers have the authority to accept or reject these requests. The tool also provides various indicative tables such as live request status, overall team calendar, and more.

## 🚀 Features

- **Employee schedule management:** Managers can view and manage the schedules of all team members in a comprehensive calendar view.
- **Remote work requests:** Employees can request to work remotely. These requests can be accepted or rejected by managers.
- **Dynamic calendar view:** The application provides a global calendar view of all employees.
- **Live request status:** Managers can view the status of remote work requests in real time.
- **Employee account management:** Employees can manage their accounts, including changing their password.

## 🛠️ How it works

The application is built with Django, a high-level Python web framework that encourages rapid development and clean, pragmatic design.

The application uses Django's built-in authentication system. The `Employee` model extends `AbstractUser` to add an `is_manager` field, which determines whether the user is a manager or not. 

Each day that an employee wants to work remotely is represented by a `RemoteDay` object. Employees can have multiple `RemoteDay` objects associated with them. 

Remote work requests are represented by the `RemoteRequest` model. Each request has a status, which can be 'pending', 'approved', or 'rejected'. 

When a manager approves a request, the corresponding `RemoteDay` is associated with the employee who made the request. 

The application provides several views:

- `setup`: This is where employees can mark the days they wish to work remotely. If a day is in the past or a public holiday, it cannot be marked as a remote work day.
- `calendar`: This is a global view of all employees' schedules. Managers can filter this view to only show employees who are working remotely.
- `account`: This is where employees can change their password.
- `requests`: This is where managers can view all pending remote work requests.
- `requests_status`: This is where employees can view the status of their remote work requests.

## 💾 Installation

To install the application, you will need to have Python and Django installed on your machine. You can then clone this repository, navigate to the project directory, and run the following command to start the Django development server:

```bashd
python manage.py runserver
```

You can then access the application in your web browser at http://localhost:8000.

🚀 (In progress) I am currently working on an HTTPS version of the project that could be easily deployed.
