#!/usr/bin/python
import sys
import psycopg2

##define error message
def error(msg):
    print ("        Error: %s", [msg])
    print ("\n")
    sys.exit()

##connect to a database##
try:
	con = psycopg2.connect(database='mghorbal', user='mickey',password='MoUsE')
except psycopg2.DatabaseError as message:
	error(message)

curs = con.cursor()

print ("		Welcome to the Store Terminal		")
print ("        --------------------------------------------")
print ("\n")
command = input ("Are you a: \n(1) New customer \n(2) Existing customer \nEnter 1 or 2: ")

if command == '1': 
#order input
    customer = input("Sale to customer named: ")
    address = input("Ship to address: ")
    try:
        curs.execute("INSERT INTO customers VALUES('{cust}', '{add}') returning customerid".format(cust=customer, add=address))
        customerid = curs.fetchone()[0]
    except psycopg2.DatabaseError as message:
        error(message)
    else:
        con.commit() 
#
elif command == '2':
    try:
        customer = input("Please enter customer named: ")
        curs.execute("SELECT customerid FROM customers WHERE name = '{cust}'".format(cust=customer))
        customerid = curs.fetchone()[0]
        curs.execute("SELECT address FROM customers WHERE name = '{cust}'".format(cust=customer))
        address = curs.fetchone()[0]
        change = input("Would you like to update this address: {add}? ".format(add=address))
        if change == 'Yes' or change == 'yes':
            address = input ("Please enter new address: ")
            try:
                curs.execute("UPDATE customers SET address = '{add}' WHERE name = '{cust}'".format(add=address, cust=customer))
            except psycopg2.DatabaseError as message:
                error(message)
            else:
                con.commit()     
    except psycopg2.DatabaseError as message:
        error(message)
    else:
        con.commit() 

curs.execute("INSERT INTO orders (date, customerid) VALUES(current_date, {custid}) returning orderid".format(custid=customerid))
orderid = curs.fetchone()[0]
print ( "The order ID is ", orderid)

##ordering products##
print ("itemname          price")
print ("-----------------------")
try: 
	curs.execute("SELECT itemname, price FROM inventory")
except psycopg2.DatabaseError as message:
    error(message)
    con.rollback()
for inventory in curs.fetchall():
    print ("{:15s} {:7.2f}".format(inventory[0], inventory [1]))
finished = False
while finished is False:
	product=input("Pick a product: ")
	qty =input("How many {prod}s would you like to purchase? ".format(prod=product))
	try:
		curs.execute ("SELECT itemid FROM inventory where itemname = '{prod}'".format(prod=product))
		itemid = curs.fetchone()[0]
		curs.execute("INSERT INTO purchases VALUES( {ordid}, {itemid}, {qty})".format(ordid=orderid, itemid=itemid, qty=qty))
	except psycopg2.DatabaseError as message: 
		error (message)
		con.rollback()
	else: 
		con.commit()
	repeat = input("Would you like to add another item? ")
	if repeat == "No" or repeat == "no" : finished = True

# get the resulting table, a list of lists
print ("----------------------------")
print ("       FINAL RECIEPT		")
print ("----------------------------")
print ("Sale to:", customer)
print ("Product   Quantity   Price   Total")
print ("------------------------------------")
total = 0		# note: 0.0 is float, incompatible with Decimal (numeric)
try: 
	curs.execute("SELECT inventory.itemname, purchases.quantity, inventory.price, inventory.price*purchases.quantity FROM inventory LEFT OUTER JOIN purchases ON purchases.itemid = inventory.itemid WHERE purchases.orderid=%s",[orderid])
except psycopg2.DatabaseError as message:
	error(message)
	con.rollback()
else:
	con.commit
purchases = curs.fetchall()
for row in purchases:
  print ("{:13s} {:4d} {:7.2f} {:7.2f}".format(row[0], row[1], row[2], row[3]))
  total += row[3]
print ("{:26s} {:7.2f}".format('Grand total',total))

curs.close()
con.close() 

