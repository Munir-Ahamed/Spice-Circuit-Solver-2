from cmath import cos, sin                                                                  # importing necessary modules
import math
import sys as s
from numpy import *

class resistor:                                                                             # classes for each element
    def __init__(self,name,n1,n2,value):
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.value = value

class inductor:
    def __init__(self,name,n1,n2,value):
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.value = value

class capacitor:
    def __init__(self,name,n1,n2,value):
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.value = value

class voltage_source:
    def __init__(self,name,n1,n2,value):
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.value = value

class current_source:
    def __init__(self,name,n1,n2,value):
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.value = value

def str_to_float(str):                                                                      # string to float converter
    if ("e" in str):                                                                        # of values of each component
        return (float(str.split("e")[0]))*(10**(float(str.split("e")[1])))
    else:
        return float(str)

if (len(s.argv) == 1):                                                                      # validating command in cmd line
    print("Enter an inputfile.")

elif (len(s.argv) > 2):
    print("More than one inputfile detected.")

else:

    try:                                                                                    # try and except makes sure the
        with open(s.argv[1]) as f:                                                          # netlist file is proper
            lines = f.readlines()
            start,end,ac = -1,-1,0

            for line in lines:                                                              # checks for .circuit, .end and
                if (line.split("#")[0].split()[0].strip() == ".circuit"):                   # .ac and takes their index
                    start = lines.index(line)

                elif (line.split("#")[0].split()[0].strip() == ".end"):
                    end = lines.index(line)

                elif (line.split("#")[0].split()[0].strip() == ".ac"):
                    ac = lines.index(line)
                    source_val = line.split("#")[0].split()[2]
                    freq = str_to_float(source_val)                                         # freq in calculated and stored as float


            if (start >= end or start == -1):                                               # makes sure the circuit definition is correct
                print("Invalid circuit definition")
                exit()
            
            elements = []
            v_count = 0                                                                     # no. of voltage sources
            print("Input netlist file: ", "\n")

            try:
                for k in range(start+1,end):
                    line = lines[k]
                    print(line)
                    a = line.split("#")[0].split()                                          # the comments in the line are removed
                                                                                            # and line is split to words
                    if (len(a) == 4):
                        name,n1,n2,value = a
                        value = str_to_float(value)

                        if (name[0] == "R"):                                                # creating R,L,C objects
                            b = resistor(name,n1,n2,value)
                        elif (name[0] == "L"):
                            b = inductor(name,n1,n2,value)
                        elif (name[0] == "C"):
                            b = capacitor(name,n1,n2,value)
                        
                        elements.append(b)                                                  # adding objects to elements list

                    else:

                        if (a[3] == "dc"):                                                  # value of voltage source is calculated
                            name,n1,n2,source_type,value = a                                # accordingly in case of ac and dc
                            value = str_to_float(value)
                        elif (a[3] == "ac"):
                            name,n1,n2,v_type,amp_pp,phase = a
                            value = (float(amp_pp)/2)*complex(cos(float(phase)), sin(float(phase)))

                        if (a[0][0] == "V"):
                            b = voltage_source(name,n1,n2,value)                            
                            v_count += 1                                                    # counting no. of voltage sources
                        elif (a[0][0] == "I"):
                            b = current_source(name,n1,n2,value)
                        
                        elements.append(b)                                                  # adding objects to elements list

            except:
                print("Invalid component inputs")
                exit()

        node = []                                                                           # empty list to collect node values 
        for b in elements:                                                                  # with repetition
            if(b.n1 == "GND"):
                b.n1 = 0
                b.n2 = int(b.n2)
            elif(b.n2 == "GND"):
                b.n2 = 0
                b.n1 = int(b.n1)
            else:
                b.n1 = int(b.n1)
                b.n2 = int(b.n2)
            node.append(b.n1)
            node.append(b.n2)
        
        node_list = []                                                                      # empty list to collect node values
        for x in node:                                                                      # without repetition
            if x not in node_list:
                node_list.append(x)
        node_list.sort()                                                                    # arranging node values in order
        node_dic = {"GND" :node_list[0]}

        for k in range(1, len(node_list)):                                                  # adding node names and values to dictionary
            node_dic.update({"Node" + str(k) :node_list[k]})
        
        print("Name of nodes and respective values:", "\n", "\n", node_dic, "\n", "\n")

        n = len(node_list)
        A = zeros(((n+v_count-1),(n+v_count-1)), dtype = complex_)                          # creating incidence matrix with zeros
        B = zeros(((n+v_count-1),1), dtype = complex_)                                      # creating source matrix with zeros
        k = 0
       
        for element in elements:
            if (element.name[0] == "R"):                                                    # updating values in each cell of the matrices
                if (element.n1 == "GND"):
                    A[int(element.n2)-1][int(element.n2)-1] += 1/element.value
                elif (element.n2 == "GND"):
                    A[int(element.n1)-1][int(element.n1)-1] += 1/element.value
                else:
                    A[int(element.n1)-1][int(element.n1)-1] += 1/element.value
                    A[int(element.n2)-1][int(element.n2)-1] += 1/element.value
                    A[int(element.n1)-1][int(element.n2)-1] += -1/element.value
                    A[int(element.n2)-1][int(element.n1)-1] += -1/element.value

            if (element.name[0] == "C"):
                Xc = -1/float(2*(math.pi)*freq*(element.value))
                element.value = complex(0,Xc)

                if (element.n1 == "GND"):
                    A[int(element.n2)-1][int(element.n2)-1] += 1/element.value
                elif (element.n2 == "GND"):
                    A[int(element.n1)-1][int(element.n1)-1] += 1/element.value
                else:
                    A[int(element.n1)-1][int(element.n1)-1] += 1/element.value
                    A[int(element.n2)-1][int(element.n2)-1] += 1/element.value
                    A[int(element.n1)-1][int(element.n2)-1] += -1/element.value
                    A[int(element.n2)-1][int(element.n1)-1] += -1/element.value

            if (element.name[0] == "L"):
                Xl = float(2*(math.pi)*freq*(element.value))
                element.value = complex(0,Xl)

                if (element.n1 == "GND"):
                    A[int(element.n2)-1][int(element.n2)-1] += 1/element.value
                elif (element.n2 == "GND"):
                    A[int(element.n1)-1][int(element.n1)-1] += 1/element.value
                else:
                    A[int(element.n1)-1][int(element.n1)-1] += 1/element.value
                    A[int(element.n2)-1][int(element.n2)-1] += 1/element.value
                    A[int(element.n1)-1][int(element.n2)-1] += -1/element.value
                    A[int(element.n2)-1][int(element.n1)-1] += -1/element.value

            if (element.name[0] == "V"):
                if (element.n1 == "GND"):
                    A[int(element.n2)-1][n+k-1] += -1
                    A[n+k-1][int(element.n2)-1] += -1
                    B[n+k-1] += element.value
                    k = k+ 1
                elif (element.n2 == "GND"):
                    A[int(element.n1)-1][n+k-1] += 1
                    A[n+k-1][int(element.n1)-1] += 1
                    B[n+k-1] += element.value
                    k =k+ 1
                else:
                    A[int(element.n1)-1][n+k-1] += 1
                    A[int(element.n2)-1][n+k-1] += -1
                    A[n+k-1][int(element.n2)-1] += -1
                    A[n+k-1][int(element.n1)-1] += 1
                    B[n+k-1] += element.value
                    k=k+1


            if (element.name[0] == "I"):
                if (element.n1 == "GND"):
                    B[int(element.n2)-1][0] += -element.value
                elif (element.n2 == "GND"):
                    B[int(element.n1)-1][0] += element.value
                else:
                    B[int(element.n1)-1][0] += element.value
                    B[int(element.n2)-1][0] += -element.value
        
        X = linalg.solve(A,B)                                                               # solving both the matrices and
        print("Source matrix: ", "\n", "\n", X,"\n" ,"\n")                                  # getting the node voltages and
        print("Output: ", "\n")                                                             # current through voltage source
        
        for m in range(n-1):                                                                # printing the result
            y = str(m+1)
            print("V" +y +" is", X[m], "\n")

        for l in range(v_count):
            y = str(m+1)
            print("I" +y +" is", X[l+n-1], "\n")

    except:
        print("The inputfile is invalid")
        exit()