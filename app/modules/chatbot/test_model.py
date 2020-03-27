import spacy


nlp = spacy.load("../FacultyModel")

doc = nlp("Who is Zilong Ye?")
for ent in doc.ents:
	print(f"\n\n\Input: {ent.text}\nEntity: {ent.label_}\n\n")

doc = nlp("What time does the food court close?")
for ent in doc.ents:
	print(f"Input: {ent.text}\nEntity: {ent.label_}\n\n")

doc = nlp("How do I apply for FAFSA?")
for ent in doc.ents:
	print(f"Input: {ent.text}\nEntity: {ent.label_}\n\n")

doc = nlp("What benefits does the student union provide?")
for ent in doc.ents:
	print(f"Input: {ent.text}\nEntity: {ent.label_}\n\n")

doc = nlp("What is Dr. Pamula's email?")
for ent in doc.ents:
	print(f"Input: {ent.text}\nEntity: {ent.label_}\n\n")