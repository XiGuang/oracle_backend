import numpy as np
import json

from backend import app
from backend.app import db
from models import Meaning, Image, Word, OrdinaryTest, Idiom, Vocabulary


def create_tables():
    db.drop_all()
    db.create_all()
    create_word_table()
    create_test_table()
    create_idiom_table()
    create_vocabulary_table()
    print('All tables created successfully')


def create_word_table():
    words = json.load(open('data/final_word.json', 'r', encoding='utf-8'))
    for word in words:
        meaning = Meaning(meaning=word['explanation'])
        db.session.add(meaning)
        db.session.commit()
        image = Image(image=word['path'])
        db.session.add(image)
        db.session.commit()
        word = Word(word=word['word'], pinyin=word['pinyin'], radical=word['radicals'], meaning_id=meaning.id,
                    image_id=image.id)
        db.session.add(word)
        db.session.commit()
    print('Word table created successfully')


def create_test_table():
    tests = np.loadtxt('data/test1.csv', dtype=str, delimiter=',', encoding='utf-8-sig', skiprows=1)
    for test in tests:
        test = OrdinaryTest(question=test[0], A=test[1], B=test[2], C=test[3], D=test[4], answer=test[5],
                            answer_explanation=test[6])
        db.session.add(test)
        db.session.commit()
    print('Test table created successfully')


def create_idiom_table():
    idioms = np.loadtxt('data/idiom_valid.csv', dtype=str, delimiter=',', encoding='utf-8-sig', skiprows=1)
    for idiom in idioms:
        word_ids = [Word.query.filter_by(word=word).first().id for word in idiom]
        idiom_db = Idiom(idiom=idiom, word_id_1=word_ids[0], word_id_2=word_ids[1], word_id_3=word_ids[2],
                         word_id_4=word_ids[3])
        db.session.add(idiom_db)
        db.session.commit()
    print('Idiom table created successfully')


def create_vocabulary_table():
    vocabularies = np.loadtxt('data/ci_valid.csv', dtype=str, delimiter=',', encoding='utf-8-sig', skiprows=1)
    for vocabulary in vocabularies:
        word_ids = [Word.query.filter_by(word=word).first().id for word in vocabulary]
        vocabulary_db = Vocabulary(vocabulary=vocabulary, word_id_1=word_ids[0], word_id_2=word_ids[1])
        db.session.add(vocabulary_db)
        db.session.commit()
    print('Vocabulary table created successfully')

if __name__ == '__main__':
    with app.app.app_context():
        create_tables()