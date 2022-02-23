#these are the imports i would be using to create my system
from tkinter import * #used for gui
from School import *
from argon2 import PasswordHasher #used to hash the password
import psycopg2 #used for the database
import os

#verify if the code is valid for a teacher/student
def roleAuthenticate(code):
    #codes are used to verify the user; the return values are used to indicate the role the user has.
    if code == "STARK2021":
        return "Student"
    elif code == "TEARK2021":
        return "Teacher"
    #if the code entry is blank
    elif not code:
        return True
    else:
        return "Invalid code"

#this function is used to register a new user into the database
def registerUser():
    #check if the user is a valid student/teacher
    authenticate = roleAuthenticate(code.get())
    userFullName = userFirstName.get().strip() + " " + userLastName.get().strip()

    #check if the user's role and code match
    if(authenticate ==  "Student" and role.get() == "Student"):
        #if it smatches, it creates a student object
        studentClass = Student(userFullName, password.get())
        studentClass.createStudent(register)
    elif(authenticate == "Teacher" and role.get() == "Teacher"):
        #this would instantiate a teacher object
        teacherClass = Teacher(userFullName, password.get()) 
        teacherClass.createTeacher(register)

    elif(authenticate == "Invalid code"):
        messagebox.showerror("Grades+", "Error: Enter a valid code.")
    elif(role.get() == "pick a role"): 
        #creates an error box because the user has not picked a role
        messagebox.showerror("Grades+", "Error: Pick a role")
    elif(authenticate == True):
        #error box is created as the entry value for the code is empty 
        messagebox.showerror("Grades+", "Error: Enter a code.")
    else:
        messagebox.showerror("Grades+", "Error: Enter the correct code.")

def loginUser():
    #this creates a connection to the database
    connection = psycopg2.connect(host = "localhost", user = "postgres", password = "postgres", port = "5432", database = "school")
    cursor = connection.cursor()
    
    #checks the global variable role as to identify the user's interface.
    if(role.get() == "Student"):
        userFullName =  fullname.get().lower().strip()
        #this sql statement retrieves the attribute "student name" if it exists
        cursor.execute("SELECT student_name FROM students WHERE student_name = %s;", (userFullName,))

        #if the student exists in the database
        if cursor.fetchone() is not None: 
            #this sql statement retrieves the password which is associated with the student
            cursor.execute("SELECT student_password FROM students WHERE student_name = %s;", (userFullName,))
            storedPassword = cursor.fetchone() 
            authorised = False

            #as an error is called when the password is incorrect, i would catch it using exception handling.
            try:
                #this verifies if the password input is the same as the hashed password in thed database.
                PasswordHasher().verify(storedPassword[0], password.get())
                authorised = True
            except:
                #if theres an error, this would be because the password is incorrect hence i would make an errorbox to show this. 
                messagebox.showerror("Grades+", "Error: Incorrect password.")

            if authorised == True: 
                login.destroy()
                #this creates student object
                studentClass = Student(userFullName, password.get()) 
                #this would create the interface for the user
                studentClass.sendGUI() 

            connection.close()
        else: #if the student doesn't exist in the database, an errorbox would be called.
            messagebox.showerror("Grades+", "Error: This account does not exist or has not been registered yet.")
    elif(role.get() == "Teacher"):
        userFullName =  fullname.get().lower().strip()
        #this sql statement would check if teacher exists in the database
        cursor.execute("SELECT teacher_name FROM teachers WHERE teacher_name = %s;", (userFullName,))
        if cursor.fetchone() is not None: #if the teacher exists
            cursor.execute("SELECT teacher_password FROM teachers WHERE teacher_name = %s;", (userFullName,))
            storedPassword = cursor.fetchone() 
            
            authorised = False 
            try:
                #checks if the input of password is the same as the one in the database.
                PasswordHasher().verify(storedPassword[0], password.get())
                authorised = True
            except:
                messagebox.showerror("Grades+", "Error: Incorrect password.")
            
            #if the user's password was validated, it would instantiate the teacher object and create the interface.
            if authorised == True: 
                login.destroy()
                teacherClass = Teacher(userFullName, password.get()) 
                teacherClass.sendGUI() 

            connection.close()
        else: #if the teacher doesn't exist, an errorbox will be called
            messagebox.showerror("Grades+", "Error: This account does not exist or has not been registered yet.")

#this is the function for the registration interface
def register():
    global register
    #this create a new interface for the user to register
    register = Toplevel(auth)
    register.title("Registration")

    #create stringvar's for username and password so that the stored data can be collected
    #the strinvar data will be stored in the database for the student/teacher.
    global userFirstName
    global userLastName
    global password
    global code
    global role

    userFirstName = StringVar(register)
    userLastName = StringVar(register)
    password = StringVar(register)
    code = StringVar(register)
    role = StringVar(register)
    #this sets the default option for the roles dropdown.
    role.set("pick a role")

    Label(register, text = "First name:").grid(column = 0, row = 1)
    #this create an entry so that data can be inputted for the first name.
    Entry(register, textvariable = userFirstName).grid(column=1, row=1)

    Label(register, text = "Last name:").grid(column = 0, row = 2)
    #this create an entry so that data can be inputted for the last name.
    Entry(register, textvariable = userLastName).grid(column = 1, row = 2)

    Label(register, text = "Password:").grid(column = 0, row = 3)
    #this create a label and an entry so that data can be inputted for the password.
    #show = '*' will change the characters into an asterix to hide the password.
    Entry(register, textvariable = password, show = "*").grid(column = 1, row = 3)
    
    Label(register, text = "Code:").grid(column = 0, row = 4)
    #this create an entry so that data can be inputted for the code.
    Entry(register, textvariable = code).grid(column = 1, row = 4)
    
    #a dropdown for the user to choose if they are a student or a teacher.   
    OptionMenu(register, role, "Student", "Teacher").grid(sticky = E)
    #this create empty label for spacing purposes.
    Label(register,text = "").grid()
    #this create button to register the user. the function linked to the button will be called when the button is clicked.
    Button(register, text = "Register", command = registerUser).grid()

def login():
    global login
    global fullname
    global password
    global role

    #this create a new interface for the user to login
    login = Toplevel(auth)
    login.title("Login")

    #the following stringvar's are used to collect the data being inputted.
    fullname = StringVar(login)
    password = StringVar(login)
    role = StringVar(login)
    role.set("pick a role")

    Label(login, text = "Full name:").grid(column = 0, row = 1)
    #this create an entry so that data can be inputted for the full-name.
    Entry(login, textvariable = fullname).grid(column = 1, row = 1)

    Label(login, text = "Password:").grid(column = 0, row = 2)

    #this create an entry so that data can be inputted for the password.
    Entry(login, textvariable = password, show = "*").grid(column = 1, row = 2)
    
    #this would give the user a dropdown from which they can pick their role.
    OptionMenu(login, role, "Student", "Teacher").grid(sticky = E)
    
    #this create button to register the user and if validated the main interface would be created.
    Button(login, text = "Login", command = loginUser).grid()
  
def main():
    #this creates a file to track the validated students 
    def createStudentsFile():
        if os.path.exists("validstudents.txt"): #this would check if the file exists
            pass
        else:
            #opens the file/creates it if it does not exist and writes the data into it.
            studentFile = open("validstudents.txt", "w")      
            studentFile.write("#enter names of students that are valid\n")   #the default messages are for admin to customise the textfile. 
            studentFile.write("#format: firstname lastname (e.g. John Appleseed)")
            studentFile.close()

    #this creates a file to track the validated teachers
    def createTeachersFile():
        if os.path.exists("validteachers.txt"):
            pass 
        else:
            #opens the file/creates it if it does not exist and writes the data into it.
            teacherFile = open("validteachers.txt", "w")
            teacherFile.write("#enter names of teachers that are valid\n")   
            teacherFile.write("#format: firstname lastname (e.g. John Appleseed)")
            teacherFile.close()
    
    def createSubjectsFile():
        if os.path.exists("subjects.txt"):
            pass 
        else:
            #this creates the file to input subjects that the school teaches. (by default there are the subjects that the 6th form teaches)
            subjectsFile = open("subjects.txt", "w")
            subjectsFile.write("#enter the subjects below:")   
            subjectsFile.close()

    #this function checks for any new subjects in the subjects files and updates it
    def updateSubjectClass():
        #creating a connection to the database
        connection = psycopg2.connect(host = "localhost", user = "postgres", password = "postgres", port = "5432", database = "school")
        cursor = connection.cursor()
        
        #opens the subject textfile and gets every line in it.
        subjectsFile = open("subjects.txt", "r") 
        subjects = subjectsFile.readlines() 

        for subject in subjects:  #loops through all lines in subjects
            if subject.strip() == "#enter the subjects below:":
                pass #disregards the line
            else:
                #this sql statement retrieves the subject from subjects. I did this so that the system can check if the subject already exists or not.
                cursor.execute("SELECT subject FROM subjects WHERE subject = %s;", (subject.strip(),)) 
                
                if cursor.fetchone() is None:
                    #this would mean that thesubject does not exist and hence, adds the subject to the database
                    #the sql statement creates a new row by inserting the subject into the subjects table.
                    cursor.execute("INSERT INTO subjects (subject) VALUES (%s);", (subject.strip(),))
                    connection.commit()
        
        subjectsFile.close()
        connection.close()

    createStudentsFile()
    createTeachersFile()
    createSubjectsFile()

    databaseStatus = False 
    #I am using exception handling to check whether the database is running or not.
    try:
        #this would create a connection to the database
        psycopg2.connect(host = "localhost", user = "postgres", password = "postgres", port = "5432", database = "school")
        databaseStatus = True
    except:
        #this would mean that an error was called/the database is offline 
        print("Database isn't running right now.") 
    
    #if the database is running, then i would create the data-tables and the menu interface for the user
    if databaseStatus == True: 
        global auth
        connection = psycopg2.connect(host = "localhost", user = "postgres", password = "postgres", port = "5432", database = "school")
        cursor = connection.cursor()

        #this creates the students table if it doesnt exist
        cursor.execute("""CREATE TABLE IF NOT EXISTS students (
                    student_id SERIAL PRIMARY KEY,
                    student_name VARCHAR(150),
                    student_password VARCHAR(1000)
                    );""")

        #this creates the teachers table if it doesn't exist
        cursor.execute("""CREATE TABLE IF NOT EXISTS teachers (
                    teacher_id SERIAL PRIMARY KEY,
                    teacher_name VARCHAR(150),
                    teacher_password VARCHAR(1000)
                    );""")

        #this creates the table for the subjects if it doesn't exist
        cursor.execute("""CREATE TABLE IF NOT EXISTS subjects (
                    subject_id SERIAL PRIMARY KEY,
                    subject VARCHAR(50)
                    );""")

        #this creates the table for TeachersInClass if it doesn't exist
        cursor.execute("""CREATE TABLE IF NOT EXISTS teacherinclass (
                    subject_id INTEGER,
                    teacher_id INTEGER, 
                    FOREIGN KEY(subject_id) REFERENCES subjects(subject_id),
                    FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id),
                    teacher_name VARCHAR(150)
                    );""")

        #this creates the table for StudentInClass if it doesn't exist
        cursor.execute("""CREATE TABLE IF NOT EXISTS studentinclass (
                    subject_id INTEGER,
                    student_id INTEGER, 
                    FOREIGN KEY(subject_id) REFERENCES subjects(subject_id),
                    FOREIGN KEY(student_id) REFERENCES students(student_id),
                    student_name VARCHAR(150)            
                    );""")

        #this creates the table for the grades if it doesn't exist
        cursor.execute("""CREATE TABLE IF NOT EXISTS grades (
                        grade_id SERIAL PRIMARY KEY,
                        subject_id INTEGER,
                        student_id INTEGER,       
                        FOREIGN KEY(student_id) REFERENCES students(student_id),
                        FOREIGN KEY(subject_id) REFERENCES subjects(subject_id),
                        grade VARCHAR(2),
                        date DATE
                    );""")
        
        connection.commit()
        connection.close()
        updateSubjectClass() 
        
        #this would create the interface for the authentication system
        auth = Tk()  
        auth.title("Grades+")
        #this create a button to give the user the option to register. When clicked, the register interface would be created.
        Button(text = "Register", height = "3", width = "20", command = register).pack()
        Label(text="").pack() 
        #this create a button to give the user the option to login. When clicked, the login interface would be created.
        Button(text = "Login", height = "3", width = "20", command = login).pack() 
        
        #this would run the tkinter window
        auth.mainloop()

if __name__ == "__main__":
    main()