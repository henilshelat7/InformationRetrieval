import json
import pprint
 
f = open('sample.json','r')
    
data = json.load(f)
new_dict = {}
for k,v in data.items():
    k = k.replace("\n", "").strip()
    new_dict[k] = v
    
with open("sample2.json", "w") as write_file:
    json.dump(new_dict, write_file, indent=4)