# Echelon
Echelon is a CRM with E2EE built within. It is designed to provide the highest level of privacy and security to its users.

# Front-end
- Javascript
- HTML
- CSS

# Back-end
- Python Django
- PostgreSQL


# Virtual Environment
The project will be started in a virtual environment. This is to isolate all of the project dependencies.
	To start the environment use
	source EchelonEnv/bin/activate on MacOS
	.\EchelonEnv\Scripts\activate

make sure you install django after setting up the virtual environment using
	python install Django

# Admin Credentials
Username: Admin
Password: Password!23

# Start Local Server
python manage.py runserver

paster URL into your browser

# Start App
python manage.py startapp appname

# Workflow
Admin creates Company account and links all associated accounts through admin

# Permissions
### Admin 
	- Create/Remove/Update Staffs and Clients.
	- Create/Remove/Update Services
	- Create/Remove/Update Tasks (Assigns to Manager or Staff or Client or Them Selfs)
	- Create/Remove/Update Meeting
	- Create/Remove/Update Invoices.
		- Can communicate with anyone in company account
### Manager
	- Create/Remove/Update Services
	- Create/Remove/Update Tasks (Assigns to Staff or Client or Them Selfs)
	- Create/Remove/Update Meeting
	- Create/Remove/Update Invoices
	- Send Messages.
		- Can directly communicate with employees or clients
### Staff
	- Create/Update Tasks (Assigns to client or Them Selfs)
	- Create/Update Meeting
	- Create/Update Invoices
	- Send Messages.
		- Can directly communicate with people requesting service, or manager

### Client
	- Request Service
	- Create/Update Meeting
	- Send Message
		- Can communicate with person with assigned task to requested service
	
# TODO 
- [] Landing App
	[] Views/FrontEnd
		[] Landing page
			[] where users log in
			[] Only the admin can create accounts. (No manual registration my ANY user)
		[] Home/Dashboard
			Companies (Staffs/Managers) & Clients will have different views
			[] Active Services
			[] Show requested service
			[] Meetings
			[] Show active messages
	What else do y'all think the dash board need to see?

- [] Accounts App
	[] Views/front end
		[] Manager
			[] Create/Remove/Update Staffs and clients.
			[] View all users under Company Account
	[x] Models
		Company manager, Staff and, client is needed.
		[x] User
		[x] CompanyAccount
		[x] Membership

- [] CRM App
	[] Views/FrontEnd
		Tasks created under services
		[] Display Tasks assigned to user
		[] Display users contacts
	[x] Models
		[x] Tasks
		[x] Contact

- [] Services App
	[] Views/FrontEnd
		[] Manager
			[] Creates/Delete/Modify Services
			[] Create/Delete/Modify Task to Staff or client
		[] Staff
			[] Create/Delete/Modify Tasks to client
			[] Is assigned Tasks
			[] Modifies Services Status
		[] Client
			[] Requests Services
			[] Is Assigned Tasks
			[] Views progress
	[x] Models
		[x] Services
		[x] Requested Services 

- [] Scheduling Scheduling
	[] Views/FrontEnd
		[] Schedule meeting
		[] Edit meeting
		[] Cancel Meeting
	[] Models
		[] Meeting
			[] meetings are billable
		[] Meeting participant

- [] Billing App
	Invoices will be created by scanning complete requested services, and complete meetings to sum a bill.
	[] Views/FrontEnd
		[] Create invoice
		[] Delete invoice
		[] Take payment (Optional)
		[] Display current meetings 
	[] Models
		[] Invoice
		[] Paid Invoice

- [] Messaging App
	[] Views/FrontEnd
		[] Create message
		[] 
	[] Models
		Message

- [] Crypto App
	[] Views/FrontEnd
	[] Models

- [] Maybe Audit checks
	[] Views/FrontEnd
	[] Models