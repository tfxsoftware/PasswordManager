from tkinter import *
from tkinter.ttk import Treeview
from tkinter import ttk
from tkinter import messagebox
import sqlite3



## BACKEND ##
class database():
    def db_connect(self):
        self.conn_accounts = sqlite3.connect("accounts.db")
        self.cursor = self.conn_accounts.cursor()

    def db_disconnect(self):
        self.cursor.close()

    def create_table(self):
        self.db_connect()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS accounts(
        email VARCHAR2(40) PRIMARY KEY,
        password VARCHAR2(40) NOT NULL);
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS userinfo(
        accountname VARCHAR2(40) NOT NULL,
        login_key VARCHAR2(40) NOT NULL,
        login_password VARCHAR2(40) NOT NULL,
        obs VARCHAR2(500),
        userid VARCHAR2CHAR(40), 
        FOREIGN KEY(userid) REFERENCES accounts(email));
        """)
        self.conn_accounts.commit()
        self.db_disconnect()

    def create_account(self):
        self.db_connect()
        if (self.newaccount_password_entry.get() == "" or self.newaccount_email_entry.get() == ""):
            messagebox.showinfo('Attention!','Please fill all blanks')   
        elif self.newaccount_password_entry.get() != self.newaccount_repassword_entry.get():
            messagebox.showerror('Error!', 'Password does not match!')
        elif self.newaccount_email_entry.get() == 'admin':
            messagebox.showerror("Error!","Cant create new 'admin' user")
        else:
            try:
                self.db_connect()
                self.newrepass = self.newaccount_repassword_entry.get()
                self.newpass = self.newaccount_password_entry.get()
                self.newacc = self.newaccount_email_entry.get()
                self.cursor.execute("""INSERT INTO accounts(email, password) VALUES(?,?)""",(self.newacc, self.newpass))
                self.conn_accounts.commit()
                self.newaccount_password_entry.delete(0,END)
                self.newaccount_repassword_entry.delete(0,END)
                self.newaccount_email_entry.delete(0,END)    
                self.db_disconnect()
                messagebox.showinfo('Success!', 'Account succesfully created!')
            except:
                messagebox.showinfo('Error!', 'E-mail already registered')

    def account_validation(self):
        self.valid_email = "admin"
        self.valid_password = "admin"
        self.db_connect()
        self.results = self.cursor.execute("SELECT * FROM accounts WHERE email = ?",(self.login_email_entry.get(),))
        for row in self.results:
            self.valid_email = row[0]
            self.valid_password = row[1]
        if  self.valid_email == self.login_email_entry.get() and self.valid_password == self.login_password_entry.get():
            self.main_window_config()
        else:
            messagebox.showwarning('Error!', 'Invalid credentials!')

    def new_entry(self):
        self.db_connect()
        self.used_names = ""
        self.existing_entries = self.cursor.execute("SELECT * FROM userinfo WHERE userid= ? AND accountname = ?",(self.valid_email,self.newentry_name_entry.get(),))
        for row in self.existing_entries:
            self.used_names = row[0]

        if self.newentry_name_entry.get() == "":
            messagebox.showwarning('Error!','Name cant be empty!')
        elif self.used_names != "":
            messagebox.showwarning('Error!','Name already used!')
        else:
            self.cursor.execute("INSERT INTO userinfo (accountname, login_key, login_password, obs, userid) VALUES(?,?,?,?,?)",
            (self.newentry_name_entry.get(),self.newentry_key_entry.get(),self.newentry_pwd_entry.get(),self.newentry_obs_text.get('1.0','end'),self.valid_email,))
            self.conn_accounts.commit()
            self.newentry_name_entry.delete(0,END)
            self.newentry_key_entry.delete(0,END)
            self.newentry_pwd_entry.delete(0,END)
            self.newentry_obs_text.delete('1.0','end')
          

        self.db_disconnect()
        self.select_treeview()
 
    def select_treeview(self):
        self.main_pwd_treeview.delete(*self.main_pwd_treeview.get_children())
        self.db_connect()
        self.treeview_list = self.cursor.execute("SELECT * FROM userinfo WHERE userid = ? ORDER BY accountname ASC",(self.valid_email,))
        for row in self.treeview_list:
            self.main_pwd_treeview.insert("",END, values=row)
        self.db_disconnect()

    def select_click(self, event):
        selection = self.main_pwd_treeview.item(self.main_pwd_treeview.selection())
        self.name_selected = selection['values'][0]
        self.login_selected = selection['values'][1]
        self.pwd_selected = selection['values'][2]
        self.obs_selected = selection['values'][3]

    def edit_entry(self):
        answer = messagebox.askyesno('Warning!','Are you sure you want to edit this entry?')
        if answer:
                self.db_connect()
                self.cursor.execute('DELETE FROM userinfo WHERE accountname = ? AND userid = ?',(self.name_selected, self.valid_email))
                self.conn_accounts.commit()
                self.cursor.execute('INSERT INTO userinfo (accountname, login_key, login_password, obs, userid) VALUES(?,?,?,?,?)',
                (self.name_selected,self.editentry_login_entry.get(),self.editentry_pwd_entry.get(),self.editentry_obs_text.get('1.0','end'),self.valid_email,))
                self.conn_accounts.commit()
                self.select_treeview()
                self.db_disconnect()
                messagebox.showinfo('Success!', 'Entry succesfully edited!')
                
        else:
            pass

    def remove_entry(self):
        answer = messagebox.askyesno('Warning!','Are you sure you want to delete this entry?')
        if answer:
            try:
                self.db_connect()
                self.cursor.execute('DELETE FROM userinfo WHERE accountname = ? AND userid = ?',(self.name_selected, self.valid_email))
                self.conn_accounts.commit()
                self.select_treeview()
                self.db_disconnect()
            except:
                messagebox.showwarning('Error!','No entry selected')
        else:
            pass
   
    def exit_application(self):
        answer =  messagebox.askyesno('Warning!','Are you sure you want to exit?')
        if answer:
            self.main_window.destroy()
        else:
            pass
    
    def logout(self):
        answer =  messagebox.askyesno('Warning!','Are you sure you want to logout?')
        if answer:
            self.name_selected=[]
            self.main_window.destroy()
            self.login_window_config()
        else:
            pass

    
## FRONTEND ##
class  App(database):
    def __init__(self):
        self.create_table()
        self.login_window_config() 

    def login_window_config(self):
        self.login_window = Tk()
        self.login_window.title('Password Manager')
        self.login_window.geometry('400x100')
        self.login_window.resizable(FALSE, FALSE)


        self.login_email_label = Label(self.login_window, text='E-mail: ')
        self.login_password_label = Label(self.login_window, text='Password: ')
        self.login_email_entry  = Entry(self.login_window)
        self.login_password_entry = Entry(self.login_window, show="*")
        self.login_button = Button(self.login_window, text='Login', command=self.account_validation, width=13)
        self.newuser_button = Button(self.login_window, text='New user', command=self.newaccount_window_config, width=13)
        self.exit_button = Button(self.login_window, text='Exit', command=self.login_window.destroy, width=13)

        self.login_email_label.place(x=10, y=20)
        self.login_password_label.place(x=200, y=20)
        self.login_email_entry.place(x=55,y=22)
        self.login_password_entry.place(x=260,y=22)
        self.login_button.place(x=10, y=70)
        self.newuser_button.place(x=120, y=70)
        self.exit_button.place(x=290,y=70)
        self.login_window.mainloop()

    def newaccount_window_config(self):
        self.newaccount_window = Toplevel()
        self.newaccount_window.title('New User')
        self.newaccount_window.geometry("260x160")
        self.newaccount_window.resizable(False, False)
        self.newaccount_window.transient(self.login_window)
        self.newaccount_window.focus_force()
        self.newaccount_window.grab_set()

        self.newaccount_email_label = Label(self.newaccount_window, text="New Email: ")
        self.newaccount_password_label = Label(self.newaccount_window, text="New Password: ")
        self.newaccount_repassword_label = Label(self.newaccount_window, text="Re-enter Password: ")
        self.newaccount_email_entry = Entry(self.newaccount_window)
        self.newaccount_password_entry = Entry(self.newaccount_window, show="*")
        self.newaccount_repassword_entry = Entry(self.newaccount_window, show="*")
        self.newaccount_create_button = Button(self.newaccount_window, text="Create account", command=self.create_account, width=13)
        self.newaccount_return_button = Button(self.newaccount_window, text="Return to Login", command=self.newaccount_window.destroy, width=13)


        self.newaccount_email_label.place(x=10,y=10)
        self.newaccount_password_label.place(x=10,y=50)
        self.newaccount_repassword_label.place(x=10, y=90)
        self.newaccount_email_entry.place(x=120, y=10)
        self.newaccount_password_entry.place(x=120,y=50)
        self.newaccount_repassword_entry.place(x=120,y=90)
        self.newaccount_create_button.place(x=10,y=130)
        self.newaccount_return_button.place(x=150,y=130)

    def main_window_config(self):

        self.login_window.destroy()
        self.main_window = Tk()
        self.main_window.title('Password Manager: ' + self.valid_email)
        self.main_window.geometry("750x380")
        self.main_window.resizable(FALSE, FALSE)

        self.main_manage_label = Label(self.main_window, text="SAVED PASSWORDS: ")
        self.main_pwd_treeview = Treeview(self.main_window, height=15, columns=("col1, col2, col3, col4"))
        self.main_pwd_treeview.heading("#0", text="")
        self.main_pwd_treeview.heading("#1", text="Name")
        self.main_pwd_treeview.heading("#2", text="Login")
        self.main_pwd_treeview.heading("#3", text="Password")
        self.main_pwd_treeview.heading("#4", text="Additional info:")
        self.main_pwd_treeview.column("#0", width=0, stretch=NO)
        self.main_pwd_treeview.column("#1", width=150, anchor=W)
        self.main_pwd_treeview.column("#2", width=150)
        self.main_pwd_treeview.column("#3", width=150)
        self.main_pwd_treeview.column("#4", width=150)
        self.main_pwd_treeview_scroll = Scrollbar(self.main_window, orient="vertical")
        self.main_pwd_treeview.configure(yscroll=self.main_pwd_treeview_scroll.set)
        self.main_pwd_treeview.bind("<ButtonRelease-1>", self.select_click)
        self.main_new_button = Button(self.main_window,    text="New Entry", command=self.newentry_window_config, width=13)
        self.main_edit_button = Button(self.main_window,   text="  View/Edit Entry   ", command=self.editentry_window_config, width=13)
        self.main_remove_button = Button(self.main_window, text="    Remove Entry    ", command=self.remove_entry, width=13)
        self.main_exit_button = Button(self.main_window,  text="         Exit        ", command=self.exit_application, width=13)
        self.main_logout_button = Button(self.main_window,  text="Logout", command=self.logout, width=13)

        self.main_manage_label.place(x=10,y=10)
        self.main_pwd_treeview.place(x=10,y=40)
        self.main_pwd_treeview_scroll.place(x=596, y=40, height=325.5)
        self.main_new_button.place(x= 630,y=40)
        self.main_exit_button.place(x=630,y=340)
        self.main_edit_button.place(x=630,y=80)
        self.main_remove_button.place(x=630,y=120)
        self.main_logout_button.place(x=630,y=300)


        

        self.select_treeview()
        self.main_window.mainloop()

    def newentry_window_config(self):
        self.newentry_window = Toplevel()
        self.newentry_window.title('New Entry')
        self.newentry_window.geometry("330x430")
        self.newentry_window.resizable(False, False)
        self.newentry_window.transient(self.main_window)
        self.newentry_window.focus_force()
        self.newentry_window.grab_set()


        self.newentry_new_label = Label(self.newentry_window, text="New Entry: ")
        self.newentry_name_label = Label(self.newentry_window, text="Account name: ")
        self.newentry_login_label = Label(self.newentry_window, text="Login: ")
        self.newentry_pwd_label = Label(self.newentry_window, text="Password: ")
        self.newentry_obs_label = Label(self.newentry_window, text="Additional info: ")
        self.newentry_name_entry = Entry(self.newentry_window)
        self.newentry_key_entry = Entry(self.newentry_window)
        self.newentry_pwd_entry = Entry(self.newentry_window)
        self.newentry_obs_text = Text(self.newentry_window,width=15,height=10)
        self.newentry_add_button = Button(self.newentry_window, text="ADD Entry", command=self.new_entry, width=13)
        self.newentry_return_button = Button(self.newentry_window, text="Return", command=self.newentry_window.destroy, width=13)
        
        
        self.newentry_new_label.place(x=10,y=10)
        self.newentry_name_label.place(x=10,y=50)
        self.newentry_login_label.place(x=10,y=90)
        self.newentry_pwd_label.place(x=10,y=130)
        self.newentry_obs_label.place(x=10,y=170)
        self.newentry_name_entry.place(x=100,y=50)
        self.newentry_key_entry.place(x=100,y=90)
        self.newentry_pwd_entry.place(x=100,y=130)
        self.newentry_obs_text.place(x=100,y=170)
        self.newentry_add_button.place(x=10,y=400)
        self.newentry_return_button.place(x=220,y=400)

    def editentry_window_config(self):
        try:
            if self.name_selected == []:
                messagebox.showwarning('Error!','No entry selected')
            else:
                self.editentry_window = Toplevel()
                self.editentry_window.title('View Entry')
                self.editentry_window.geometry("330x430")
                self.editentry_window.resizable(False, False)
                self.editentry_window.transient(self.main_window)
                self.editentry_window.focus_force()
                self.editentry_window.grab_set()


                self.editentry_view_label = Label(self.editentry_window, text="View Entry: ")
                self.editentry_name_label = Label(self.editentry_window, text="Account name: ")
                self.editentry_login_label = Label(self.editentry_window, text="Login: ")
                self.editentry_pwd_label = Label(self.editentry_window, text="Password: ")
                self.editentry_obs_label = Label(self.editentry_window, text="Additional info: ")
                self.editentry_accountname_entry = Label(self.editentry_window, text=self.name_selected, foreground="green")
                self.editentry_login_entry = Entry(self.editentry_window)
                self.editentry_pwd_entry = Entry(self.editentry_window)
                self.editentry_obs_text = Text(self.editentry_window,width=15,height=10)
                self.editentry_add_button = Button(self.editentry_window, text="Edit Entry", command=self.edit_entry, width=13)
                self.editentry_return_button = Button(self.editentry_window, text="Return", command=self.editentry_window.destroy, width=13)

        
        
                self.editentry_view_label.place(x=10,y=10)
                self.editentry_name_label.place(x=10,y=50)
                self.editentry_login_label.place(x=10,y=90)
                self.editentry_pwd_label.place(x=10,y=130)
                self.editentry_obs_label.place(x=10,y=170)
                self.editentry_accountname_entry.place(x=100,y=50)
                self.editentry_login_entry.place(x=100,y=90)
                self.editentry_pwd_entry.place(x=100,y=130)
                self.editentry_obs_text.place(x=100,y=170)
                self.editentry_add_button.place(x=10,y=400)
                self.editentry_return_button.place(x=220,y=400)

                self.editentry_login_entry.insert(0, self.login_selected)
                self.editentry_pwd_entry.insert(0, self.pwd_selected)
                self.editentry_obs_text.insert(1.0,self.obs_selected)
        
        except:
            messagebox.showwarning('Error!','No entry selected')

App()