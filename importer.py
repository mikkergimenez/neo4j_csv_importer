#!/usr/bin/python
#
# Example use:
#
# ./importer.py state_capitals.csv city:capital_of "state,abbreviation,size,size_units,dst" 
# 
# Syntax:
#
# ./importer.py <File> <relationship_columns> "<property_columns>"
#
# relationship_columns and property columns are comma separated lists.
# 
# the relationship_columns will create a new node for each column in the relationship, 
# and relate it to the node created by the line.
#
# The relationship_column entry is a colon seperated list of entries:
# {column_name}:{relationship_name}:{direction_of_relationship}:{whether_to_create a node}
# 
#   column_name: name of csv column
#   relationship_name: name of relationship to create
#   direction_of_relationship 'f' or 'r' forward: this -> parent 'r' parent -> this
#   whether_to_create_a_node: if this column relates this node to other nodes in the list, put 0 here
# 
# This is somewhat custom to my purposes but I will continue to generesize it.
#
# all this script does is print the cypher to the screen, so there there should be no danger in using it.


import csv
from StringIO import StringIO
import sys
from pyparsing import (printables, originalTextFor, OneOrMore, quotedString, Word, delimitedList)


DELIMITER = ';'

rel_objs = []
rel_names = {}
relationships = sys.argv[2].split(',')
for i, relationship in enumerate(relationships):
    split_rel = relationship.split(':')
    rel_objs.append(split_rel[0])
    rel_names[split_rel[0]] = dict()
    rel_names[split_rel[0]]['text'] = split_rel[1]
    try:
        rel_names[split_rel[0]]['direction'] = split_rel[2]
    except:
        rel_names[split_rel[0]]['direction'] = 'f'
    try:
        rel_names[split_rel[0]]['create'] = split_rel[3]
    except:
        rel_names[split_rel[0]]['create'] = 1


property_fields = sys.argv[3].split(',')

f = open(sys.argv[1], "r")

liane = f.readline()

titles = line.split(DELIMITER)

titles[len(titles) - 1] = titles[len(titles) - 1].rstrip()

for i, title in enumerate(titles):
    if titles[i].startswith('"') and titles[i].endswith('"'):
        titles[i] = titles[i][1:-1]


def capify(string):
    return string.upper().replace(" ", "").replace("'", "").replace("-", "").replace(".", "")


def create_relationship(one, rel, two, dir, name):
    query = "MATCH (a), (b) "
    query += "WHERE a."
    if name == 'borders':
        query += "acronym"
    else:
        query += "name"
    query += " = '" + one + "' AND b.acronym = '" + two + "' "
    if dir == 'r':
        query += "CREATE (b)-[r:" + capify(rel) + "]->(a) "
    else:
        query += "CREATE (a)-[r:" + capify(rel) + "]->(b) "
    query += "RETURN r;"
    return query


def do_rel_objs(rel_names, elements):
    if rel_names[titles[i]]['create'] == 1:
        rel_items.append('MERGE (' + capify(elements[i]) + ':' + titles[i] + ' { name: "' + elements[i] + '" });')
    if ',' in elements[i]:
        
        the_elements = elements[i].split(',')
        for element in the_elements:
            # create multiple relationships if applicable
            rel_links.append(create_relationship(element, rel_names[titles[i]]['text'], elements[4], rel_names[titles[i]]['direction'], titles[i]))
            # rel_links.append('CREATE (' + element) + ')-[:' + rel_names[titles[i]]['text']) + ']->(' + elements[5] + ');')    
    else:
        rel_links.append(create_relationship(elements[i], rel_names[titles[i]]['text'], elements[4], rel_names[titles[i]]['direction'], titles[i]))


def do_primary(i, element, titles, property_fields):
    return_val = ''
    if titles[i] in property_fields:
        if titles[i] == 'name':
            if ',' in elements[i]:
                the_names = elements[i].split(',')
                return_val += 'name: "' + the_names[0] + '", '
                for j, name in enumerate(the_names):
                    if j == 1:
                        return_val += 'aka: "' + the_names[j]
                    if j > 1:
                        return_val += ';' + the_names[j]
                return_val += '", '
        else:
            if ',' in elements[i]:
                elements[i] = elements[i].replace(",",";")
            return_val += titles[i] + ': "' + elements[i] + '", '
    return return_val


rel_items = []
rel_links = []

line_x = 0
while line:
    this_line = ''
    data = StringIO(line)
    reader = csv.reader(data, delimiter=DELIMITER)
    for row in reader:
        elements = row
    this_line = 'CREATE (' + elements[4] + ':' + 'country' + ' { ' #name: "' + elements[0].title() + '", '
    for i, element in enumerate(elements):
        this_line += do_primary(i, element, titles, property_fields)
        if titles[i] in rel_objs:
	        do_rel_objs(rel_names, elements)

    this_line = this_line[:-2]
    this_line += ' });'
    
    if line_x > 0:
        print this_line    
    line_x+=1

    line = f.readline()

rel_items = list(set(rel_items))
for item in rel_items:
    print item
rel_links = list(set(rel_links))
for link in rel_links:
    print link

