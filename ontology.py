"""A module for building ontologies and viewing the relations defined within them.

Author: Stephen Kaplan
Last Modified: July 2022
"""

import pickle
import os
import json
from pprint import pprint

triples = {}
pending_removals = False

inheritance_relations = {}

def sort_subject(triple):
	return triple.split(" ")[1]

def init_sol():
	"""Load relations and rules
	"""
	table_title("Loading Rules and Relations")
	for filename in os.listdir(os.getcwd() + "/Relations"):
		with open(os.path.join(os.getcwd() + "/Relations", filename), 'r') as rfile:
			json_data = json.load(rfile)
			for relation, data in json_data["relations"].items():
				for index in range(0, len(data["rules"])):
					data["rules"][index] = eval(data["rules"][index])
			inheritance_relations.update(json_data["relations"])
			print("Loaded", filename, "-", json_data["name"], "- v" + str(json_data["version"]))

def reset():
	global triples
	triples = {}
	print("Cleared all entries.")

def import_datafile(filepath):
	# Load additional dict files, append to dict
	global triples
	filepath = filepath.replace("\ ", " ").strip()
	try:
		with open(filepath, "rb") as dict_file:
			new_triples = pickle.load(dict_file)

			triples_to_add = {}
			for k,v in new_triples.items():
				pos = max(k, len(triples)+len(triples_to_add))
				if [v[0], v[1], v[2]] not in triples.values():
					triples_to_add[pos] = v

			triples.update(triples_to_add)
	except FileNotFoundError:
		print("Error: Could not locate the target datafile.")

def load(target):
	# Import entire dict file, replace dict
	global triples
	try:
		with open(target, "rb") as dict_file:
			triples = pickle.load(dict_file)
	except FileNotFoundError:
		print("Error: Could not locate the target datafile.")

def learn(target):
	global triples
	new_triples = {}
	found = False
	for filename in os.listdir(os.path.join(os.getcwd(), "Libraries")):
		if ".py" not in filename and filename is not ".DS_Store":
			with open(os.path.join(os.getcwd(), "Libraries", filename), 'rb') as datafile:
				new_triples = pickle.load(datafile)
				for key, value in new_triples.items():
					if target in value:
						print("Found definition in %s." % os.path.join(os.getcwd(), "Libraries", filename))
						found = True
						triples_to_add = {}
						for k,v in new_triples.items():
							pos = max(k, len(triples)+len(triples_to_add))
							if [v[0], v[1], v[2]] not in triples.values():
								triples_to_add[pos] = v

						triples.update(triples_to_add)
						print("Added %d triples:" % len(triples_to_add))
						pprint(triples_to_add)
						print()
						break
	return found
			
			
def export():
	global triples
	print("-" * 20)
	print(triples)

	print("Do you want to export to file? (y/n)")
	decision = input()

	if decision in ["Y", "y", "Yes", "yes"]:
		print("Input a file name (blank = 'triples')")
		filename = input()
		if filename == "":
			filename = "triples"
		with open("/Libraries/"+filename+".dictionary", "wb") as dict_file:
			pickle.dump(triples, dict_file)
		print("Exported to file: " + os.getcwd() + "/Libraries/"+filename+".dictionary")
	else:
		print("Not exported to file.")

def add_triple(subject, predicate, object):
	global triples
	existing_id = lookup(subject, predicate, object)
	if existing_id == -1:
		new_id = len(triples)
		triples[new_id] = [subject, predicate, object]
		return new_id
	else:
		return existing_id

def lookup(subject, predicate, object):
	for key, value in triples.items():
		if value[0].lower() == subject.lower():
			if value[1].lower() == predicate.lower():
				if value[2].lower() == object.lower():
					return key
	return -1

def get_triples(target):
	global triples
	target_triples = []
	parts = target.split(" ")
	for key, value in triples.items():
		if len(parts) == 1:
			if value[0].lower() == target.lower():	# Check subject
				target_triples.append(str(key) + ": " + " ".join(triples[key]))
			elif value[1].lower() == target.lower():	# Check predicate
				target_triples.append(str(key) + ": " + " ".join(triples[key]))
			elif value[2].lower() == target.lower(): # Check object
				target_triples.append(str(key) + ": " + " ".join(triples[key]))
		elif value[0].lower() == parts[0].lower() and value[1].lower() == parts[1].lower():
			# Check subject and predicate
			target_triples.append(str(key) + ": " + " ".join(triples[key]))
		elif value[1].lower() == parts[0].lower() and value[2].lower() == parts[1].lower():
			# Check predicate and object
			target_triples.append(str(key) + ": " + " ".join(triples[key]))
		elif value[1].lower() == target.lower():
			# Check complex predicate
			target_triples.append(str(key) + ": " + " ".join(triples[key]))
		elif value[0].lower()+" "+value[1].lower() == target.lower():
			# Check subject and complex predicate
			target_triples.append(str(key) + ": " + " ".join(triples[key]))
		elif value[1].lower()+" "+value[2].lower() == target.lower():
			# Check complex predicate and object
			target_triples.append(str(key) + ": " + " ".join(triples[key]))

	if len(target_triples) == 0:
		print("No entries found. Attempt to learn from external files? (y/n)")
		decision = input()
		if decision in ["Y", "y", "Yes", "yes"]:
			if learn(target):
				target_triples = get_triples(target)
			else:
				print("No external entries found.")
	return target_triples

def get_deep_triples(target, level=0):
	global triples
	all_triples = []
	targets = []

	targets.append(target);
	
	# Get variations of target
	for key, value in triples.items():
		# 	# Just simple targets for now (not multiple words)
		if level == 0:
			if value[0].lower() == target.lower():
				# Target is something, add something as synonym
				if value[2] not in targets:
					targets.append(value[2])
			elif value[2].lower() == target.lower():
				# Something is target, add something as synonym
				if value[0] not in targets:
					targets.append(value[0])
		else:
			if value[1] == "is same as" and value[0].lower() == target.lower():
				# Target is something, add something as synonym
				if value[2] not in targets:
					targets.append(value[2])
			elif value[1] == "is same as" and value[2].lower() == target.lower():
				# Something is target, add something as synonym
				if value[0] not in targets:
					targets.append(value[0])

	for new_target in targets:
		all_triples.extend(triple for triple in get_triples(new_target) if triple not in all_triples)

	return all_triples

def build_inferences():
	global triples
	inferences_remaining = True
	added = False
	while inferences_remaining:
		inferences_remaining = False
		for key, value in list(triples.items()):
			new_triples = []
			for relation, data in inheritance_relations.items():
				subject = value[0]
				predicate = value[1]
				object = value[2]
					
				# Add ruled inferences
				for rule in data["rules"]:
					result = rule(subject, predicate, object)
					if result != None:
						for new_triple in result:
							new_triples.append([new_triple[0], new_triple[1], new_triple[2]])

					result = rule(object, predicate, subject)
					if result != None:
						for new_triple in result:
							new_triples.append([new_triple[0], new_triple[1], new_triple[2]])

				if value[1].lower() == relation:
					subject1 = value[0]
					subject2 = value[2]

					# Add implied inferences
					for implied_relation in data["implies"]:
						new_triples.append([subject1, implied_relation, subject2])

					for implied_relation in data["implies-inverse"]:
						new_triples.append([subject2, implied_relation, subject1])

					# Add synonymic inferences
					for key2, value2 in list(triples.items()):
						if value2[1].lower() in data["inherits"]:
							if value2[0] == subject2 and subject1 != value2[2]:
								new_triples.append([subject1, value2[1], value2[2]])

				if value[1].lower() == "is same as":
					subject1 = value[0]
					subject2 = value[2]
					for key2, value2 in list(triples.items()):
						if value2[0] == subject1 and subject2 != value2[2]:
							new_triples.append([subject2, value2[1], value2[2]])
						if value2[0] == subject2 and subject1 != value2[2]:
							new_triples.append([subject1, value2[1], value2[2]])
						if value2[2] == subject1 and subject2 != value2[0]:
							new_triples.append([value2[0], value2[1], subject2])
						if value2[2] == subject2 and subject1 != value2[0]:
							new_triples.append([value2[0], value2[1], subject1])
						
			for new_triple in new_triples:
				if new_triple not in triples.values() and len(new_triple) > 0:
					new_id = add_triple(new_triple[0], new_triple[1], new_triple[2])
					print("Added Triple #%d: %s" % (new_id, " : ".join(new_triple)))
					inferences_remaining = True
					added = True
	return added
				

def check_triple(subject, predicate, object):
	triple = " ".join([subject, predicate, object])
	all_triples = " ".join(get_deep_triples(subject))
	if triple in all_triples:
		print("True")
	else:
		print("False")

def clean():
	global triples
	new_key = 0
	cleaned_triples = {}
	for key, value in triples.items():
		if value[0] != "None":
			cleaned_triples[new_key] = value
			new_key = new_key + 1
	triples = cleaned_triples

def prompt_for_input(carry):
	"""Prompts users with the first value in carry, if defined, or -> otherwise.
	"""
	if len(carry) < 1:
		print("\n->", end="")
	else:
		print(carry[0], end="")

	input_str = input()
	return input_str

def table_title(title):
	print("-" * (len(title)+2))
	print(" " + title + " ")
	print("-" * (len(title)+2))

def parse_input(input_str):
	intent = []
	input_arr = input_str.split(" ")

	if input_str.lower() in ["quit", "bye", "exit"]:
		intent.append(-1) # Exit
	elif input_str.lower() in ["reset"]:
		intent.append(-2)
	elif input_arr[0].lower() in ["learn"]:
		intent.append(-3)
		intent.append(input_arr[1])
	elif input_str.lower() in ["list", "ls", "show all"]:
		table_title("List of All Triples")
		intent.append(-4)
	elif input_str.lower() in ["clean"]:
		print("Clearing null entries...")
		intent.append(-5)
	elif input_arr[0].lower() in ["add", "insert"]:
		subject = input_arr[1]
		predicate = " ".join(input_arr[2:-1])
		object = input_arr[-1]
		if "," not in object:
			intent.append(1) # Add
			intent.append(subject)
			intent.append(predicate)
			intent.append(object)
		else:
			# Multiple objects
			objects = object.split(",")
			for sub_object in objects[0:-1]:
				new_id = add_triple(subject, predicate, sub_object)
				print("Added Triple #%d: %s" % (new_id, " : ".join([subject, predicate, sub_object])))
			intent.append(1) # Add
			intent.append(subject)
			intent.append(predicate)
			intent.append(objects[-1])
	elif input_arr[0].lower() in ["remove", "delete", "del", "rem", "rm"]:
		intent.append(2)	# Remove
		intent.append(int(input_arr[1]))	# Triple ID
	elif input_arr[0].lower() in ["export"]:
		intent.append(3)
	elif input_arr[0].lower() in ["import"]:
		intent.append(4)
		intent.append(" ".join(input_arr[1:]))
	elif input_arr[0].lower() in ["all"]:
		table_title("Triples Describing Concept of %s" % input_arr[1].title())
		target_triples = get_deep_triples(input_arr[1])
		intent.append(5)	# Deep Find
		target_triples.sort(key=sort_subject)
		intent.append("\n".join(target_triples))
	elif input_str.lower()[-1] == "?":
		intent.append(6)	# Query
		subject = input_arr[0]
		predicate = " ".join(input_arr[1:-1])
		object = input_arr[-1][:-1]
		intent.append(subject)
		intent.append(predicate)
		intent.append(object)
	elif input_str.lower() in ["infer"]:
		table_title("Inferred Triples")
		intent.append(7)
	elif input_arr[0].lower() in ["load"]:
		intent.append(8)
		intent.append(input_arr[1])
	elif input_arr[0].lower() in ["more"]:
		table_title("Triples Containing %s and Synonyms" % input_arr[1].title())
		target_triples = get_deep_triples(input_arr[1], 1)
		intent.append(9)	# Mid-deep Find
		target_triples.sort(key=sort_subject)
		intent.append("\n".join(target_triples))
	else:
		table_title("Triples Containing %s" % input_str.title())
		target_triples = get_triples(input_str)
		intent.append(10)	# Find
		target_triples.sort(key=sort_subject)
		intent.append("\n".join(target_triples))

	return intent

def run_intent(intent):
	global triples
	global pending_removals

	carry = []

	intent_cmd = intent[0]

	if intent_cmd == -1:	# Exit
		print("Bye!")
		return (None, False)
	elif intent_cmd == -2: # Reset
		reset()
	elif intent_cmd == -3: # Learn
		learn(intent[1])
	elif intent_cmd == -4: # List
		pprint(triples)
	elif intent_cmd == -5: # Clean
		clean()
	elif intent_cmd == 1:	# Add
		new_id = add_triple(intent[1], intent[2], intent[3])
		print("Added Triple #%d: %s" % (new_id, " : ".join(intent[1:])))
	elif intent_cmd == 2: # Remove
		id = intent[1]
		removed = triples[id]
		triples[id] = ["None", "None", "None"]
		print("Removed Triple #%d: %s" % (id, " : ".join(removed)))
		pending_removals = True
	elif intent_cmd == 3: # Export
		export()
	elif intent_cmd == 4: # Import
		import_datafile(intent[1])
	elif intent_cmd == 6: # Query
		check_triple(intent[1], intent[2], intent[3])
	elif intent_cmd == 7: # Infer
		if not build_inferences():
			print("None")
	elif intent_cmd == 8: # Load
		load(intent[1])
	elif intent_cmd == 5 or intent_cmd == 9 or intent_cmd == 10: # Find
		print(intent[1])

	return (carry, True)

def main():
	global pending_removals
	again = True
	carry = []
	counter = 0

	while (again):
		input_str = prompt_for_input(carry)
		intent = parse_input(input_str)
		(carry, again) = run_intent(intent)
		if counter % 10 == 0 and pending_removals == True:
			print("Autocleaning...")
			clean()
			pending_removals = False
		else:
			counter = counter + 1

init_sol()
main()