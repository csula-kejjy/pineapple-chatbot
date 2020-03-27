from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
from .mysqlstorage import MySQLStorage


# new entity label
LABEL = 'ROOM'
LABEL_2 = 'PHONE'

# training data
# Note: If you're using an existing model, make sure to mix in examples of
# other entity types that spaCy correctly recognized before. Otherwise, your
# model might learn the new type, but "forget" what it previously knew.
# https://explosion.ai/blog/pseudo-rehearsal-catastrophic-forgetting
#TRAIN_DATA = [

#    ("E&T 322 is the computer science office", {
#        'entities': [(0, 7, 'ROOM')]
#    }),

#    ("Which room is Dr.Kangs office", {
#        'entities': []
#    }),

#    ("The senior design room is in E&T B10", {
#        'entities': [(29, 36, 'ROOM')]
#    }),

#    ("The office of Dr.Pamula is E&T A324", {
#        'entities': [(27, 35, 'ROOM')]
#    }),

#    ("Dr.Zilong's office is in E&T A329", {
#        'entities': [(25, 33, 'ROOM')]
#    }),

#    ("Phone (342) 093-4325", {
#        'entities': [(6, 20, 'PHONE')]
#    }),

#    ("Office: E&T A327 Phone: (818) 343-6689 E-mail: zye5@calstatela.edu", {
#        'entities': [(8, 16, 'ROOM'), (24, 38, 'PHONE')]
#    }),

#    ("My phone number is (917) 343-0393", {
#        'entities': [(19, 33, 'PHONE')]
#    }),

#    ("His phone is missing", {
#        'entities': []
#    }),

#	("vakis@calstatela.edu Vladimir Akis", {
#        'entities': [(0, 12, 'EMAIL'), (13, 25, 'PERSON')]
#    })

#]

TRAIN_DATA = formatTrainingData()


@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    new_model_name=("New model name for model meta.", "option", "nm", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int))

def main(model=None, new_model_name='pineapple', output_dir='./models/pineapple_1_0', n_iter=10):
    """Set up the pipeline and entity recognizer, and train the new entity."""
    # if model is not None:
    #     nlp = spacy.load('en')
    #     print("Loaded model '%s'" % model)
    # else:
    #     nlp = spacy.blank('en')  # create blank Language class
    #     print("Created blank 'en' model")
    # Add entity recognizer to model if it's not in the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy

    nlp = spacy.load('en_core_web_sm')

    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner)
    # otherwise, get it, so we can add labels to it
    else:
        ner = nlp.get_pipe('ner')

    ner.add_label(LABEL)   # add new entity label to entity recognizer
    ner.add_label(LABEL_2)
    if model is None:
        optimizer = nlp.begin_training()
    else:
        # Note that 'begin_training' initializes the models, so it'll zero out
        # existing entity types.
        optimizer = nlp.entity.create_optimizer()

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4., 32., 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.35,
                           losses=losses)
            print('Losses', losses)


    test_text = 'Office E&T 420 Phone (323) 343-669 Address 5151 State University Drive, Los Angeles, CA 90032 Web cs.calstatela.edu or www.calstatela.edu/cs'

    doc = nlp(test_text)
    #print("Entities in '%s'" % test_text)
    for ent in doc.ents:
        print(ent.label_, ent.text)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta['name'] = new_model_name  # rename model
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        doc2 = nlp2(test_text)
        for ent in doc2.ents:
            print(ent.label_, ent.text)

def formatTrainingData():
	"""
	parses the data from the database into the following format:

		(STRING, DICTIONARY -> {'entities': 
									ARRAY -> [ 
												SET -> (INT, INT, STRING), 
												SET -> (INT, INT, STRING),
												... 
											 ]
								}
		)

	Returns the data in a set.
	"""

	training_data = set()
	database = MySQLStorage(user='', password='', database='chatbot_dev')

	query("""SELECT * FROM crawler""")
	database.cursor.execute(query)
	data = set(database.cursor.fetchall())

	for (idcrawler, url, keywords, category, subcategory) in data:
		text = ""
		for word in keywords:
			text += word
		text = text.replace("'", "").replace(",", "")
		# parse data into training data
		print("test")

	# maybe save this into a text file...?
	print("test")
	return training_data;

if __name__ == '__main__':
    plac.call(main)