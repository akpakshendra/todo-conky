#!/usr/bin/python

# reding files in python
# from __future__ import print_function
# f = open('data');
# for line in f:

# python argument parsing
import argparse
parser = argparse.ArgumentParser()

# sql lite
import sqlite3

# handling time
import time


#-----------------------------------------------------------------------
# create the table, must be called for the first time, the scripts however calls this anyways at the start
def init(args):

  # get the global connection
  conn = sqlite3.connect('todo.db')

  # get a cursor to database
  cursor = conn.cursor()

  # create the tables
  cursor.execute(''' CREATE TABLE IF NOT EXISTS todo (
    'id' integer PRIMARY KEY AUTOINCREMENT NOT NULL,
    'date' text,
    'title' text NOT NULL UNIQUE,
    'desc' text,
    'remind' text,
    'focus' int default 0,
    'daily' int default 0
  )''')

  # commit and close the connection
  conn.commit()
  conn.close()

#-------------------------------------------------------------------------


#-----------------------------------------------------------------------
# list the todosby id
def list(args, verbosity = True):

  # get the global connection
  conn = sqlite3.connect('todo.db')

  # get a cursor to database
  cursor = conn.cursor()

  # select everything from table
  cursor.execute("SELECT * FROM todo ORDER BY id ASC")

  # get all the rows
  rows = cursor.fetchall()
  count = len(rows)

  # print them all
  for row in rows:
    print("id: %d, date: %s, title: %s,  desc: %s, remind %s, focus %d, daily %d"%row);

  # close the connection
  conn.close()

#-------------------------------------------------------------------------


#-----------------------------------------------------------------------
# add a new todo
def add(args):

  # get the global connection
  conn = sqlite3.connect('todo.db')

  # get a cursor to database
  cursor = conn.cursor()

  # get the title
  title = args.title.strip()

  # handling the errors
  error_count = 0
  errors = []

  # mapping months to the number of days in the months
  month_to_day = [None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

  # check the date, if not available set it to todays date
  # first of all get todays date
  today_day, today_month, today_year = int(time.strftime('%d')), int(time.strftime('%m')), int(time.strftime('%Y'))
  # alidate the day passed if it is passed
  if(args.date):

    try:
      day, month, year = tuple(args.date.strip().split('-',3))
      # check the year

      try:
        # first check if it a number or not
        try:
          year = int(year)
        except ValueError:
          raise Exception("DateError : Year is invalid")
        # check if the year has passed
        if(year < today_year):
          raise Exception("DateError : Year has already passed")
        # change the day_to_month map if the year is a leap year, set feb to 29 days
        if(year%4 == 0 and year%400 != 0):
          month_to_day[2] = 29;
      except Exception as e:
        error_count = error_count + 1
        errors.append(e.args[0])

      # check the month
      try:
        # first check if it a number or not
        try:
          month = int(month)
        except ValueError:
          raise Exception("DateError : Month is invalid")
        # check if this is a valid month or not
        if(month < 1 or month > 12):
          raise Exception("DateError : Month month in not possible")
        # check if the month has passed
        if(year == today_year and month < today_month):
          raise Exception("DateError : For this year, this month had already passed")
      except Exception as e:
        error_count = error_count + 1
        errors.append(e.args[0])

      # check the day
      try:
        # first check if it a number or not
        try:
          day = int(day)
        except ValueError:
          raise Exception("DateError : Day is invalid")
        # check if this is a valid month or not
        if(not(month < 1 or month > 12) and (day < 1 or day > month_to_day[month])):
          raise Exception("DateError : Day is not possible in this month")
        # check if the day has passed
        if(year == today_year and month == today_month and day < today_day):
          raise Exception("DateError : For this month and year, the day has already passed")
      except Exception as e:
        error_count = error_count + 1
        errors.append(e.args[0])

    except ValueError:
      error_count = error_count + 1
      errors.append(e.args[0])

    except Exception as e:
      error_count = error_count + 1
      errors.append(e.args[0])

  else:
    day, month, year = today_day, today_month, today_year;

  # form the solid date
  date = str(day) + '-' + str(month) + '-' + str(year);

  # get the description or set it to empty string
  if args.desc:
    desc = args.desc.strip()
  else:
    desc = ''

  # check the daily flag
  if args.daily:
    daily = 1
  else:
    daily = 0

  # check the focus flag
  if args.focus:
    focus = 1
  else:
    focus = 0

  # check the remind is there or set it to empty string
  if args.remind:

    try:
      hour, minute, meridian = tuple(args.remind.strip().split(':',3))

      # check the meridian
      try:
        # check if it is valid or not
        if meridian.lower() == 'am' or meridian.lower() == 'pm':
          meridian = meridian.lower()
        else:
          raise Exception("RemindTimeError : Please choose either am or pm")
      except Exception as e:
        error_count = error_count + 1
        errors.append(e.args[0])

      # check the hour
      try:
        # first check if it a number or not
        try:
          hour = int(hour)
        except ValueError:
          raise Exception("RemindTimeError : Invalid hour")
        # check if this is a valid hour or not
        if(hour < 1 or hour > 12):
          raise Exception("RemindTimeError : Hour value not possible")
      except Exception as e:
        error_count = error_count + 1
        errors.append(e.args[0])

      # check for minute
      try:
      # first check if it a number or not
        try:
          minute = int(minute)
        except ValueError:
          raise Exception("RemindTimeError : Invalid minute")
        if minute < 0 or minute > 59:
          raise Exception("RemindTimeError : Hour value not possible")
      except Exception as e:
        error_count = error_count + 1
        errors.append(e.args[0])

    except ValueError:
      error_count = error_count + 1
      errors.append(e.args[0])

    except Exception as e:
      error_count = error_count + 1
      errors.append(e.args[0])

    # set up string remind from the above
    remind = args.remind

  else:
    remind = ''

  # if there where errors print them and return
  if error_count > 0:
    for err in errors:
      print(err)
    return

  # fortunately there were no errors, write into the db
  try:
    cursor.execute("INSERT INTO todo('title', 'desc', 'date', 'remind', 'daily', 'focus') values (?,?,?,?,?,?)", (title, desc, date, remind, daily, focus));
  except Exception as e:
    print(e.args[0])


  # commit and close the connection
  conn.commit()
  conn.close()

#-------------------------------------------------------------------------


#-------------------------------------------------------------------------
# delete a todo from list
def done(args):

  # get the global connection
  conn = sqlite3.connect('todo.db')

  # get a cursor to database
  cursor = conn.cursor()

  # handling the errors
  error_count = 0
  errors = []

  # get the id, if nothing is passed then it must be zero
  try:
    id = int(args.id)
  except ValueError as e:
    error_count = error_count + 1
    errors.append('IdError : Not a valid id format, must be an integer')

  # if there where errors print them and return
  if error_count > 0:
    for err in errors:
      print(err)
    return

  # we got the id check what to do, if the id is zero then print a list of ids and tasks
  if id == 0:
    list(args)
    return
  else:
    # remove the todo
    try:
      cursor.execute("DELETE FROM todo WHERE id = %d"%(id))
    except Exception as e:
      print(e.args[0])
    # check if something was removed
    if cursor.rowcount > 0:
      print("The to do was removed");
    else:
      print("No such todo was found");

  # commit and close the connection
  conn.commit()
  conn.close()

#--------------------------------------------------------------------------
# Edit a todo
def edit(args):

  # get the global connection
  conn = sqlite3.connect('todo.db')

  # get a cursor to database
  cursor = conn.cursor()

  # handling the errors
  error_count = 0
  errors = []

  # get the id, if nothing is passed then it must be zero
  try:
    # try and convert it to an integer
    id = int(args.id)

    # if the id is not provided print a list
    if id == 0:
      list(args)
      return
    else:

      # get the info about the todo from database
      try:
        cursor.execute("SELECT * FROM todo WHERE id = %d"%(id))
      except Exception as e:
        print(e.args[0])

      # check if there was any result, that is any todo corressponding to the id given
      rows = cursor.fetchall()
      count = len(rows)
      if count < 1:
        print("There not such todo with the given id")
        return
      else:

        # get the current values
        id, date, title, desc, remind, focus, daily  = rows[0]

        # mapping months to the number of days in the months
        month_to_day = [None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        # check the date, if not available set it to todays date
        # first of all get todays date
        today_day, today_month, today_year = int(time.strftime('%d')), int(time.strftime('%m')), int(time.strftime('%Y'))
        # alidate the day passed if it is passed
        if(args.date):

          try:
            day, month, year = tuple(args.date.strip().split('-',3))
            # check the year

            try:
              # first check if it a number or not
              try:
                year = int(year)
              except ValueError:
                raise Exception("DateError : Year is invalid")
              # check if the year has passed
              if(year < today_year):
                raise Exception("DateError : Year has already passed")
              # change the day_to_month map if the year is a leap year, set feb to 29 days
              if(year%4 == 0 and year%400 != 0):
                month_to_day[2] = 29;
            except Exception as e:
              error_count = error_count + 1
              errors.append(e.args[0])

            # check the month
            try:
              # first check if it a number or not
              try:
                month = int(month)
              except ValueError:
                raise Exception("DateError : Month is invalid")
              # check if this is a valid month or not
              if(month < 1 or month > 12):
                raise Exception("DateError : Month month in not possible")
              # check if the month has passed
              if(year == today_year and month < today_month):
                raise Exception("DateError : For this year, this month had already passed")
            except Exception as e:
              error_count = error_count + 1
              errors.append(e.args[0])

            # check the day
            try:
              # first check if it a number or not
              try:
                day = int(day)
              except ValueError:
                raise Exception("DateError : Day is invalid")
              # check if this is a valid month or not
              if(not(month < 1 or month > 12) and (day < 1 or day > month_to_day[month])):
                raise Exception("DateError : Day is not possible in this month")
              # check if the day has passed
              if(year == today_year and month == today_month and day < today_day):
                raise Exception("DateError : For this month and year, the day has already passed")
            except Exception as e:
              error_count = error_count + 1
              errors.append(e.args[0])

          except ValueError:
            error_count = error_count + 1
            errors.append(e.args[0])

          except Exception as e:
            error_count = error_count + 1
            errors.append(e.args[0])

          # form the solid date
          date = str(day) + '-' + str(month) + '-' + str(year);
        else:
          # do nothing keep the original one
          pass



        # get the description or set it to empty string
        if args.desc:
          desc = args.desc.strip()
        else:
          # do nothing keep the original one
          pass

        # check the daily flag
        if args.daily:
          daily = 1 - daily
        else:
          # do nothing keep the original one
          pass

        # check the focus flag
        if args.focus:
          focus = 1 - focus
        else:
          # do nothing keep the original one
          pass

        # check the remind is there or set it to empty string
        if args.remind:

          try:
            hour, minute, meridian = tuple(args.remind.strip().split(':',3))

            # check the meridian
            try:
              # check if it is valid or not
              if meridian.lower() == 'am' or meridian.lower() == 'pm':
                meridian = meridian.lower()
              else:
                raise Exception("RemindTimeError : Please choose either am or pm")
            except Exception as e:
              error_count = error_count + 1
              errors.append(e.args[0])

            # check the hour
            try:
              # first check if it a number or not
              try:
                hour = int(hour)
              except ValueError:
                raise Exception("RemindTimeError : Invalid hour")
              # check if this is a valid hour or not
              if(hour < 1 or hour > 12):
                raise Exception("RemindTimeError : Hour value not possible")
            except Exception as e:
              error_count = error_count + 1
              errors.append(e.args[0])

            # check for minute
            try:
            # first check if it a number or not
              try:
                minute = int(minute)
              except ValueError:
                raise Exception("RemindTimeError : Invalid minute")
              if minute < 0 or minute > 59:
                raise Exception("RemindTimeError : Hour value not possible")
            except Exception as e:
              error_count = error_count + 1
              errors.append(e.args[0])

          except ValueError:
            error_count = error_count + 1
            errors.append(e.args[0])

          except Exception as e:
            error_count = error_count + 1
            errors.append(e.args[0])

          # set up string remind from the above
          remind = args.remind

        else:
          # do nothing keep the original one
          pass

        # if there where errors print them and return
        if error_count > 0:
          for err in errors:
            print(err)
          return

        # everything is alright, update the database
        try:
          cursor.execute("UPDATE todo set 'title' = ? , 'desc' = ?, 'date' = ?, 'remind' = ?, 'daily' = ?, 'focus' = ? where id = %d"%(id),
                          (title, desc, date, remind, daily, focus));
          if(cursor.rowcount > 0):
            print("The todo is updated")
          else:
            print("No such todo found")
        except Exception as e:
          print(e.args[0])
          return

  except ValueError as e:
    error_count = error_count + 1
    errors.append('IdError : Not a valid id format, must be an integer')


  # commit and close
  conn.commit()



#--------------------------------------------------------------------------

# get subparsers manager
subparsers = parser.add_subparsers(help='Choose what you want to do')

# the argument to initailize the database
init_parser = subparsers.add_parser('init', help = 'initailize the todo list, use it only once when using for the first time, this will delete any data present before');
init_parser.set_defaults(func=init)

# the argument to list the todo in the database according to id
list_parser = subparsers.add_parser('list', help = 'list the todos');
list_parser.set_defaults(func=list)

# the group of agruments that help add a todo
new_parser = subparsers.add_parser('add', help = 'add a todo, use "add -h" to see more help for this command')
new_parser.add_argument('title', help='new todo title, plese put it inside quote, if not other option is given the a todo for today will be added')
new_parser.add_argument('-D', '--date', help='add a deadline date to the todo, format is "day-month-year"')
new_parser.add_argument('-d', '--desc', help='description to add, please use ; to seperate lines, use with --desc/-d option')
new_parser.add_argument('--daily', help='when used with a todo, makes it appear daily of he list till the deadline', action='store_true')
new_parser.add_argument('--focus', help='when used with a todo, makes it the priority no matter what the deadline is, appers on the top of list', action='store_true')
new_parser.add_argument('--remind', help='adds a remainder and shows notificaton if possible and make it the focus, if daily flag is set will show notification daily, time format is "hour:minute am/pm" ')
new_parser.set_defaults(func=add)

# the group of argumnets that help delete the todo
done_parser = subparsers.add_parser('done', help = 'removes a todo, use "done -h" to see more help for this command')
done_parser.add_argument('id', help='deletes a todo by id, if the id is not specified then prints a list with id to help choose', nargs = '?',  default = '0')
done_parser.set_defaults(func=done)

# edit group
edit_parser = subparsers.add_parser('edit', help = 'removes a todo, use "edit -h" to see more help for this command')
edit_parser.add_argument('id', help='deletes a todo by id, if the id is not specified then prints a list with id to help choose', nargs = '?',  default = '0')
edit_parser.add_argument('-D', '--date', help='sets a deadline date to the todo, format is "day-month-year"')
edit_parser.add_argument('-d', '--desc', help='description to set, please use ; to seperate lines, use with --desc/-d option')
edit_parser.add_argument('-t', '--time', help='sets a deadline time to the todo, format is "hour:minute am/pm"')
edit_parser.add_argument('--daily', help='sets whether the todo will appear on the list daily, giving this will revese the current setting', action='store_true')
edit_parser.add_argument('--focus', help='sets whether the todo will be the attention, giving this will revese the current setting', action='store_true')
edit_parser.add_argument('--remind', help='sets a remainder and shows notificaton if possible and make it the focus, if daily flag is set will show notification daily, time format is "hour:minute am/pm" ')
edit_parser.set_defaults(func=edit)

# update group
update_parser = subparsers.add_parser('update', 'updates the text file for lua')
update_parser.set_defaults(func=update)

# parse the arguments and call the function according the sub command
args = parser.parse_args()
args.func(args)


