import shutil
import os

def read_config_file(filePath):
	config = {}
	with open(filePath) as file:
		for line in file:
			if not line.strip() is "":
				key = line.split("=")[0].strip()
				value = line.split("=")[1].strip()
				config[key] = value
	return config

def move_file(src, dst):
	shutil.move(src, dst)
	
def delete_file(path):
	os.remove(path)
	
def save_db(dbPath, key, value):
	if not os.path.exists(dbPath):
		file = open(dbPath, "w+")
		file.write("")
		file.truncate()
		file.close()
		
	file = open(dbPath, "r+")
	all_db = file.readlines()
	file.seek(0)
	for line in all_db:
		if not line.startswith(key + "="):
			file.write(line)
	file.write(key + "=" + value + "\n")
	file.truncate()
	file.close()
	
def read_db(dbPath):
	db = {}
	if os.path.exists(dbPath):
		with open(dbPath) as file:
			for line in file:
				if not line.strip() == "":
					keyAndValue = line.split("=")
					allKey = keyAndValue[0].strip()
					value = keyAndValue[1].strip()
					keys = allKey.split(".")[:-1]
					bottomTable = None
					for subkey in keys:
						if bottomTable is None:
							db[subkey] = {}
							bottomTable = db[subkey]
						else:
							bottomTable[subkey] = {}
							bottomTable = bottomTable[subkey]
						print(db)
					bottomTable[allKey.split(".")[-1]] = value
					print(db)
	return db
	