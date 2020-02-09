# var 1 is interface lists
# var 2 is file list
# var 3 is the contract list
import sys
import os

from jinja2 import Environment, FileSystemLoader
file_loader = FileSystemLoader('interfaces')
env = Environment(loader=file_loader)


temp = os.listdir("interfaces")
inputs = []
for i in temp:
  file_parts = i.split(".")
  if len(file_parts) > 1:
    if file_parts[1] == "soc":
         inputs.append(i)
os.system("rm contracts/*")

for i in inputs:
   print("i",i)
   template = env.get_template(i)
   output = template.render()
   
   path = "contracts/"+i
   contract_file = open(path,'w')
   contract_file.write(output)
   contract_file.close()
   
   
compile_inputs = []
for i in inputs:
  compile_inputs.append("contracts/"+i)   
#print(compile_inputs)
str = "  "
output = str.join(compile_inputs)
#print("output",output)
command_line = "solcjs --optimize --bin --abi -o binary_data " +output

print("command_line",command_line)
os.system("rm binary_data/*")
os.system(command_line)

os.chdir("binary_data")
file_list = os.listdir(".")
for i in file_list:
  parts = i.split("_")
  if parts[-2] == "soc":
    
    os.rename(i,parts[-1])
  else:
    
    os.remove(i)
    
    

'''
solcjs --optimize --bin --abi -o temp_output $1 
VAR1=$1
VAR2=$2

cp   ${VAR1}_${VAR2}.abi solc_output/${VAR2}.abi
cp   ${VAR1}_${VAR2}.bin solc_output/${VAR2}.bin

rm   *.abi
rm   *bin
'''