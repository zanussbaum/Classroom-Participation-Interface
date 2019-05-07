import json

def read_json(file):
    with open("course-dump.json", 'r') as json_file:
        array = json.load(json_file)

    print(array)



if __name__ == '__main__':
    read_json("course-dump.json")