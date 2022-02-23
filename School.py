#import modules which would be used for the system
from tkinter import * #used for gui
from tkinter import ttk
from tkinter import messagebox
from argon2 import PasswordHasher #used to hash the password
import time    
import psycopg2 #used for the database

#create the base class for the system
class School:
    def __init__(self, userFullName, password):
        #this would store the user's properties so that it can be used throughout the program.
        self.userFullName = userFullName.lower().strip()
        self.password = password

    #this function would return the attribute "userFullName"
    def getName(self):
        return self.userFullName
    
    #this function would return the attribute "password"
    def getPassword(self):
        return self.password

    #this procedure would create a messagebox when required in my system
    def messageBox(self, textLabel, messageType):
        if messageType == "error":
            #this is an error box which would be created when the input is error.
            messagebox.showerror("Grades+", "Error: " + textLabel)
        elif messageType == "info":
            #this creates an info box
            messagebox.showinfo("Grades+", textLabel)
    
    #this function checks if the password is valid
    def isPasswordValid(self, password): 
        if not password: #checks if the string is empty (stirng-falsy)
            #this would show errorbox as the entry is invalid
            self.messageBox("Enter a password.", "error")
        
        #this condition checks if the password's length is less than 5
        elif len(password) < 5:
            #as the password is smaller than 5 characters, it would throw an errorbox.
            self.messageBox("Password must be atleast 5 characters long.", "error")
            return False
        #checks if the password's length is more than 10
        elif len(password) > 10: 
            self.messageBox("Password cannot be longer than 10 characters. ", "error")
            return False 
        else:
            return True #if password is valid, the function would return true

#this class is a subclass which inherits the methods of it's parent class which is School.
class Teacher(School):
    #this function would follow an algorithm in order to add the teacher to the database
    def createTeacher(self, window):
        #this creates a connection to the database
        connection = psycopg2.connect(host = "localhost", user = "postgres", password = "postgres", port = "5432", database = "school")
        cursor = connection.cursor()

        #Here I am opening and reading the lines of the valid teachers textfiles to check if the corresponding teacher is valid.
        teachersFile = open("validteachers.txt", "r") 
        validTeachers = teachersFile.readlines() 
        validated = False
        #looping through the file to see if the teacher is in it
        for teacher in validTeachers: 
            if self.getName() == teacher.strip().lower():
                validated = True
                #this sql statement is used to check if the teacher exists in the database
                cursor.execute("SELECT teacher_name FROM teachers WHERE teacher_name = %s;", (self.getName(),)) 
                if cursor.fetchone() is not None:
                    #teacher exists in the database since value is not null
                    self.messageBox("Already registered.", "error")
                else: 
                    #the teacher is valid
                    #the system would checks if password is valid
                    if self.isPasswordValid(self.getPassword()) == True: 
                        #as the teacher does not exist; the sql statement would add the teacher to the database
                        hashedPassword = PasswordHasher().hash(self.getPassword())
                        cursor.execute("INSERT INTO teachers (teacher_id, teacher_name, teacher_password) VALUES (DEFAULT, %s, %s);", (self.getName(), hashedPassword))
                        self.messageBox("Success! You have been registered.", "info")
                        window.after(3000, window.destroy)

        #if value of validated did not change then that means the student is not valid
        if validated == False: 
            self.messageBox("You are not a validated teacher.", "error")
        
        connection.close()
    
    #this function is the core as it provides the main interface for the teacher.  
    def sendGUI(self):
        connection = psycopg2.connect(host = "localhost", user = "postgres", password = "postgres", port = "5432", database = "school")
        cursor = connection.cursor() 

        #this creates the window for the interface
        gui = Tk()
        gui.title("Grades+")
        gui.geometry("1500x800")
        menubar = Menu(gui)

        #this procedure would stop the program from running
        def logOut():
            exit(0)

        #this function is for the class interface
        def subjectGUI(subject):
            #this would create the class interface
            subjectGUI = Toplevel(gui)
            subjectGUI.title(subject)
            menubar = Menu(gui)
            
            #the treeview method is being used to show the teachers the grades that were assigned to the teacher
            gradesTable = ttk.Treeview(subjectGUI, columns = ("Name", "Grade", "Date assigned"), show = "headings")
            gradesTable.heading("Name", text = "Name")
            gradesTable.heading("Grade", text = "Grade")
            gradesTable.heading("Date assigned", text = "Date assigned")    
            gradesTable.grid()
            
            #this sql statement retrieves the subject id for the subject arguement that was passed into the function
            cursor.execute("SELECT subject_id FROM subjects WHERE subject = %s;", (subject,))
            subjectid = cursor.fetchone()
            
            #this parameterised sql statement is used to retrieve the student's name grade and the date that the grade was assigned on.
            cursor.execute("SELECT students.student_name, grades.grade, grades.date FROM students INNER JOIN grades ON grades.student_id = students.student_id WHERE grades.subject_id = %s;", (subjectid,))

            data = cursor.fetchall()
            for i in range(len(data)):
                #the student's data is being added onto the treeview
                gradesTable.insert("", "end", values = (data[i][0], data[i][1], data[i][2]))

            #this interface is used by teachers to add students to the class or remove them from the class
            def studentGUI():
                #this creates the new tab for the interface
                studentGUI = Toplevel(subjectGUI)
                #this sql statement retrieves all the students that are registered in the database
                cursor.execute("SELECT student_name FROM students;")
                names = cursor.fetchall()
                students = []
                classEmpty = False
                #I am looping through the fetched data so that it can be added onto an array.
                if names is None or not names:
                    classEmpty = True
                else:
                    #this gets every students name from the  result
                    for s in names: 
                        for student in s:
                            students.append(student)
                
                #if there is no-one in the class, the teacher would be unable to use the functionalities.
                if classEmpty == True:
                    Label(studentGUI, text = "There are no students who have currently registered. You can start adding students into your class(es) once they have been registered").grid()
                else:
                    #this creates a dropdown with every student that is on the array/database
                    s = StringVar(studentGUI)
                    s.set("select a student")
                    OptionMenu(studentGUI, s, *students).grid(column = 1, row = 1)
                    
                    #this function is designated to adding students to a class
                    def addStudent():
                        cursor.execute("SELECT subject_id FROM subjects WHERE subject = %s;", (subject,))
                        subjectid = cursor.fetchone()
                        
                        #this sql statement retrieves all students that are in the class
                        cursor.execute("SELECT student_name FROM studentinclass WHERE subject_id = %s AND student_name = %s;", (subjectid, s.get(),))
                        inClass = False

                        if cursor.fetchone() is not None:
                            #the student is in class so it throws an error to the teacher
                            self.messageBox("This student is already in this class.", "error")
                            inClass = True

                        #if the student is not in the class, then they would be added to the class and
                        if inClass == False:
                            if s.get() != "select a student":
                                self.messageBox(s.get() + " was added to this class.", "info")
                                
                                cursor.execute("SELECT subject_id FROM subjects WHERE subject = %s;", (subject,))
                                subjectid = cursor.fetchone()
                                #this sql statement retrieves the id that is associated with the chosen student (needed so that the student can be added to the database)
                                cursor.execute("SELECT student_id FROM students WHERE student_name = %s;", (s.get(),))
                                studentid = cursor.fetchone()
                                #this sql statement inserts the student to the class
                                cursor.execute("INSERT INTO studentinclass (subject_id, student_id, student_name) VALUES (%s, %s, %s);", (subjectid, studentid, s.get(),))
                                connection.commit()

                    #this function is called when the teacher wants to remove a student from a class       
                    def removeStudent():
                        cursor.execute("SELECT subject_id FROM subjects WHERE subject = %s;", (subject,))
                        subjectid = cursor.fetchone()
                        #this sql statement retrieves every student in the chosen class
                        cursor.execute("SELECT student_name FROM studentinclass WHERE subject_id = %s AND student_name = %s;", (subjectid, s.get(),))
                        inClass = False

                        if cursor.fetchone() is not None:
                            #the student was found
                            #this sql statement would remove the chosen student from the class in the database
                            cursor.execute("DELETE FROM studentinclass WHERE student_name = %s AND subject_id = %s;", (s.get(), subjectid,))
                            connection.commit()
                            self.messageBox(s.get() + " is no longer in this class.", "info")
                            inClass = True

                        #if the student was not in the class, it would throw an error to the teacher.
                        if inClass == False: #student is not in the class
                            if s.get() != "select a student":
                                self.messageBox("This student is not in this class.", "error")
                    
                    #these buttons are what the teacher clicks in order to add or remove the student.
                    Button(studentGUI, text = "-", command = removeStudent).grid(column = 0, row = 1)
                    Button(studentGUI, text = "+", command = addStudent).grid(column = 2, row = 1)

            # this function is one of the main functionalities for the teacher
            # student's grades are assigned through this function
            def setGrade(subject):
                setgrades = Toplevel(gui)

                cursor.execute("SELECT subject_id FROM subjects WHERE subject = %s;", (subject,))
                subjectid = cursor.fetchone()
                #this sql statement retrieves the students who are in the class
                cursor.execute("SELECT student_name FROM studentinclass WHERE subject_id = %s;", (subjectid,))

                names = cursor.fetchall()
                students = []
                classEmpty = False
                #i am looping through the retrieved data so that they can be added onto an array and hence be presented on a dropdown menu
                if names is None or not names:
                    classEmpty = True
                else:
                    #this gets every students name in the database
                    for s in names: 
                        for student in s:
                            #the names are added onto the array
                            students.append(student)

                #if there is no-one in the class, they would not be able to assign the grades so they must add students to the class
                if classEmpty == True:
                    Label(setgrades, text = "This class currently has no students. Please add students using the menu.").grid()
                else: #if there are students in the class
                    #this creates a dropdown so the teacher can select a teacher
                    s = StringVar(setgrades)
                    s.set("select a student")
                    #a dropdown for the teacher to select a student.   
                    Label(setgrades, text = "Student: ").grid(column = 0,row = 1)
                    OptionMenu(setgrades, s, *students).grid(column = 1,row = 1)
                    
                    grade = StringVar(setgrades)
                    grade.set("select a grade")
                    grades = ["A*","A","B","C","D","E","U"]
                    #the grades U-A* are put as a dropdown so the teacher can assign it to the student
                    Label(setgrades, text = "Grade: ").grid(column = 0,row = 3)
                    OptionMenu(setgrades, grade, *grades).grid(column = 1 ,row = 3)
                    
                    #this functions assigns the grade to the student
                    def updateGrades():
                        if grade.get() != "select a grade" and s.get() != "select a student":
                            cursor.execute("SELECT student_id FROM students WHERE student_name = %s;", (s.get(),))
                            studentid = cursor.fetchone()
                            date = time.strftime("%Y-%m-%d")      
                            #the grade is assigned to the student in the database
                            cursor.execute("INSERT INTO grades (grade_id, subject_id, student_id, grade, date) VALUES (DEFAULT, %s, %s, %s, %s);", (subjectid, studentid, grade.get(), date))
                            connection.commit()
                            self.messageBox("Grade: " + grade.get() + " was successfully set to " + s.get() + ".", "info")
                    #the "add" button is what the teacher clicks on to set the grade.
                    Button(setgrades, text = "add", command = updateGrades).grid()
                    connection.commit()

            #menu is created so that the teacher can see the different options
            studentMenu = Menu(menubar, tearoff = 0)
            studentMenu.add_command(label = "add/remove student", command = studentGUI)
            menubar.add_cascade(label = "Class", menu = studentMenu)

            gradesMenu = Menu(menubar, tearoff = 0)
            gradesMenu.add_command(label = "Set Grade", command = lambda: setGrade(subject))
            menubar.add_cascade(label = "Grades", menu = gradesMenu)

            subjectGUI.config(menu = menubar)
        
        #this function creates the interface for the teacher to convert a % to a grade
        def grade():
            global converter
            converter = Toplevel(gui)
            converter.title("Convert a % to a rough grade")
            #this function is used to convert percentages to a grade
            def convertGrade(): 
                percentage = percent.get()
                #checks if the percentage is greater than 100
                if percentage > 100:  
                    self.messageBox("Percentage cannot be higher than 100.", "error")
                elif percentage >= 82: #around 82% is an A*
                    self.messageBox("Grade: A*", "info")
                elif percentage >= 70:  #around 70% is an A
                    self.messageBox("Grade: A", "info")
                elif percentage >= 57:  #around 57% is an B
                    self.messageBox("Grade: B", "info")
                elif percentage >= 45:  #around 45% is an C
                    self.messageBox("Grade: C", "info")        
                elif percentage >= 30:  #around 30% is an D
                    self.messageBox("Grade: D", "info")
                elif percentage >= 20:  #around 20% is an E
                    self.messageBox("Grade: E", "info")
                elif 0 > percentage:
                    self.messageBox("% must be a number between 0 and 100.", "error")
                else:
                    self.messageBox("Grade: U", "info")
            
            percent = IntVar(converter)
            Label(converter, text = "%:").grid(column = 0,row = 1)
            Entry(converter, textvariable = percent).grid(column = 1,row = 1)
            #the "convert" button calls the convertGrade function and converts the % 
            Button(converter, text = "convert", command = convertGrade).grid()

        #this function would be used by teachers to add or remove a class
        def subjects():
            #this function is used by the teacher to add a class that they teach
            def addSubject():
                cursor.execute("SELECT subject_id FROM subjects WHERE subject = %s;", (s.get(),))
                subjectid = cursor.fetchone()
                #this retrieves the teachers that are in the chosen class (s.get()).
                cursor.execute("SELECT teacher_name FROM teacherinclass WHERE subject_id = %s AND teacher_name = %s;", (subjectid, self.getName(),))
                inClass = False
                if cursor.fetchone() is not None:
                    #the teacher is already in the class so an error is thrown
                    self.messageBox("You are already in this class.", "error")
                    inClass = True
               
                #if the teacher is not in the class, the system would add it to the database
                if inClass == False:
                    if s.get() != "select a subject":
                        #add the teacher to the class/subject array in both teachers table and subjects table
                        self.messageBox("You are now in this class.", "info")
                        cursor.execute("SELECT teacher_id FROM teachers WHERE teacher_name = %s;", (self.getName(),))
                        teacherid = cursor.fetchone()
                        #this sql statements inserts the teacher into the class's table.
                        cursor.execute("INSERT INTO teacherinclass (subject_id, teacher_id, teacher_name) VALUES (%s, %s, %s);", (subjectid, teacherid, self.getName(),))
                        connection.commit()  
                        classMenu.add_command(label = s.get(), command = lambda subject = s.get(): subjectGUI(subject))
                        
            #this function would be called if the teacher wanted to leave a class
            def removeSubject():
                cursor.execute("SELECT subject_id FROM subjects WHERE subject = %s;", (s.get(),))
                subjectid = cursor.fetchone()

                cursor.execute("SELECT teacher_name FROM teacherinclass WHERE subject_id = %s AND teacher_name = %s;", (subjectid, self.getName(),))

                inClass = False
                if cursor.fetchone() is not None:
                    #if the teacher was found, the system  would remove teacher from the class in the database
                    cursor.execute("SELECT teacher_id FROM teachers WHERE teacher_name = %s;", (self.getName(),))
                    teacherid = cursor.fetchone()
                    
                    cursor.execute("SELECT subject_id FROM subjects WHERE subject = %s;", (s.get(),))
                    subjectid = cursor.fetchone()
                    #the DELETE sql statement gets rid of the entry where the teacher is in the class.
                    cursor.execute("DELETE FROM teacherinclass WHERE teacher_id = %s AND subject_id = %s;", (teacherid, subjectid,))
                    connection.commit()

                    #this removes the subject from the menu
                    classMenu.delete(s.get())

                    self.messageBox("You are no longer in this class.", "info")
                    inClass = True

                #However, if the teacher is not in the class, an error would be called.
                if inClass == False: 
                    self.messageBox("You are not in this class.", "error")

            classGUI = Toplevel(gui)
            classGUI.geometry("250x250")
            
            #the following sql statement retrieves all the subjects avaialable 
            cursor.execute("SELECT subject FROM subjects;")
            subject = cursor.fetchall()
            subjects = []

            for s in subject: #get every subject in the database
                subjects.append(s[0])

            s = StringVar(classGUI)
            s.set("select a subject")
  
            OptionMenu(classGUI, s, *subjects).grid(column = 1, row = 1)
            #the following buttons would add or remove the teacher from a class when it is clicked
            Button(classGUI, text = "-", command = removeSubject).grid(column = 0, row = 1)
            Button(classGUI, text = "+", command = addSubject).grid(column = 2, row = 1)

        aboutMenu = Menu(menubar, tearoff = 0)
        aboutMenu.add_command(label = "Log Out", command = logOut)
        menubar.add_cascade(label = "Settings", menu = aboutMenu)
        classMenu = Menu(menubar, tearoff = 0)
        classMenu.add_command(label = "add/remove a subject", command = subjects)
        #this iterates through the classes that the teacher is in
        cursor.execute("SELECT subject_id FROM teacherinclass WHERE teacher_name = %s;", (self.getName(),))
        subjectid = cursor.fetchall()
        for subject in subjectid:
            if subject is None or not subject: 
                pass
            else:
                #the teacher is in the class so it is added to the dropdown
                for subj in subject:
                    cursor.execute("SELECT subject FROM subjects WHERE subject_id = %s;", (subj,))
                    classes = cursor.fetchone()
                    classMenu.add_command(label = classes[0], command = lambda: subjectGUI(classes[0]))

        menubar.add_cascade(label = "Classes", menu = classMenu)
        gradesMenu = Menu(menubar, tearoff = 0)
        gradesMenu.add_command(label = "Convert % to grade.", command = grade)
        menubar.add_cascade(label = "Grades", menu = gradesMenu)
        gui.config(menu = menubar)
        gui.mainloop()
        connection.close()

#the student class is used to instantiate students as objects. Like the teacher class, this class also inherits the methods of the School class.
class Student(School):
    def createStudent(self, window):
        connection = psycopg2.connect(host = "localhost", user = "postgres", password = "postgres", port = "5432", database = "school")
        cursor = connection.cursor()

        #the following checks if the student is in the validated students textfile
        studentsFile = open("validstudents.txt", "r") 
        validStudents = studentsFile.readlines() 
        validated = False
        #loops through each line in the textfile
        for student in validStudents: 
            #if the line is the same as the students name then it means that they are validated
            if self.getName() == student.strip().lower():
                validated = True
                #as the student is valid, the system would check if they are already in the database
                cursor.execute("SELECT student_name FROM students WHERE student_name = %s;", (self.getName(),))
                if cursor.fetchone() is not None:
                    #student exists in database since value is not null
                    self.messageBox("Already registered.", "error")               
                else:
                    #as the student does not exist, the system would check if the password is valid
                    if self.isPasswordValid(self.getPassword()) == True:
                        #if it is, then the student is added to the database
                        hashedPassword = PasswordHasher().hash(self.getPassword())
                        cursor.execute("INSERT INTO students (student_id, student_name, student_password) VALUES (DEFAULT , %s , %s);", (self.getName(), hashedPassword))
                        connection.commit()
                        connection.close()
                        self.messageBox("Success! You have been registered.", "info")   
                        window.after(3000, window.destroy)
        #if value of the Boolean validated did not change then that means the student is not valid
        if validated == False: 
            self.messageBox("You are not a validated student.", "error")

        connection.close()
        
    #this provides the main interface for the student.
    def sendGUI(self):
        connection = psycopg2.connect(host = "localhost", user = "postgres", password = "postgres", port = "5432", database = "school")
        cursor = connection.cursor() 
        #creates the tkinter window for the interface
        gui = Tk()
        gui.title("Grades+")
        gui.geometry("1500x800")
        menubar = Menu(gui)

        #this procedure would stop the program from running.
        def logOut():
            exit(0)

        #when this function is called, it shows the student their grades for the chosen subject
        def subjectGUI(subject):
            subjectGUI = Toplevel(gui)
            subjectGUI.title(subject)

            cursor.execute("SELECT subject_id FROM subjects WHERE subject = %s;", (subject,))
            subjectid = cursor.fetchone()
            
            cursor.execute("SELECT student_id FROM students WHERE student_name = %s;", (self.getName(),))
            studentid = cursor.fetchone()

            #this sql statement retrieves the date and grade that were assigned to the student for the class
            cursor.execute("SELECT grade, date FROM grades WHERE student_id = %s AND subject_id = %s;", (studentid, subjectid,))
            grades = cursor.fetchall()
            #to represent the grades, i am using treeview.
            gradesTable = ttk.Treeview(subjectGUI, columns = ("Grade", "Date assigned"), show = "headings")
            gradesTable.heading("Grade", text = "Grade")
            gradesTable.heading("Date assigned", text = "Date assigned")    
            gradesTable.grid()
            
            for i in range(len(grades)):
                gradesTable.insert("", "end", values = (grades[i][0], grades[i][1]))

        #the menu widget is used to allow the students to pick what they want to do
        settingsMenu = Menu(menubar, tearoff = 0)
        settingsMenu.add_command(label = "Log Out", command = logOut)
        menubar.add_cascade(label = "Settings", menu = settingsMenu)
        subjectMenu = Menu(menubar, tearoff = 0)
        
        cursor.execute("SELECT student_id FROM students WHERE student_name = %s;", (self.getName(),))
        student = cursor.fetchone()

        cursor.execute("SELECT subject_id FROM studentinclass WHERE student_id = %s;", (student,))
        subjectid = cursor.fetchall()

        #this would check what classes the student is in 
        for subject in subjectid:
            if subject is None or not subject: 
                pass 
            else: #student was found in a class
                for subj in subject:
                    #the class is added to a dropdown for the student to select if they want to see their grade.
                    cursor.execute("SELECT subject FROM subjects WHERE subject_id = %s;", (subj,))
                    classes = cursor.fetchone()
                    subjectMenu.add_command(label = classes[0], command = lambda subject = classes[0]: subjectGUI(subject))

        menubar.add_cascade(label = "Subjects", menu = subjectMenu)
        
        gui.config(menu = menubar)
        gui.mainloop()
        connection.close()
