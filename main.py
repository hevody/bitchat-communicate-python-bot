from dotenv import load_dotenv
import json
import os
import json
import logging

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import art.art_resource as art
import cryptography_specific.generate_key as keygen

def load_necessary_data() -> tuple[list, bool, str]:
	load_dotenv()
	with open("config.json") as f:
		config = json.load(fp=f)
	
	relays = config["RELAYS"]
	enable_proof_of_work = config["enable_proof_of_work"]
	PRIVATE_KEY = os.getenv("PRIVATE_KEY")

	return relays, enable_proof_of_work, PRIVATE_KEY

def menu():
	options = {
		"Generate a seed": keygen.generate_seed,
		"Exit": exit
	}

	options_with_index = list(options)

	print('')
	for index in range(len(options_with_index)):
		print(f'\t[{index + 1}] {options_with_index[index]}')

	try:
		choice = int(input('\n> ')) - 1
	except KeyboardInterrupt:
		exit()
	except:								# when decimal is given
		return							

	# input validation
	if choice < 0:
		return
	if choice + 1 > len(options_with_index):
		return

	options[options_with_index[choice]]()

class HeadingArt:
	def __init__(self):
		print(self.ascii_art_temple())
		print(self.ascii_art_text())

	def ascii_art_temple(self):
		CYAN_ANSI_COLOR_CODE = "\033[0;36m"
		ANSI_RESET = "\033[0m"
		ASCII_ART = r'''

  	               )\         O_._._._A_._._._O         /(
                  \`--.___,'=================`.___,--'/
                   \`--._.__                 __._,--'/
                     \  ,. l`~~~~~~~~~~~~~~~'l ,.  /
         __            \||(_)!_!_!_.-._!_!_!(_)||/            __
         \\`-.__        ||_|____!!_|;|_!!____|_||        __,-'//
          \\    `==---='-----------'='-----------`=---=='    //
          | `--.                                         ,--' |
           \  ,.`~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',.  /
             \||  ____,-------._,-------._,-------.____  ||/
              ||\|___!`======="!`======="!`======="!___|/||
              || |---||--------||-| | |-!!--------||---| ||
    __O_____O_ll_lO_____O_____O|| |'|'| ||O_____O_____Ol_ll_O_____O__
    o H o o H o o H o o H o o |-----------| o o H o o H o o H o o H o
   ___H_____H_____H_____H____O =========== O____H_____H_____H_____H___
                            /|=============|\
  ()______()______()______() '==== +-+ ====' ()______()______()______()
  ||{_}{_}||{_}{_}||{_}{_}/| ===== |_| ===== |\{_}{_}||{_}{_}||{_}{_}||
  ||      ||      ||     / |==== s(   )s ====| \     ||      ||      ||
  ======================()  =================  ()======================
  ----------------------/| ------------------- |\----------------------
                       / |---------------------| \
  -'--'--'           ()  '---------------------'  ()
                     /| ------------------------- |\    --'--'--'
         --'--'     / |---------------------------| \    '--'
                  ()  |___________________________|  ()           '--'-
    --'-          /| _______________________________  |\
   --'           / |__________________________________| \

		'''
		return CYAN_ANSI_COLOR_CODE + ASCII_ART + ANSI_RESET

	def ascii_art_text(self):
		BOLD_ANSI = "\033[1m"
		ANSI_RESET= "\033[0m"
		USAP_NOSTR_CLIENT = r'''
                                                                              
   ▄████  ▄▄     ▄▄▄  ▄▄▄▄▄ ▄▄▄▄▄ ▄▄▄▄    ▄█████ ▄▄    ▄▄ ▄▄▄▄▄ ▄▄  ▄▄ ▄▄▄▄▄▄ 
  ██  ▄▄▄ ██    ██▀██   ▄█▀ ██▄▄  ██▄█▄   ██     ██    ██ ██▄▄  ███▄██   ██   
   ▀███▀  ██▄▄▄ ██▀██ ▄██▄▄ ██▄▄▄ ██ ██   ▀█████ ██▄▄▄ ██ ██▄▄▄ ██ ▀██   ██   
                                                                              
    usap tayo, ano tara?
	  '''
		return BOLD_ANSI + USAP_NOSTR_CLIENT + ANSI_RESET





if __name__ == '__main__':
	# art.show_headings()
	# while True:
	# 	menu()
	HeadingArt()


