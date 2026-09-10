import re

with open("test_regex") as f:
	contents = f.read()

def translate_time_to_Filipino(contents: str):
	PATTERNS = {
		"second_pattern": [re.compile(r"a second ago"), "isang segundo na ang nakalipas"],
		"seconds_pattern": [re.compile(r"seconds ago"), "segundo na ang nakalipas"],
		"minute_pattern": [re.compile("a minute ago"), "isang minuto na ang nakalipas"],
		"minutes_pattern": [re.compile(r"minutes ago"), "minuto na ang nakalipas"],
		"hour_pattern": [re.compile("an hour ago"), "isang oras na ang nakalipas"],
		"hours_pattern": [re.compile("hours ago"), "oras na ang nakalipas"]

	}

	for pattern in PATTERNS:
		contents = PATTERNS[pattern][0].sub(
			PATTERNS[pattern][1],
			contents
		)
	return contents

if __name__ == '__main__':
	translated_Fil_time = translate_time_to_Filipino('an hour ago')
	print(translated_Fil_time)
