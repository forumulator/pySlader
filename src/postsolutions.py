import sys, time, os, os.path
from sladeragent import SladerAgent
from solutionparser import *
from Crypto.Cipher import DES

SLADER_USER = "forumulator"
SLADER_PASS = "mindo32hell"

def depad(text):
    return text.split("~")[0]

def pad(text):
    pad_len = 8 - len(text) % 8
    return text + ''.join((['~'] * pad_len))

def decrypt_creds():
    passwd = input("Please enter the passkey: ")
    des = DES.new(passwd, DES.MODE_ECB)
    global SLADER_PASS, SLADER_USER
    SLADER_USER = depad(des.decrypt(SLADER_USER))
    SLADER_PASS = depad(des.decrypt(SLADER_PASS))

def get_parser(file_name):
    """ Return the parser object based on the kind of text file """
    if not os.path.exists(file_name):
        raise ValueError("Invalid Path: " + file_name)
    if os.path.isfile(file_name):
        parser = TextSolutionParser(file_name)
    else:
        parser = SolutionDirParser(file_name)
    return parser 

def main():
    soln_file = sys.argv[1]
    with SladerAgent(SLADER_USER, SLADER_PASS) as sl_agent, \
            get_parser(soln_file) as prsr:
        for solution in prsr.solutions():
            print("Posting solution")
            try:
                sl_agent.post_answer(solution)
            except (ValueError, Exception) as e:
                if "Invalid book" in str(e):
                    raise e
                else:
                    print(str(e))

if __name__ == "__main__":
    if (len(sys.argv)) < 2:
        print("Error: Missing argument - filename")
        sys.exit(1)
    try:
        ret = main()
        sys.exit(ret)
    except Exception as e:
        print("Error: " + str(e))
        sys.exit(1)

# Google
# GoogIe