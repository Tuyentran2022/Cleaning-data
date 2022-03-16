import datetime
import pandas as pd
import os
import openpyxl
import re

# Read excel file
messy_df = pd.read_excel(os.path.abspath("messy.xlsx"), engine='openpyxl', sheet_name='test')

#TODO 1: Clean the names of columns to lowercase separated by “_”, remove any empty column if necessary

# Rename the header in the dataframe
new_header = ['cust_id', 'join%_date', 'Empty column', 'mobiles', 'fll_nam']
messy_df.columns = new_header

# Remove a 'Empty column' column in the dataframe
messy_df.drop(labels='Empty column', axis=1, inplace=True)

#TODO 2: Change the date column to the same format ‘YYYY-MM-DD’.

list_date = messy_df['join%_date'].values.tolist()
# Create a new column which converts dd/mm/yy' to 'yyyy-mm-dd'
list_dt1 = []
for dt in list_date:
    # Find date that has a format 'dd/mm/yy' and replace it by 'yyyy-mm-dd'
    match = re.match(r'\d{2}/\d{2}/\d{2}', str(dt))
    if match:
        date = datetime.datetime.strptime(match.group(), '%d/%m/%y')
        list_dt1.append(date.strftime('%Y-%m-%d'))
    else:
        list_dt1.append('')

messy_df['dt1'] = list_dt1

# Create a new column which converts 'yyyy-mm-dd hh:mm:s+' to 'yyyy-mm-dd'
list_dt2 = []
for dt in list_date:
    # Find date that has a format yyyy-mm-dd hh:mm:s+' and replace it by 'yyyy-mm-dd'
    match = re.match(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{10}', str(dt))
    if match:
        # unless we use [0:10], the ouput will return an error 'unconverted data remains: '
        # match.group()[0:10] will return a string that has a format
        date = datetime.datetime.strptime(match.group()[0:10], '%Y-%m-%d')
        list_dt2.append(date.strftime('%Y-%m-%d'))
    else:
        list_dt2.append('')

messy_df['dt2'] = list_dt2


# Create a new column which converts 'yyyymmdd' (integer) to 'yyyy-mm-dd'
list_dt3 = []
for dt in list_date:
    # Find date that has a format 'dd/mm/yy' and replace it by 'yyyy-mm-dd'
    match = re.match(r'\d{8}', dt)
    if match:
        date = datetime.datetime.strptime(match.group(), '%Y%m%d')
        list_dt3.append(date.strftime('%Y-%m-%d'))
    else:
        list_dt3.append('')

messy_df['dt3'] = list_dt3

# Combine 3 columns into one column, and then replace the values of 'join%_date' by that of column created
# We use functions agg, lambda and join to do it.
columns_combined = ['dt1', 'dt2', 'dt3']
messy_df['join%_date'] = messy_df[columns_combined].agg(
    lambda x: "".join(x.values), axis=1).T

# Drop 3 temporary columns
messy_df = messy_df.drop(columns=['dt1', 'dt2', 'dt3'])

# Change dtype from 'object' to 'datetime' to support other tasks
messy_df['join%_date'] = pd.to_datetime(messy_df['join%_date'], format='%Y-%m-%d') #dtypes datetime64[ns]

#TODO 3: Change the name column to the title case (e.g: Jason Mraz)
messy_df['fll_nam'] = messy_df['fll_nam'].str.strip() # remove spaces
messy_df['fll_nam'] = messy_df['fll_nam'].str.lower() # convert to lower
messy_df['fll_nam'] = messy_df['fll_nam'].str.title()

#TODO 4: Make a new “email” column with the form:{last_name}.{first_name}.{id}@yourcompany.com

# Add 2 new columns to the existing dataframe
new_columns = ['first_name', 'last_name']
messy_df[new_columns] = messy_df['fll_nam'].str.split(expand=True)

# create a list of email in order to create for
create_email = list(map(lambda a, b, c: f"{a}.{b}.{c}@yourcompany.com",
                        messy_df["last_name"], messy_df["first_name"], messy_df["cust_id"]))
messy_df['email'] = create_email

#TODO 5: Change the phone number column to the format “84……”

# Remove syntax "+", and the first digit "0" in each telephone number
messy_df["mobiles"] = messy_df["mobiles"].astype(str)
messy_df["mobiles"] = messy_df["mobiles"].str.strip()

# Create a dict_list (key and list of values)
dict_list = messy_df.to_dict(orient='list')
list_str = []

# the standard number of digits in each telephone number is 10(the initial number doesn't start from "01") and 11 (The other starts from 01)
# Based on the mentioned standard, we consider the length of the number and 2 first digits
# Due to removing "+" and "0", the valid number of digits decreases to 9 and 10, we add "84" to the beginning of each number
# Others have 84 at the 2 first position, we still keep them
for nbr in dict_list["mobiles"]:
    # nbr[0:2] == 84 and len(nbr) == (11, 12): pass
    if len(nbr) == 9 or len(nbr) == 10:  # removed "0"
        list_str.append("84" + nbr[0:])
    else:
        list_str.append(nbr)

messy_df["mobiles"] = list_str

#TODO 6: Find any duplicated ID and remove those who join later.

# Sort data frame by the columns 'join%_date'
messy_df = messy_df.sort_values(by='join%_date')

# Drop duplicated cust_id based on the joining date
messy_df = messy_df.drop_duplicates('cust_id', keep='first')
messy_df = messy_df.sort_values('cust_id')
#TODO 7: Filter those who join since 2019 and export to a csv file, delimited by “|”, file name “emp_2019.csv”
messy_df = messy_df.reset_index(drop=True)

# Extract 'year' from the 'join%_date' column
a = pd.DatetimeIndex(messy_df['join%_date']).year
filter_2019 = messy_df[a == 2019]

# create a new csv file delimited by “|”
print(filter_2019.to_csv('emp_2019.csv', sep='|'))
