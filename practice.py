import re

def remove_special_characters(sentence : str) -> str:
    res = re.sub(r'[^a-zA-Z0-9]', '', sentence)

    return res

string1 = "Definitely, the world still needs peace and respect for humanity".lower()


string2 = "Definitely. The world still needs peace and respect for humanity.".lower()

new_string1 = remove_special_characters(string1)
new_string2 = remove_special_characters(string2)

print(f"First String ---> {remove_special_characters(string1)}")
print(f"Second String ---> {remove_special_characters(string2)}")

print(new_string1 == new_string2)
