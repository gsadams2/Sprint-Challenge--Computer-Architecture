

"""CPU functionality."""

import sys


LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
JMP = 0b01010100
ADD = 0b10100000
CMP = 0b10100111
JEQ = 0b01010101
JNE = 0b01010110


# Call does two things
# 1) store return address on the stack  
# 2) set the pc to whatever was in the register 

# Return does two things
# 1) pop the value off the stack
# 2) take the value that it got off the stakc and  put it into that PC

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.reg = [0]*8 #these are like our variables... R0, R1,... R7
        self.ram = [0]*256 #or should we do 255?
        self.SP = 7
        self.reg[self.SP] = 0xf4 #initialize SP to empty stack 
        self.E = 0
        self.L = 0
        self.G = 0

    def load(self):
        """Load a program into memory."""

        
        address = 0

        if len(sys.argv) != 2:
            print("usage: ls8.py filename")
            sys.exit(1)
        
        progname = sys.argv[1]


        with open(progname) as f:
            for line in f:
                line = line.split("#")[0]
                line = line.strip() #lose whitespace 

                if line == "":
                    continue

                val = int(line, 2) #binary so it's base 2

                self.ram[address] = val
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        
        #elif op == "SUB": etc

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
            
        elif op == 'CMP':
            if self.reg[reg_a] == self.reg[reg_b]:
                self.L = 0
                self.E = 1
                self.G = 0
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.L = 1
                self.E = 0
                self.G = 0
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.L = 0
                self.E = 0
                self.G = 1

        else:
            raise Exception("Unsupported ALU operation")

 

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # ram_read() should accept the address to read and return the value stored there.
    def ram_read(self, memory_address):
        return self.ram[memory_address]

    # ram_write() should accept a value to write, and the address to write it to.
    def ram_write(self, memory_address, value):
        self.ram[memory_address] = value


    def run(self):
        """Run the CPU."""
        while self.ram_read(self.pc) != HLT:


            # instruction = memory[pc]
            instruction = self.ram_read(self.pc)

            # LDI: load "immediate", store a value in a register, or "set this register to this value".
            if instruction == LDI:
                # read the bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b
                operand_register = self.ram_read(self.pc + 1)
                operand_value = self.ram_read(self.pc + 2)

                # Set the value of a register to an integer.
                # register[reg_num] = value
		        # pc += 3

                self.reg[operand_register] = operand_value

                #3 byte instruction
                self.pc += 3
            

            # PRN: a pseudo-instruction that prints the numeric value stored in a register.

            elif instruction == PRN:
                operand_register = self.ram_read(self.pc + 1)

                print(self.reg[operand_register])

                #2 byte instruction so add 2
                self.pc += 2

         

            elif instruction == MUL:
                operand_a = self.ram_read(self.pc + 1)
                operand_b = self.ram_read(self.pc + 2)
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3

          

            elif instruction == PUSH:
                self.reg[self.SP] -= 1 # decrement sp 

                # need register number... push is a two byte instruction 
                reg_num = self.ram_read(self.pc + 1)
                
                # now need value so we can copy it into memory where the stack pointer is 
                reg_value = self.reg[reg_num]

                
                # copy register value into memory at the address SP
                self.ram[self.reg[self.SP]] = reg_value

                self.pc += 2 # 2 byte instruction
            
            elif instruction == POP:
                # get the value out of memory where the stack pointer is pointing
                val = self.ram[self.reg[self.SP]]

                reg_num = self.ram[self.pc + 1]

                self.reg[reg_num] = val  # copy val from memory at SP into register 

                self.reg[self.SP] += 1 #incremeent the SP

                self.pc += 2 # 2 byte instruction
            
            elif instruction == CALL:
                #push return addr on stack
            
                return_address = self.pc + 2 # we know return address will be +2 b/c call is a 2 byte function
                self.reg[self.SP] -= 1 #decrement sp 
                self.ram[self.reg[self.SP]] = return_address


                #set the pc to the value in the register 
                
                reg_num = self.ram[self.pc + 1]
        

                self.pc = self.reg[reg_num]
            
            elif instruction == ADD:
                operand_a = self.ram_read(self.pc + 1)
                operand_b = self.ram_read(self.pc + 2)
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3
       

            elif instruction == RET:
                # pop the return address off stack
                # store it in the pc 
                self.pc = self.ram[self.reg[self.SP]]
                
                self.reg[self.SP] += 1

            elif instruction == CMP:
                a = self.ram_read(self.pc + 1)
                b = self.ram_read(self.pc + 2)

                self.alu('CMP', a, b)
                self.pc += 3
            
            elif instruction == JMP:
                a = self.ram[self.pc + 1]                

                self.pc = self.reg[a]
            
            elif instruction == JEQ:
                a = self.ram[self.pc + 1]
                
                if self.E == 1:
                    self.pc = self.reg[a]
                
                else:
                    self.pc += 2
                    #inctement 
            
            
            elif instruction == JNE:
                a = self.ram[self.pc + 1]

                if self.E == 0:
                    self.pc = self.reg[a]
                
                else:
                    self.pc += 2
            
                    
            else:
                print("UNKNOWN INSTRUCTION")
                # sys.exit(1)
                break
                
            
     


# python3 ls8.py examples/test.ls8