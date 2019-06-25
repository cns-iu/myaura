# coding: utf-8
# Author: Nathan D Ratkiewicz
# Created: 05 September 2016
# Updated: 25 June 2019 (by Rion B Correia)
#
# Description:
# Preprocess the text on the DB
#
import time
import os
from sets import Set
import db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
import pandas as pd
import csv

tableNames = ['source', 'role', 'city', 'state', 'region', 'category', 'subcategory']
tableDicts = {}
chunkSize = 5000
numTotalRowsDict = {0: 2583241058, 1: 530624248, 2: 642567580, 3: 501659474}
numTotalRows = 1933175410
failures = Set()


def getTableIndex(table, name):
    try:
        index = tableDicts[table][str(name).lower()]
    except exc.SQLAlchemyError:
        failures.add(name)
        index = None
    return index


def populateTables(session):
    print("Building reference tables")
    for table in tableNames:
        tableDicts[table] = {}
        query = """INSERT INTO {}({}, {}) VALUES(%s, %s)""".format(table, table + '_id', table + '_name')
        values = []
        pathToRead = os.getcwd() + '//csv//' + table + '.csv'
        dfTable = pd.read_csv(pathToRead, header=None, names=[table], usecols=[0])
        for index, row in dfTable.iterrows():
            tableDicts[table][str(row[table]).lower()] = int(index)
            values.append((int(index), row[table]))
        session.executemany(query, values)
        session.commit()
    print('Done building reference tables')


def getGenderNum(gender):
    if(gender == 'M'):
        return 1
    elif(gender == 'F'):
        return 2
    else:
        return None


def getAreaCode(areaCode):
    if(not(str(areaCode).isdigit())):
        return None

    return areaCode


def getAge(age):
    if(pd.isnull(age) or age < 0):
        return None

    return int(age)


def getZipCode(zipCode):
    if(zipCode == '--US Unknown--'):
        return None

    return zipCode


def createDatabase(session):
    """ Loads a .sql file containing the create table scripts"""
    fd = open('create_database.sql', 'r')
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sqlCommands = sqlFile.split(';')
    print("Executing creation commands")
    # Execute every command from the input file
    for command in sqlCommands:
        # This will skip and report errors
        # For example, if the tables do not yet exist, this will skip over
        # the DROP TABLE commands
        try:
            session.execute(command)
        except exc.StatementError as err:
            print("Something went wrong `{}`".format(err))
    print("Database creation complete")


def dropTables(session):
    tableNames = ['source', 'role', 'city', 'state', 'region', 'category', 'subcategory', 'person', 'message']

    for table in tableNames:
        print("Dropping table {:s}".format(table))
        try:
            session.execute("DROP TABLE {:s}".format(table))
            session.commit()
        except exc.StatementError as err:
            print("Could not find table `{:s}` : error: {:s}".format(table, err))


def main():

    engine = db.connectToMySQL(server='mysql_chacha')
    Session = sessionmaker(bind=engine)
    session = Session()

    dropTables(session)

    createDatabase(session)

    personMessageCounts = {}

    populateTables(session)

    columnNames = [
        'message_id', 'date', 'category', 'subcategory',
        'source', 'role', 'city', 'state', 'region',
        'area_code', 'zip_code', 'gender', 'age',
        'perso[n_id', 'raw_query_text'
    ]

    filePath = '/l/casci/chacha/data/'
    files = ['iuson_output_09.tsv', 'iuson_output_10.tsv', 'iuson_output_11.tsv', 'iuson_output_12.tsv']

    currentFileNum = 0

    add_person = """INSERT INTO person (person_id, age_first_seen, gender, city, region, state, zip_code, area_code, post_count, date_first_seen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    add_message = """INSERT INTO message (message_id, person_id, category_id, subcategory_id, role_id, source_id, message_text, message_date, message_length) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    while not(currentFileNum == 4):
        startTime = time.clock()
        fileName = filePath + files[currentFileNum]
        print('Beginning processing on %s' % fileName)
        reader = pd.read_csv(fileName, sep='\t', quotechar='\x07', header=None, names=columnNames,
                             chunksize=chunkSize, usecols=[0, 1, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16],
                             dtype={'message_id': pd.np.int64, 'date': str, 'category': str, 'subcategory': str,
                                    'source': str, 'role': str, 'city': str, 'state': str,
                                    'region': str, 'gender': str, 'person_id': pd.np.int64, 'raw_query_text': str
                                    }
                             )

        chunkFraction = numTotalRowsDict[currentFileNum] / chunkSize
        chunkNum = 0
        person_data = []
        messageData = []
        for chunk in reader:
            chunkStartTime = time.clock()
            newPeople = Set()
            chunkNum += 1
            for index, row in chunk.iterrows():
                    message = str(row['raw_query_text'])
                    messageLength = len(message)
                    if(messageLength > 2 and (not message == 'nan')):
                        person_Id = row['person_id']
                        if(person_Id in newPeople or person_Id in personMessageCounts):
                            personMessageCounts[person_Id] += 1
                        else:
                            person_city_Id = getTableIndex('city', row['city'])
                            person_state_Id = getTableIndex('state', row['state'])
                            person_region_id = getTableIndex('region', row['region'])
                            person_gender = getGenderNum(row['gender'])
                            person_area_code = getAreaCode(row['area_code'])
                            person_age_first_seen = getAge(row['age'])
                            person_zip_code = getZipCode(row['zip_code'])
                            person_first_seen = row['date']

                            person_data.append((person_Id, person_age_first_seen, person_gender, person_city_Id, person_region_id,
                                                person_state_Id, person_zip_code, person_area_code, None, person_first_seen))
                            personMessageCounts[person_Id] = 1
                            newPeople.add(person_Id)

                        messageId = row['message_id']
                        messageDate = row['date']
                        categoryId = getTableIndex('category', row['category'])
                        subcategoryId = getTableIndex('subcategory', row['subcategory'])
                        sourceId = getTableIndex('source', row['source'])
                        roleId = getTableIndex('role', row['role'])
                        messageData.append((messageId, person_Id, categoryId, subcategoryId, roleId, sourceId, message, messageDate, messageLength))

            if (len(person_data) > 50000):
                insertStartTime = time.clock()
                session.executemany(add_person, person_data)
                session.commit()
                print("Inserting {0} Person records took {1:.2f} seconds".format(len(person_data), time.clock() - insertStartTime))
                person_data = []

            if (len(messageData) > 50000):
                insertStartTime = time.clock()
                session.executemany(add_message, messageData)
                session.commit()
                print("Inserting {0} Message records took {1:.2f} seconds".format(len(messageData), time.clock() - insertStartTime))
                messageData = []

            print("{0} Chunk #{1}/{2} took {3:.2f} seconds".format(files[currentFileNum], chunkNum, chunkFraction, time.clock() - chunkStartTime))

        if (len(person_data) > 0):
            insertStartTime = time.clock()
            session.executemany(add_person, person_data)
            session.commit()
            print("Inserting {0} Person records took {1:.2f} seconds".format(len(person_data), time.clock() - insertStartTime))
            person_data = []

        if (len(messageData) > 0):
            insertStartTime = time.clock()
            session.executemany(add_message, messageData)
            session.commit()
            print("Inserting {0} Message records took {1:.2f} seconds".format(len(messageData), time.clock() - insertStartTime))
            messageData = []

        print(fileName + ' successfully processed.')
        currentFileNum += 1

    finishTime = time.clock()
    totalTime = finishTime - startTime
    wholeSetTime = totalTime / 60 / 60 / 24
    print("It took {} days total".format(wholeSetTime))

    savePersonTime = time.clock()
    print("Saving person counts, just in case...")
    peopleToWrite = len(personMessageCounts)
    i = 1
    with open('personMessageCounts.csv', 'wb') as outfile:
        writer = csv.writer(outfile)
        for key, value in personMessageCounts.items():
            writer.writerow([key, value])
            i += 1
            if(i >= 50000):
                peopleToWrite = peopleToWrite - i
                print("50,000 written to file {} remaining".format(peopleToWrite))
                i = 0

    print("It took {} seconds to save people csv".format(time.clock() - savePersonTime))

    print("Rebuilding database structure")
    rebuildTime = time.clock()

    print('Adding primary Key to Person')
    updateKeys = time.clock()
    session.execute("""ALTER TABLE person ADD PRIMARY KEY(person_id)""")
    session.commit()
    print("It took {} seconds to add the primary key to person".format(time.clock() - updateKeys))

    print("Adding city foreign key to person")
    updateKeys = time.clock()
    session.execute("""ALTER TABLE person ADD FOREIGN KEY (`city`) REFERENCES city(`city_id`);""")
    session.commit()
    print("It took {} seconds to add city foreign key to person".format(time.clock() - updateKeys))

    print("Adding state foreign key to person")
    updateKeys = time.clock()
    session.execute("""ALTER TABLE person ADD FOREIGN KEY (`state`) REFERENCES state(`state_id`);""")
    session.commit()
    print("It took {} seconds to add state foreign key to person".format(time.clock() - updateKeys))

    print("Adding region foreign key to person")
    updateKeys = time.clock()
    session.execute("""ALTER TABLE person ADD FOREIGN KEY (`region`) REFERENCES region(`region_id`);""")
    session.commit()
    print("It took {} seconds to add region foreign key to person".format(time.clock() - updateKeys))

    print('Adding primary Key to message')
    updateKeys = time.clock()
    session.execute("""ALTER TABLE message ADD PRIMARY KEY(message_id)""")
    session.commit()
    print("It took {} seconds to add the primary key to message".format(time.clock() - updateKeys))

    print("Adding person foreign key to message")
    updateKeys = time.clock()
    session.execute("""ALTER TABLE message ADD FOREIGN KEY (`person_id`) REFERENCES person(`person_id`);""")
    session.commit()
    print("It took {} seconds to add person_id foreign key to message".format(time.clock() - updateKeys))

    print("Adding category foreign key to message")
    updateKeys = time.clock()
    session.execute("""ALTER TABLE message ADD FOREIGN KEY (`category_id`) REFERENCES category(`category_id`);""")
    session.commit()
    print("It took {} seconds to add category foreign key to message".format(time.clock() - updateKeys))

    print("Adding subcategory foreign key to message")
    updateKeys = time.clock()
    session.execute("""ALTER TABLE message ADD FOREIGN KEY (`subcategory_id`) REFERENCES subcategory(`subcategory_id`);""")
    session.commit()
    print("It took {} seconds to add subcategory foreign key to message".format(time.clock() - updateKeys))

    print("Adding role foreign key to message")
    updateKeys = time.clock()
    session.execute("""ALTER TABLE message ADD FOREIGN KEY (`role_id`) REFERENCES role(`role_id`);""")
    session.commit()
    print("It took {} seconds to add role foreign key to message".format(time.clock() - updateKeys))

    print("Adding source foreign key to message")
    updateKeys = time.clock()
    session.execute("""ALTER TABLE message ADD FOREIGN KEY (`source_id`) REFERENCES source(`source_id`);""")
    print("It took {} seconds to add source foreign key to message".format(time.clock() - updateKeys))
    session.commit()

    postCountUpdate = time.clock()
    update_person = """UPDATE person SET post_count=%s WHERE person_id=%s"""
    person_update_data = []
    i = 0
    print('Starting post count update')
    lengthUpdates = len(personMessageCounts)
    print(str(lengthUpdates) + ' updates remaining')
    for personId in personMessageCounts:
        count = personMessageCounts[personId]
        if(count > 1):
            person_update_data.append((count, personId))
            i += 1
            if(i >= 20000):
                print("Updating {} records".format(i))
                updateKeys = time.clock()
                session.executemany(update_person, person_update_data)
                session.commit()
                lengthUpdates = lengthUpdates - i
                print("It took {} seconds to update {} posts. {} updates remaining.".format(time.clock() - updateKeys, i, lengthUpdates))
                i = 0

    if(not(i == 0)):
        print("Updating {} records".format(i))
        updateKeys = time.clock()
        session.executemany(update_person, person_update_data)
        session.commit()
        print("It took {} seconds to update {} posts.".format(time.clock() - updateKeys, i))

    print("It took {} seconds to update the post counts".format(time.clock() - postCountUpdate))

    print("It took {} seconds to rebuild the structure".format(time.clock() - rebuildTime))

    print(failures)

    print("That's all folks!")


if __name__ == "__main__":
    main()
