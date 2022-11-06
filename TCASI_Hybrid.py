
# from unittest import result
from ast import And
from errno import ERANGE
from math import degrees
from operator import xor
import random
from unittest import result

class hybrid_LDPC:

    def __init__(self):
        self.degree = 6   #dv - has to be even
        self.random_number_sequence = []
        self.class_range = range(0, 10)
        for i in self.class_range:
            self.random_number_sequence.append(random.randrange(0, 1))

    ################################## the Sum Block implementation ##################################
    def S2T_adder(self, signP1, signP2, p1, p2):
        sum2 =  (not p2 and p1 and signP1) or (not p1 and p2 and signP2) or (p2 and p1 and signP2 and signP1)
        sum1 =  sum2 or (p1 and p2 and not(signP1) and not(signP2))
        sum0 =  (p1 and not p2) or (p2 and not p1)
        # return [0, sum0, sum1, sum2]
        return [sum2, sum2, sum1, sum0]

    def xor(a, b): 
        return (a and not b) or (b and not a)

    def ha(self, a, b): 
        return self.xor(a, b), a and b     # sum, carry

    def full_adder(self, a, b, ci):
        s0, c0 = self.ha(ci, a)
        s1, c1 = self.ha(s0, b)
        return s1, c0 or c1     # sum, carry

    def four_bit_adder(self, a, b):
        width = 4
        ci = [None] * width
        co = [None] * width
        s  = [None] * width
        for i in range(width):
            s[i], co[i] = self.full_adder(a[i], b[i], co[i-1] if i else 0)
        return s
            
    def parallel_adder(self, P):
        s2t_counter = 0
        results = []
        degree = self.degree
        while degree > 0 :
            s2t_counter += 1
            results.append(self.S2T_adder(self, P[s2t_counter][0], P[s2t_counter+1][0], P[s2t_counter][1], P[s2t_counter+1][1]))
            degree -= 2
        while len(results) > 1 :
            first_operand = results.pop()
            second_operand = results.pop()
            results.append(self.four_bit_adder(self, first_operand, second_operand))
        return results.pop()
    
    def add_reg(self, k_input):         ### here I should add the llr as the controller of register
        register_out = []
        middle_data = self.four_bit_adder(k_input, register_out)  if len(register_out)>0 else  k_input
        register_out = middle_data
        yield register_out

    def final_add(self, parallel_adder_output, added_P):
        Q = self.four_bit_adder( parallel_adder_output, added_P)
        return Q

    def sum_block(self, P):
        parallel_adder_to_reg = self.parallel_adder(P)
        parallel_adder_after_reg = self.add_reg(parallel_adder_to_reg)
        P_after_reg = []
        Q = []
        for unit in range(1, self.degree):
            P_after_reg[unit] = self.add_reg(P[unit])
            Q[unit] = self.four_bit_adder(P_after_reg[unit], parallel_adder_after_reg)
        return Q


    ################################## the SNG implementation ##################################

    def SNG(self, input_number):
        for i in self.class_range:  
            if input_number > self.random_array[i]:
                yield 1
            else:
                yield 0

    ################################## the VN implementation ##################################

    def VN(self, preprocessing_in, CN_in):
        early_termination = []
        ## I should 
        # 1-do sth with preprocessing data
        # 2-generate early_termination
        return self.SNG(self.sum_block(CN_in)), early_termination

    ################################## the MIN implementation ##################################

    def degree_minus_AND_gate(self, input):
        while len(input) > 1 :
            first_operand = input.pop()
            second_operand = input.pop()
            input.append(first_operand and second_operand)
        return input.pop()

    def degree_XOR_gate(self, input):
        while len(input) > 1 :
            first_operand = input.pop()
            second_operand = input.pop()
            input.append(xor(first_operand, second_operand))
        return input.pop()

    def mag(self, Q):
        P = []
        Q_minus_1 = []
        for i in range(0, self.degree-1):
            Q_minus_1 = Q
            Q_minus_1.pop(i)
            P.append(self.degree_minus_AND_gate(Q_minus_1))
        return P

    def sign(self, signQ):
        sign_out = self.degree_XOR_gate(signQ)
        signP = []
        for i in range(0, self.degree-1):
            signP.append(xor(signQ, sign_out))
        return signP

    def min_block(self, signQ, Q):
        return self.sign(signQ), self.mag(Q)


    ################################## the connection between parts ##################################

    
