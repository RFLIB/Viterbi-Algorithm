from typing import List
from itertools import cycle
import math
import copy

class ConvolutionalCode:
    def __init__(self, generators: tuple):
        generators_bin_char = []
        self.generators_bin_int = []
        self.max_generator_size = 0
        self.constraint = 0
        temp_generator_int = []
        for generator in generators:
            generators_bin_char.append(bin(generator))
        for generator in generators_bin_char:
            temp_generator = generator[2:]
            for bit in temp_generator:
                temp_generator_int.append(int(bit))
            self.generators_bin_int.append(temp_generator_int)
            temp_generator_int = []
        self.max_generator_size = len(max(self.generators_bin_int, key=len))
        self.constraint = self.max_generator_size - 1
        self.parse_generators()
        self.out_num = len(generators)
        

    def encode(self, data: bytes) -> List[int]:
        """
        :param data: data to be encoded
        :return: encoded data
        :rtype: list[int]
        """
        
        #take all generators and xor them with the input in segments of self.max_len
        #create list of outputs from the generators
        
        parsed_data = self.parse_input(data)
    
        data_to_encode = self.add_constraint(parsed_data)
        generator_indecies = self.get_generator_indecies()
        encoded = []
        
        for stream_idx, stream_value in enumerate(data_to_encode):
            temp_segment = data_to_encode[stream_idx:self.max_generator_size+stream_idx]
            
            

            for generator in generator_indecies:
                sum_one = 0
                for generator_idx, generator_value in enumerate(generator):
                    sum_one+=temp_segment[generator_value]

                if sum_one%2 == 0:
                    encoded.append(0)
                else:
                    encoded.append(1)
            temp_segment = []

            if (len(data_to_encode) - stream_idx) == self.max_generator_size:
                break
        
        
        return encoded
        
        #for i in range(0, len(data_to_encode)):
            
            #print(i) 
        #    print(data_to_encode[i:i+ self.max_generator_size])
        #    if len(data_to_encode) - i == self.max_generator_size:
        #        break
        

#converting hex input to bin int string with appropriate size
    def parse_input(self, input_stream):
        binary_input = "{:b}".format(int(input_stream.hex(), 16))
        missing_zeros = len(input_stream)*8 - len(binary_input)
        binary_input = '0'*missing_zeros + binary_input
        digit_input = []
        for bit in binary_input:
            digit_input.append(int(bit))
        return digit_input

#adding input constaint from left and from right (zero)
    def add_constraint(self, input_stream):
        constraint_list = [0 for i in range(self.constraint)]
        constrained_input = constraint_list + input_stream + constraint_list
        return constrained_input
    def get_generator_indecies(self):
        indecies = []
        for generator in self.generators_bin_int:
            
            temp_indecies = []
            for idx,value in enumerate(generator):
                if value!=0:
                    temp_indecies.append(idx)
            indecies.append(temp_indecies)
        return indecies


#creating a truth table for our states
    def truth_table(self):
        cols = self.max_generator_size
        rows = pow(2, cols)
        b = False
        n = 2
        truth_table = [[0 for i in range(cols)] for j in range(rows)]
        for i in range(0, cols):
            for j in range(0,rows):
                if b == False:
                    truth_table[j][i] = 0
                else:
                    truth_table[j][i] = 1
                if j%(rows/n) == ((rows/n)-1) and truth_table[j][i] == 1:
                    b = False
                if j%(rows/n) == ((rows/n)-1) and truth_table[j][i] == 0:
                    b = True
            n = n*2

        return truth_table
#adding required zeros to all generators
    def parse_generators(self):
        parsed_generators = []
        for idx, val in enumerate(self.generators_bin_int):
            if len(val) < self.max_generator_size:
                zeros_to_add = self.max_generator_size - len(val)
                temp_zeros = []
                for i in range(0,zeros_to_add):
                    temp_zeros.append(0)
                self.generators_bin_int[idx] = temp_zeros + self.generators_bin_int[idx]
    def get_output_table(self, truth_table):
        cols = self.out_num
        rows = len(truth_table)
        output_table = []
        indecies = self.get_generator_indecies()
        for row in truth_table:
            temp_output_row = []
            for generator in indecies:
                sum_one = 0
                for generator_idx, generator_value in enumerate(generator):
                    sum_one+=row[generator_value]
                if sum_one%2 == 0:
                    temp_output_row.append(0)
                else:
                    temp_output_row.append(1)
            output_table.append(temp_output_row)    
        return output_table

    def get_encoded_chunks(self, encoded):
        chunk_size = self.out_num
        encoded_chunks = [encoded[i:i+chunk_size] for i in range(0, len(encoded), chunk_size)]
        return encoded_chunks
        

    def get_states(self, truth_table):
        states = []
        for i in range(0, len(truth_table), 2):
            states.append(truth_table[i][:self.constraint])
        print(states)
        return states
        
        

    def hamming(self, s1,s2):
        result=0
        for x,(i,j) in enumerate(zip(s1,s2)):
            if i!=j:
                result+=1
        return result


    def decode(self, data: List[int]) -> (bytes, int):
        truth_table = self.truth_table()
        output_table = self.get_output_table(truth_table)
        encoded_chunks = self.get_encoded_chunks(data)
        path_length = len(encoded_chunks)
        states = self.get_states(truth_table)
        min_hamming = []
        decoded = []
        
        for state in states:
            print(state)
            states_value = {}
            temp_decoded, temp_cost = self.aux_decoded(state, encoded_chunks, output_table, truth_table, states_value, path_length, 0, []) 
            
            min_hamming.append(copy.deepcopy(temp_cost))
            decoded.append(copy.deepcopy(temp_decoded))
            
        
        return min_hamming, decoded
        




    def aux_decoded(self, state, chunks, states_output, truth_table, states_value, path_length, index, path):
        
        
        if index == path_length:
            return path, states_value[(index-1, tuple(state))]
        
        state_output_index0 = truth_table.index(state + [0])
        next_state0 = truth_table[state_output_index0][1:]
        child0 = tuple(next_state0) 

        state_output_index1 = truth_table.index(state + [1])
        next_state1 = truth_table[state_output_index1][1:]
        child1 = tuple(next_state1)

        path0 = path + [0] 
        path1 = path + [1]
        print("len of output_table")
        print(len(states_output))
        print(state_output_index0)
        print("len of chunks")
        print(len(chunks))
        print(index)
        cost0 = self.hamming(states_output[state_output_index0], chunks[index])
        cost1 = self.hamming(states_output[state_output_index1], chunks[index])
        
        key0 = (index, child0)
        key1 = (index, child1)
        if key0 in states_value.keys():
    
            if  states_value[key0] > cost0:
                states_value[key0] = cost0 
                min_path0, min_cost0 = self.aux_decoded(next_state0, chunks, states_output, truth_table, states_value, path_length, index+1, path0)
            else:
                states_value[key0] = math.inf
                return None, math.inf
        else:
                states_value[key0] = cost0 
                min_path0, min_cost0 = self.aux_decoded(next_state0, chunks, states_output, truth_table, states_value, path_length, index+1, path0)

       

        if key1 in states_value.keys():
    
            if  states_value[key1] > cost1:
                states_value[key1] = cost1 
                min_path1, min_cost1 = self.aux_decoded(next_state1, chunks, states_output, truth_table, states_value, path_length, index+1, path1)
            else:
                states_value[key1] = math.inf
                return None, math.inf
        else:
                states_value[key1] = cost1 
                min_path1, min_cost1 = self.aux_decoded(next_state1, chunks, states_output, truth_table, states_value, path_length, index+1, path1)

        if min_cost0 <= min_cost1:
            min_cost = min_cost0
            return min_path0, min_cost
        else:
            min_cost = min_cost1
            return min_path1, min_cost

            
        
#        decode = decode + [0]
#        zero_hamming = self.aux_decoded(next_state, chunks, state_output,truth_table, path_length, index+1, decode, zero_hamming + temp_hamming, one_hamming)


        
#        decode = decode + [1]
#        one_hamming = self.aux_decoded(next_state, chunks, state_output, truth_table, path_length,index+1, decode, zero_hamming, one_hamming + temp_hamming)
#        if zero_hamming < one_hamming:
            
#            return decode + [0]
#        else:
#            return decode + [1]

conv = ConvolutionalCode((3,7,13))
input_bytes = b"\x72\x01"
encoded = conv.encode(input_bytes)
print(encoded == [0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1] )
decoded, corrected_errors = conv.decode(encoded)





