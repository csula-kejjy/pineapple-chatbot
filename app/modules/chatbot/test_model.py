import spacy


nlp = spacy.load("../FacultyModel")

doc = nlp("Who is Zilong Ye?")
for ent in doc.ents:
	print(ent.text, ent.label_, ent)