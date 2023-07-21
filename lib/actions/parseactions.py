# takes a header file, outputs action ids

import tokenize
import sys


def filter(g):
	while True:
		t = next(g)
		if t[1] == "/*":
			while next(g)[1] != "*/":
				pass
			continue
		if t[1] == "//":
			while next(g)[1] != "\n":
				pass
			continue

		if t[1] != "\n":
#			print t
			yield t[1]


def do_file(f, mode):
	tokens = filter(tokenize.generate_tokens(open(f, 'r').readline))

	sys.stderr.write("parsing %s\n" % f)

	state = 0

	classstate = 0

	firsthit = 1

	while True:
		try:
			t = next(tokens)
		except:
			break

		if t == "class":
			classname = next(tokens)
			classstate = state

		if t == "{":
			state += 1

		if t == "}":
			state -= 1

		if t == "enum" and state == classstate + 1:
			actionname = next(tokens)

			if actionname == "{":
				while next(tokens) != "}":
					pass
				continue

			if actionname[-7:] == "Actions":
				if next(tokens) != "{":
					try:
						print(classname)
					except:
						pass

					try:
						print(actionname)
					except:
						pass

					raise Exception("action enum must be simple.")

				counter = 0

				while True:

					t = next(tokens)

					if t == "=":
						next(tokens)
						t = next(tokens)

					if t == "}":
						break

					if counter:
						if t != ",":
							raise Exception("no comma")
						t = next(tokens)

					if firsthit:

						if mode == "include":
							# hack hack hack!!
							print("#include <lib/" + '/'.join(f.split('/')[-2:]) + ">")
						else:
							print("\t// " + f)

						firsthit = 0

					if mode == "parse":
						print("{\"" + actionname + "\", \"" + t + "\", " + "::".join((classname, t)) + "},")

					counter += 1


mode = sys.argv[1]

if mode == "parse":
	print("""
	/* generated by parseactions.py - do not modify! */
struct eActionList
{
	const char *m_context, *m_action;
	int m_id;
} actions[]={""")

for x in sys.argv[2:]:
	do_file(x, mode)

if mode == "parse":
	print("};")
