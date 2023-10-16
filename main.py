from constants import INVERSE_SBOX_TABLE, INVERSE_MIX_COLUMN_TABLE, L_TABLE, E_TABLE, STRING_TO_INT, ROUND_KEYS

def add_round_key(round_key, cypher_text):
    # Convert hex strings to bytes
    key_bytes = bytes.fromhex(round_key)
    cypher_bytes = bytes.fromhex(cypher_text)

    # Perform XOR operation
    result_bytes = bytes(x ^ y for x, y in zip(key_bytes, cypher_bytes))

    # Convert the result back to a hexadecimal string
    result_hex = result_bytes.hex()

    # print("Result of XOR:", result_hex.upper())

    return result_hex.upper()

def reverse_shift_rows(row1, row2, row3, row4):
    new_row1 = row1[0:2] + row2[0:2] + row3[0:2] + row4[0:2]
    new_row2 = row4[2:4] + row1[2:4] + row2[2:4] + row3[2:4]   
    new_row3 = row3[4:6] + row4[4:6] + row1[4:6] + row2[4:6]
    new_row4 = row2[6:8] + row3[6:8] + row4[6:8] + row1[6:8] 
    return new_row1, new_row2, new_row3, new_row4

def substitution_byte(hex_string):
    # Convert the value to a list of bytes
    value_bytes = bytes.fromhex(hex_string)

    # Apply the Inverse SubBytes transformation
    result_bytes = bytes(INVERSE_SBOX_TABLE[nibble] for nibble in value_bytes)

    # Convert the result back to a hexadecimal string
    result_hex = result_bytes.hex().upper()

    return result_hex

def divide_string_by_4(hex_string):
    """Divides text into 4 parts.
    
    Assuming that the text is already read downwards.
    """
    row1 = hex_string[0:8]
    row2 = hex_string[8:16]
    row3 = hex_string[16:24]
    row4 = hex_string[24:32]

    return [row1, row2, row3, row4]

def mix_column(cypher_text):

    # Get the value from XOR of round key and mix column (if round 10, use shift row only)
    # round_key = 'BFE2BF904559FAB2A16480B4F7F1CBD8' # round 9 key
    # cypher_text = 'B68434E8E78860D7519866708CCAFB51'
    # cypher_text = add_round_key(round_key, cypher_text)
    # get the b1, b2, b3, b4
    string_list = divide_string_by_4(cypher_text)

    # get the constant from mix column table
    # v1, v2, v3, v4 = INVERSE_MIX_COLUMN_TABLE[0:4]
    new_cyphertext = []
    for i in range(4):
        b1 = string_list[i][0:2].upper()
        b2 = string_list[i][2:4].upper()
        b3 = string_list[i][4:6].upper()
        b4 = string_list[i][6:8].upper()
        # values = []
        for j in range(4):
            # index = i % 4
            values = [ f'0{hex(item)[2:].upper()}' for item in INVERSE_MIX_COLUMN_TABLE[j]]
            
            # print(b1, b2, b3, b4)
            # print(values[0])
            l1 = convert_to_l_table_value(b1) + convert_to_l_table_value(values[0]) # b1 =  r1 = 0E
            l2 = convert_to_l_table_value(b2) + convert_to_l_table_value(values[1])
            l3 = convert_to_l_table_value(b3) + convert_to_l_table_value(values[2])
            l4 = convert_to_l_table_value(b4) + convert_to_l_table_value(values[3])
            
            # print(l3, hex(l3), len(hex(l3)[2:]), hex(l3 - 255))
            # print(len(hex(l3)[2:]) > 2, len(hex(l3)[2:]), (hex(l3- 0xff) ))
            if len(hex(l1)[2:]) > 2:
                l1 = l1 - 0xff

            if len(hex(l2)[2:]) > 2:
                l2 = l2 - 0xff

            if len(hex(l3)[2:]) > 2:
                l3 = l3 - 0xff

            if len(hex(l4)[2:]) > 2:
                l4 = l4 - 0xff

            # print(l1,l2,l3,l4, '\n')

        # # #     print(l1, l2, l3, l4)

            l1 = convert_to_e_table_value(l1)
            l2 = convert_to_e_table_value(l2)
            l3 = convert_to_e_table_value(l3)
            l4 = convert_to_e_table_value(l4)

            nb1 = int(l1, 16) ^ int(l2, 16) ^ int(l3, 16) ^ int(l4, 16)

            nb1 = format(nb1, 'X')

            new_cyphertext.append(nb1.zfill(2))

    return ''.join(new_cyphertext)


def convert_to_l_table_value(value):
    # convert hex char to int
    new_value1 = STRING_TO_INT[value[0]]
    new_value2 = STRING_TO_INT[value[1]]
    
    # get list
    l_table_list = L_TABLE[new_value1]

    # get the final value
    final_value = l_table_list[new_value2]
    return final_value

def convert_to_e_table_value(value):
    # convert hex char to int
    value = hex(value)[2:] if len(hex(value)) > 3 else f'0{hex(value)[2:]}'
    new_value1 = STRING_TO_INT[value[0].upper()]
    new_value2 = STRING_TO_INT[value[1].upper()]
    
    # # get list
    l_table_list = E_TABLE[new_value1]

    # # get the final value
    final_value = l_table_list[new_value2]

    return final_value

def get_cyphertext(previous_cyphertext):
    row1 = previous_cyphertext[0:8]
    row2 = previous_cyphertext[8:16]
    row3 = previous_cyphertext[16:24]
    row4 = previous_cyphertext[24:32]
    new_row1, new_row2, new_row3, new_row4 = reverse_shift_rows(row1, row2, row3, row4)

    inverse_shifted_value = new_row1  + new_row2 + new_row3 +  new_row4

    hex_string = substitution_byte(inverse_shifted_value)
    
    
    row1 = hex_string[0:8]
    row2 = hex_string[8:16]
    row3 = hex_string[16:24]
    row4 = hex_string[24:32]

    h_row1 = row1[0:2] + row2[0:2] + row3[0:2] + row4[0:2]
    h_row2 = row1[2:4] + row2[2:4] + row3[2:4] + row4[2:4]
    h_row3 = row1[4:6] + row2[4:6] + row3[4:6] + row4[4:6]
    h_row4 = row1[6:8] + row2[6:8] + row3[6:8] + row4[6:8]

    
    new_cyphertext = h_row1 + h_row2 + h_row3 + h_row4

    return new_cyphertext

def decrypt():
    
    cypher_text = '29C3505F571420F6402299B31A02D73A'
    
    new_value = add_round_key(ROUND_KEYS['10'], cypher_text)
    cypher_text = get_cyphertext(new_value)
    

    new_value = add_round_key(ROUND_KEYS['9'], cypher_text) 
    original_value = mix_column(new_value)
    # cypher_text = get_cyphertext(original_value)

    
    original_value = add_round_key(ROUND_KEYS['8'], cypher_text)
    original_value = mix_column(original_value)
    cypher_text = get_cyphertext(original_value)

    original_value = add_round_key(ROUND_KEYS['7'], cypher_text)
    original_value = mix_column(original_value)
    cypher_text = get_cyphertext(original_value)

    original_value = add_round_key(ROUND_KEYS['6'], cypher_text)
    original_value = mix_column(original_value)
    cypher_text = get_cyphertext(original_value)

    original_value = add_round_key(ROUND_KEYS['5'], cypher_text)
    original_value = mix_column(original_value)
    cypher_text = get_cyphertext(original_value)

    original_value = add_round_key(ROUND_KEYS['4'], cypher_text)
    original_value = mix_column(original_value)
    cypher_text = get_cyphertext(original_value)

    original_value = add_round_key(ROUND_KEYS['3'], cypher_text)
    original_value = mix_column(original_value)
    cypher_text = get_cyphertext(original_value)

    original_value = add_round_key(ROUND_KEYS['2'], cypher_text)
    original_value = mix_column(original_value)
    cypher_text = get_cyphertext(original_value)

    original_value = add_round_key(ROUND_KEYS['1'], cypher_text)
    original_value = mix_column(original_value)
    cypher_text = get_cyphertext(original_value)

    original_value = add_round_key(ROUND_KEYS['0'], cypher_text)
    original_value = mix_column(original_value)
    cypher_text = get_cyphertext(original_value)

    print(cypher_text)



decrypt()



