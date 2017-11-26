"""This is a simple SQLite database interface inspired by SS13 
cargo requsitions orders. I made it to practice and understand
SQL and Databases.

Database used by this application has the following schema:
Table orders, with following columns - 
oID INTEGER PRIMARY KEY AUTOINCREMENT - row ID
ordererID INTEGER - ID for the person making an order
materials TEXT - requested materials 
orderdate TEXT - datetime request was made
decision TEXT - foremans approval or denial of particular request
foremanID INTEGER - ID of foreman who made the decision defined above
deliverydate TEXT - date of delivery for said request

Table orders, with following columns - 
ForemanID INTEGER PRIMARY KEY - row/foreman ID
name TEXT - foremans name
Totalorders - total count of orders accepted by this foreman

This programs attaches itself to an existing, compatible database in 
directory or creates a new one. 

The ui will check ID provided by the user, and if the ID is foremans ID
it will unlock additional functions. 

Non-foremans can only add new orders and check the orders they made.
Foremans, aside of above, can accept or deny orders made by other users.
For the sake of simplicity, deliverydate is assumed to be the time foreman accepted 
an order +10 minutes.

TODO:
- foreman password authentication
- port to flask
"""
import sqlite3
import re
import os
import sys
import itertools
import datetime


def search_for_dbfile():
    """This functions returns database file path from current directory. If one .db file is found, it return it.
    If more files are found, it requires user input to choose the right file. If filename was specified
    in the console, it tries to find it, otherwise it informs the user that the file does not exists."""
    if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
        print("file {} found".format(sys.argv[1]))
        return sys.argv[1]
    elif len(sys.argv) == 2 and not os.path.isfile(sys.argv[1]):
        print("file {0} not found, create desired file as new database or exit? (y/n)".format(sys.argv[1]))
        decision = confirm()
        if decision:
            return sys.argv[1]
        elif not decision:
            print("Goodbye")
            exit(0)
    else:
        filelist = [file for file in os.listdir('.') if os.path.isfile(file) \
                    and re.search("\.db$", file)]
        if len(filelist) == 0:
            print("no db file founde, creating new file cargo.db")
            return "cargo.db"
        elif len(filelist) > 1:
            print("more thank 1 database files found, select one by typing numer before filename")
            for file in filelist:
                print("{0} - {1}".format(filelist.index(file) + 1, file))
            while True:
                userselect = input("> ")
                try:
                    return filelist[int(userselect) - 1]
                except ValueError:
                    print("wrong input, try again")
        else:
            return ''.join(filelist)


def check_schema(DbObject):
    """replace with pragmas? 
    BUG! gdy argv=2 - solved"""
    rightschema = [('oID', 'INTEGER', 1), ('ordererID', 'INTEGER'), ('materials', 'TEXT'), ('orderdate', 'TEXT'), ('decision', 'TEXT'), ('foremanID', 'INTEGER'), ('deliverydate', 'TEXT'), ('ForemanID', 'INTEGER', 1), ('name', 'TEXT'), ('Totalorders', 'INTEGER')]
    schematocheck = []
    for tablename in tablenames:
        schema = DbObject.execute('PRAGMA TABLE_INFO({})'.format(tablename)).fetchall()
        for tup in schema:
            if tup[-1]:
                toappend = list(tup[1:3])
                toappend.append(tup[-1])
                schematocheck.append(tuple(toappend))
            else:
                schematocheck.append(tup[1:3])
    print(schematocheck)
    if not schematocheck:
        print("DB file is empty. creating new db.")
        return create_db(DbObject)
    for row in rightschema:
        if row in schematocheck:
            print("row ok")
        else:
            print("Db is kill. Use with another file, or create a new DB.")
            exit(0)
    print("Database verified")

def create_db(DbObject):
    """moved """
    DbObject.execute('CREATE TABLE Orders (oID INTEGER PRIMARY KEY AUTOINCREMENT,ordererID INTEGER,'\
                ' materials TEXT,  orderdate TEXT, decision TEXT,  foremanID INTEGER, deliverydate TEXT)')
    DbObject.execute('CREATE TABLE Foremans (ForemanID INTEGER PRIMARY KEY'\
                ', name TEXT, Totalorders INTEGER)')
    print("tables created succesfully.")
    print("prepare foreman's data for input. select q whe all foreman data is inserted")
    foremanlist = []
    while True:
        foremanid = input("enter foreman 3 digit ID >")
        foremanname = input("enter foreman name (no space allowed) >").strip()
        if verify_id(foremanid) and foremanid not in itertools.chain.from_iterable(foremanlist):
            foremanlist.append((foremanid, foremanname))
        elif foremanid == "q" or foremanname == "q":
                return DbObject.executemany('INSERT INTO Foremans VALUES (?,?,0)', foremanlist)
        else:
            print("wrong Foreman ID")

def verify_id(ID):
    if re.match("[0-9][0-9][0-9]$", ID):
        return True
    else:
        return False

def string_cleanup(string):
    return ''.join(char for char in string if char.isalnum())

def none_cleanup(tuple):
    """passing None to string.format returns an exception, this function remedies this."""
    cleanedtuple = []
    for string in tuple:
        if not string:
            cleanedtuple.append("---")
        else:
            cleanedtuple.append(string)
    return cleanedtuple

def confirm():
    while True:
        decision = input("> ")
        if decision == "y":
            return True
        elif decision == "n":
            return False
        else:
            print("Wrong input - select 'y' for Yes, 'n' for No.")
            
def ordersubmit(DbObject, ID):
    while True:
        print("To submit requisition order, follow steps below")
        ordermaterials = input('Type in requested materials >')
        if ordermaterials:
            return DbObject.execute('INSERT INTO Orders (ordererID, materials, orderdate, decision, foremanID, deliverydate) VALUES (?,?,?, null, null, null)', (ID, ordermaterials, datetime.datetime.now().strftime(TIMEFORMAT)))

def ordersreview(DbObject, ID):
    """todo: materials line wrap-up"""
    print("Your orders below:")
    print("|{:^8}|{:^9}|{:^25}|{:^12}|{:^8}|{:^9}|{:^12}|".format(*columnnamesorders))
    for tuple in DbObject.execute('select * from Orders where {0} = {1}'.format(columnnamesorders[1], string_cleanup(ID))):
        print("|{:^8}|{:^9}|{:^25}|{:^12}|{:^8}|{:^9}|{:^12}|".format(*none_cleanup(tuple)))

def acceptorder():
    pass
    
def reviewallorders():
    pass

def foremanlogin(DbObject, ID):
    idlist = [row[0] for row in DbObject.execute('SELECT {0} FROM foremans where {0} = {1}'.format(columnnameforemans[0], ID)).fetchall()]
    if idlist:
        global actions
        actions.update({"4":acceptorder, "5":reviewallorders})
        return True
    else:
        return False

def exitfunction(DbObject, ID):
    DbObject.commit()
    DbObject.close()
    print("Bye!")
    exit(0)

TIMEFORMAT = "%Y-%m-%d %H:%M:%S"
actions = {"1": ordersubmit, "2":ordersreview, "3": foremanlogin, "q":exitfunction}
tablenames = ('Orders', 'Foremans',)
columnnamesorders = ('oID' ,'ordererID', 'materials',  'orderdate', 'decision', 'foremanID', 'deliverydate')
columnnameforemans = ('ForemanID', 'name', 'Totalorders')

def ui(DbObject):
    """todo"""
    #actions = {"1": ordersubmit, "2":ordersreview, "3": foremanlogin}
    print("Welcome to the SS13 cargo requisition interface.\nSelect action:\n1. Submit an order\n2. Review your orders3.\n3. Foreman log-in \n 4. quit")
    ID = ""
    while verify_id(ID) == False:
        ID = input('please provide your id > ')
    Loginasforeman = foremanlogin(DbObject, ID)
    while True:
        selection  = input('> ')
        print(Loginasforeman)
        print(actions)
        if selection in list(actions.keys()):
            print (actions[selection](DbObject, ID))
        else:
            print("wronge selection, try again.")
            
def mainloop():
    """todo"""
    dbfile = search_for_dbfile()
    DbObject = sqlite3.connect(dbfile)
    check_schema(DbObject)
    ui(DbObject)

if __name__ == "__main__":
    mainloop()


