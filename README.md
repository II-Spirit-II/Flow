# 📅 Django Enterprise Schedule Management (xflow) 

xflow is a powerful tool designed to enable managers and team leaders to effectively manage the schedules of their team members. This tool gives a comprehensive view of the calendar and allows team members to request remote work days. Managers have the authority to accept or reject these requests. The tool also provides various indicative tables such as live request status, overall team calendar, and more.

## 🚀 Features

- **Employee schedule management:** Managers can view and manage the schedules of all team members in a comprehensive calendar view.
- **Remote work requests:** Employees can request to work remotely. These requests can be accepted or rejected by managers and managers is notify by an email.
- **Dynamic calendar view:** The application provides a global calendar view of all employees and their status.
- **Live request status:** Managers can view the status of remote work requests in real time.
- **Employee account management:** Employees can manage their accounts, including changing their password.
- **Email notification:** Users receive email notifications for important updates and events.
- **Live view:** Users can see in real time who is teleworking and who is on-site.

## 🛠️ How it works

The application is built with Django, a high-level Python web framework that encourages rapid development and clean, pragmatic design.

The application uses Django's built-in authentication system. The `Employee` model extends `AbstractUser` to add an `is_manager` field, which determines whether the user is a manager or not. 

Each day that an employee wants to work remotely is represented by a `RemoteDay` object. Employees can have multiple `RemoteDay` objects associated with them. 

Remote work requests are represented by the `RemoteRequest` model. Each request has a status, which can be 'pending', 'approved', or 'rejected'. 

When a manager approves a request, the corresponding `RemoteDay` is associated with the employee who made the request. 

The application provides several pages:

- `/setup`: This is where employees can mark the days they wish to work remotely. If a day is in the past or a public holiday, it cannot be marked as a remote work day.
- `/calendar`: This is a global view of all employees' schedules. Managers can filter this view to only show employees who are working remotely.
- `/account`: This is where employees can change their password.
- `/requests`: This is where managers can view all pending remote work requests.
- `/requests_status`: This is where employees can view the status of their requests.



## 💾 Installation

To install the application, you will need to have Docker installed on your machine. Docker allows you to package the application and its dependencies into a container, making it easy to deploy and run consistently across different environments.

If you don't have Docker installed, you can follow the installation instructions for your operating system:

- [Install Docker for Windows](https://docs.docker.com/docker-for-windows/install/)
- [Install Docker for macOS](https://docs.docker.com/docker-for-mac/install/)
- [Install Docker for Linux](https://docs.docker.com/engine/install/)

Once you have Docker set up, you can proceed with the following steps:

1 - Clone this repository to your local machine.

```
git clone https://github.com/II-Spirit-II/Flow.git
```

2 - Navigate to `Flow/src/` with:

```
cd Flow/src
```

Run the following command to execute configuration script:
```
./config.sh
```

![image](https://github.com/II-Spirit-II/Flow/assets/61940136/0197495c-d6a7-4ec0-872d-d81cbfeca911)

The script is used to set up everything needed to run the stack in particular:
- SSL folder in order to set up the HTTPS protocol (you can skip this step if you have your domain name/official SSL certificate)
- Database informations like user and password

Next, run the following command to build and start the application using Docker Compose:

```
docker-compose up --build -d
```

This command will build the Docker image for the application and start the container in detached mode (in the background). You don't need to do anything else ✨ !

**Note:** If for any reason the container(s) should shut down, you can restart it without rebuilding the image, which will take much less time. To do this, use the following command:

```
docker compose up -d
```

![image](https://github.com/II-Spirit-II/Flow/assets/61940136/9688c301-3d83-4f65-b7ed-753dd2b10b8c)


## 🌐 Access

The application will be launched inside a Docker container. You can access it in your web browser at https://your-ip

![image](https://github.com/II-Spirit-II/Flow/assets/61940136/41dba6d8-8d3f-4295-91fe-fb4d74cb4fac)
