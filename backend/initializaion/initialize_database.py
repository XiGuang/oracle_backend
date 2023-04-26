import os

import numpy as np
import json
import pandas as pd

from backend import app
from backend import db
from backend.modules import Meaning, Image, Word, OrdinaryTest, Idiom, Vocabulary, Essay


def create_tables():
    db.drop_all()
    db.create_all()
    create_word_table()
    create_test_table()
    create_idiom_table()
    create_vocabulary_table()
    create_essay_table()
    print('All tables created successfully')


def create_word_table():
    words = json.load(open('backend/data/final_word.json', 'r', encoding='utf-8'))
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
    tests = pd.read_excel('backend/data/test1解析版.xlsx', header=0)
    for index, test in tests.iterrows():
        if pd.isnull(test.get('A')):
            continue
        for i in range(0, 6):
            if pd.isnull(test[i]):
                test[i] = ''
        test = OrdinaryTest(question=test[0], A=test[1], B=test[2], C=test[3], D=test[4], answer=test[5],
                            answer_explanation=test[6])
        db.session.add(test)
        db.session.commit()
    print('Test table created successfully')


def create_idiom_table():
    idioms = np.loadtxt('backend/data/idiom_valid.csv', dtype=str, delimiter=',', encoding='utf-8-sig', skiprows=1)
    for idiom in idioms:
        word_ids = [Word.query.filter_by(word=word).first().id for word in idiom]
        idiom_db = Idiom(idiom=idiom, word_id_1=word_ids[0], word_id_2=word_ids[1], word_id_3=word_ids[2],
                         word_id_4=word_ids[3])
        db.session.add(idiom_db)
        db.session.commit()
    print('Idiom table created successfully')


def create_vocabulary_table():
    vocabularies = np.loadtxt('backend/data/ci_valid.csv', dtype=str, delimiter=',', encoding='utf-8-sig', skiprows=1)
    for vocabulary in vocabularies:
        word_ids = [Word.query.filter_by(word=word).first().id for word in vocabulary]
        vocabulary_db = Vocabulary(vocabulary=vocabulary, word_id_1=word_ids[0], word_id_2=word_ids[1])
        db.session.add(vocabulary_db)
        db.session.commit()
    print('Vocabulary table created successfully')


def create_essay_table():
    files = os.listdir('backend/data/Essay')
    for file in files:
        with open('backend/data/Essay/' + file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            name = lines[0].strip()[3:]
            author = lines[1].strip()[3:]
            content = ''
            for i in range(2, len(lines)):
                if lines[i].strip() == '' or lines[i].strip() == ' ':
                    continue
                else:
                    content += lines[i].strip().strip('\\') + '\n'
        essay = Essay(title=name, author=author, content=content)
        db.session.add(essay)
        db.session.commit()
    print('Essay table created successfully')

def modify_word_table():
    words = pd.read_excel('backend/data/甲骨文字2.xlsx', header=None)
    for index, word in words.iterrows():
        word_db = Word.query.filter_by(word=word[0]).first()
        if word_db is None:
            continue
        meaning = Meaning.query.filter_by(id=word_db.meaning_id).first()
        meaning.meaning = word[1]
        db.session.commit()
    print('Word table modified successfully')


if __name__ == '__main__':
    with app.app_context():
        create_tables()
