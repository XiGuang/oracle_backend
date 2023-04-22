import json
import os
import random

import cv2
import PIL.Image
import numpy as np
from flask import Blueprint, request, jsonify, make_response

from backend.functions import getIdiomImage, renameWithHash, getSentenceImage, url_for, getCardImage, cv2PIL, to_path
from backend.modules import Meaning, Image, Word, OrdinaryTest, Idiom, Vocabulary
from backend.detectors.oracle_detector import OracleDetector
from backend.detectors.rubbing_detector import RubbingDetector

main = Blueprint('main', __name__)

oracle_detector = OracleDetector('backend/models/oracle.onnx', 'backend/detectors/oracle_dict.pkl')
rubbing_detector = RubbingDetector('backend/models/best_rubbing.onnx')


@main.route('/')
def index():
    return 'hello world'


# 得到请求甲骨文的含义或者图片
@main.route('/api/word', methods=['GET'])
def get_word():
    need_word = request.form['word']
    demand = request.form['demand']

    word = Word.query.filter_by(word=need_word).first()
    if not word:
        return make_response('Word not found', 400)

    if demand == 'meaning':
        meaning = Meaning.query.filter_by(id=word.meaning_id).first()
        if meaning:
            return meaning.meaning
        else:
            return make_response('Meaning not found', 400)
    elif demand == 'image':
        image = Image.query.filter_by(id=word.image_id).first()
        if image:
            return url_for('images/' + image.image)
        else:
            return make_response('Image not found', 400)
    elif demand == 'both':
        meaning = Meaning.query.filter_by(id=word.meaning_id).first()
        image = Image.query.filter_by(id=word.image_id).first()
        if meaning and image:
            return jsonify({'meaning': meaning.meaning, 'image': url_for('images/' + image.image)})
        else:
            return make_response('Meaning or image not found', 400)
    elif demand == 'extra':
        meaning = Meaning.query.filter_by(id=word.meaning_id).first()
        image = Image.query.filter_by(id=word.image_id).first()
        image_pil = PIL.Image.open(to_path('backend/static/images/' + image.image))
        similarity = oracle_detector.predictTopN(image_pil, 3)
        similarity = [i[0] for i in similarity if i[0] != need_word][:2]
        similar_images = [Image.query.filter_by(id=Word.query.filter_by(word=i).first().id).first().image for i in
                          similarity]
        if meaning and image:
            return jsonify({'image': url_for('images/' + image.image), 'meaning': meaning.meaning,
                            'pinyin': word.pinyin, 'radical': word.radical,
                            'similarity': {similarity[0]: url_for('images/' + similar_images[0]),
                                           similarity[1]: url_for('images/' + similar_images[1])}})
        else:
            return make_response('Meaning or image not found', 400)
    else:
        return make_response('Invalid demand', 400)


@main.route('/api/ordinary_test', methods=['GET'])
def get_ordinary_test():
    length = OrdinaryTest.query.count()
    question_ids = []
    while len(question_ids) < 10:
        num = random.randint(1, length)
        if num not in question_ids:
            question_ids.append(num)
    tests = [OrdinaryTest.query.filter_by(id=i).first() for i in question_ids]
    return jsonify([[i.id, i.question, i.A, i.B, i.C, i.D, i.answer, i.answer_explanation] for i in tests])


@main.route('/api/test_by_id', methods=['GET'])
def get_test_by_id():
    id = int(request.form['id'])
    test = OrdinaryTest.query.filter_by(id=id).first()
    return jsonify([test.id, test.question, test.A, test.B, test.C, test.D, test.answer, test.answer_explanation])


# return [{idioms, image}, {idioms, image}, ...]
@main.route('/api/idiom_test', methods=['GET'])
def get_idiom_test():
    number = int(request.form['number'])
    length = Idiom.query.count()
    idiom_ids = []
    while len(idiom_ids) < number:
        num = random.randint(1, length)
        if num not in idiom_ids:
            idiom_ids.append(num)
    idioms = [Idiom.query.filter_by(id=i).first() for i in idiom_ids]
    idiom_paths = []
    for idiom in idioms:
        words = [Word.query.filter_by(id=idiom.word_id_1).first(),
                 Word.query.filter_by(id=idiom.word_id_2).first(),
                 Word.query.filter_by(id=idiom.word_id_3).first(),
                 Word.query.filter_by(id=idiom.word_id_4).first()]
        image_paths = [to_path('backend/static/images/' + Image.query.filter_by(id=words[i].image_id).first().image) for i in range(4)]
        image = getIdiomImage(image_paths)
        name = renameWithHash(image)
        files = os.scandir('backend/static/temp')
        if name not in [file.name for file in files]:
            image.save('backend/static/temp/' + name)
        idiom_paths.append(url_for('temp/' + name))
    return jsonify([{idioms[i].idiom: idiom_paths[i]} for i in range(10)])


@main.route('/api/idiom', methods=['GET'])
def get_idiom():
    idiom = request.form['idiom']
    idiom_db = Idiom.query.filter_by(idiom=idiom).first()
    if not idiom_db:
        return make_response('Idiom not found', 400)
    words = [Word.query.filter_by(id=idiom_db.word_id_1).first(),
             Word.query.filter_by(id=idiom_db.word_id_2).first(),
             Word.query.filter_by(id=idiom_db.word_id_3).first(),
             Word.query.filter_by(id=idiom_db.word_id_4).first()]
    image_paths = [to_path('backend/static/images/' + Image.query.filter_by(id=words[i].image_id).first().image) for i in range(4)]
    image = getIdiomImage(image_paths)
    name = renameWithHash(image)
    files = os.scandir('backend/static/temp')
    if name not in [file.name for file in files]:
        image.save('backend/static/temp/' + name)
    return jsonify(url_for('temp/' + name))


# return: [{vocabulary, [bool,bool,bool,bool],[image_path,image_path,image_path,image_path]},...]
@main.route('/api/vocabulary_test', methods=['GET'])
def get_vocabulary_test():
    number = int(request.form['number'])
    length = Vocabulary.query.count()
    vocabulary_ids = []
    while len(vocabulary_ids) < number:
        num = random.randint(1, length)
        if num not in vocabulary_ids:
            vocabulary_ids.append(num)
    vocabularies = [Vocabulary.query.filter_by(id=i).first() for i in vocabulary_ids]
    results = []
    for vocabulary in vocabularies:
        # 生成错误答案的id
        length = Word.query.count()
        wrong_words_ids = []
        while len(wrong_words_ids) < 2:
            num = random.randint(1, length)
            if num not in wrong_words_ids and num not in [vocabulary.word_id_1, vocabulary.word_id_2]:
                wrong_words_ids.append(num)
        words = [Word.query.filter_by(id=vocabulary.word_id_1).first(),
                 Word.query.filter_by(id=vocabulary.word_id_2).first(),
                 Word.query.filter_by(id=wrong_words_ids[0]).first(),
                 Word.query.filter_by(id=wrong_words_ids[1]).first()]
        # 随机打乱答案顺序
        random.shuffle(words)
        answers = [words[i].word in vocabulary.vocabulary for i in range(4)]
        image_paths = [url_for('images/' + Image.query.filter_by(id=words[i].image_id).first().image)
                       for i in range(4)]
        results.append({'vocabulary': vocabulary.vocabulary,
                        'answers': answers,
                        'images': image_paths})
    return jsonify(results)


@main.route('/api/vocabulary', methods=['GET'])
def get_vocabulary():
    vocabulary = request.form['vocabulary']
    vocabulary_db = Vocabulary.query.filter_by(vocabulary=vocabulary).first()
    if not vocabulary_db:
        return make_response('Vocabulary not found', 400)

    words = [Word.query.filter_by(id=vocabulary_db.word_id_1).first(),
             Word.query.filter_by(id=vocabulary_db.word_id_2).first()]
    image_paths = [url_for('images/' + Image.query.filter_by(id=words[i].image_id).first().image)
                   for i in range(2)]
    return jsonify({'images': image_paths})


# return: [{image,[bool,bool,bool,bool],[word,word,word,word]},...]
@main.route('/api/word_test', methods=['GET'])
def get_word_test():
    length = Word.query.count()
    word_ids = []
    while len(word_ids) < 10:
        num = random.randint(1, length)
        if num not in word_ids:
            word_ids.append(num)
    results = []
    for word_id in word_ids:
        # 生成错误答案的id
        length = Word.query.count()
        wrong_words_ids = []
        while len(wrong_words_ids) < 3:
            num = random.randint(1, length)
            if num not in wrong_words_ids and num != word_id:
                wrong_words_ids.append(num)
        right_word = Word.query.filter_by(id=word_id).first()
        words = [right_word,
                 Word.query.filter_by(id=wrong_words_ids[0]).first(),
                 Word.query.filter_by(id=wrong_words_ids[1]).first(),
                 Word.query.filter_by(id=wrong_words_ids[2]).first()]
        # 随机打乱答案顺序
        random.shuffle(words)
        answers = [words[i].id == word_id for i in range(4)]
        image_path = url_for('images/' + Image.query.filter_by(id=right_word.image_id).first().image)
        meaning = Meaning.query.filter_by(id=right_word.meaning_id).first()
        results.append({'words': [words[i].word for i in range(4)],
                        'answers': answers,
                        'image_path': image_path,
                        'meaning': meaning.meaning})
    return jsonify(results)


@main.route('/api/translate_2_oracle', methods=['GET'])
def translate_2_oracle():
    sentence = request.args.get('sentence')
    if sentence is None:
        make_response('sentence is None', 400)
    sentence_paths = []
    for c in sentence:
        word = Word.query.filter_by(word=c).first()
        if word is None:
            continue
        image_path = to_path('backend/static/images/' + Image.query.filter_by(id=word.image_id).first().image)
        sentence_paths.append(image_path)
    image = getSentenceImage(sentence_paths)
    name = renameWithHash(image)
    files = os.scandir('backend/static/temp')
    if name not in [file.name for file in files]:
        image.save('backend/static/temp/' + name)
    return url_for('temp/' + name)


# 接受的格式为：{"words":[{"word":"word","position":[0,0],"color":[0,0,0]},...]}
@main.route('/api/card_customization_custom', methods=['GET', 'POST'])
def card_customization():
    card = request.files.get("image")
    if card is None:
        return make_response('image is None', 400)
    card_data = np.frombuffer(card.read(), np.uint8)
    card_cv = cv2.imdecode(card_data, cv2.IMREAD_COLOR)
    if card_cv.shape != (600, 800, 3):
        card_cv = cv2.resize(card_cv, (600, 800))
    words = request.form['words']
    words = json.loads(words)
    card_pil = getCardImage(card_cv, words)
    if card_pil is None:
        return make_response('word error', 400)
    name = renameWithHash(card_pil)
    card_pil.save('backend/static/temp/' + name)
    return url_for('temp/' + name)


@main.route('/api/rubbing_translate', methods=['GET','POST'])
def rubbing_translate():
    rubbing = request.files.get("image")
    if rubbing is None:
        return make_response('image is None', 400)
    rubbing_data = np.frombuffer(rubbing.read(), np.uint8)
    rubbing_cv = cv2.imdecode(rubbing_data, cv2.IMREAD_COLOR)
    image, words = rubbing_detector.process(rubbing_cv, 0.6)
    rubbing_pil = cv2PIL(image)
    sentence = ''
    for word in words:
        top, left, bottom, right, _, _ = word
        word_pil = rubbing_pil.crop((left, top, right, bottom))
        sentence += oracle_detector.predictTopN(word_pil, 1)[0][0]
    name = renameWithHash(rubbing_pil)
    if name not in [file.name for file in os.scandir('backend/static/temp')]:
        rubbing_pil.save('backend/static/temp/' + name)
    return jsonify({'sentence': sentence, 'image': url_for('temp/' + name)})


@main.route('/api/handwriting_judge', methods=['GET','POST'])
def handwriting_judge():
    handwriting = request.files.get('image')
    if handwriting is None:
        return make_response('image is None', 400)
    handwriting_data = np.frombuffer(handwriting.read(), np.int8)
    handwriting_cv = cv2.imdecode(handwriting_data, cv2.IMREAD_COLOR)
    handwriting_pil = cv2PIL(handwriting_cv)
    right_word = request.form.get("word")
    if right_word is None:
        return make_response("Word not found .", 400)
    writing_word = oracle_detector.predictTopN(handwriting_pil, 1)[0][0]
    if writing_word == right_word:
        return make_response('1', 200)
    return make_response('0', 200)


@main.route('/api/word_detect', methods=['GET','POST'])
def word_detect():
    word_image = request.files.get("image")
    if word_image is None:
        return make_response('image is None', 400)
    word_image_data = np.frombuffer(word_image.read(), np.uint8)
    word_image_cv = cv2.imdecode(word_image_data, cv2.IMREAD_COLOR)
    word_image_pil = cv2PIL(word_image_cv)
    words = oracle_detector.predictTopN(word_image_pil, 2)
    result = []
    for word in words:
        word_db = Word.query.filter_by(word=word[0]).first()
        if word_db is None:
            return make_response('word not found', 400)
        image_path = url_for('images/' + Image.query.filter_by(id=word_db.image_id).first().image)
        meaning = Meaning.query.filter_by(id=word_db.meaning_id).first().meaning
        result.append({'word': word[0], 'image': image_path, 'meaning': meaning})
    return jsonify(result)


@main.route("/api/upload", methods=["POST", "GET"])
def upload_image():
    image = request.files.get("file")
    print(image)
    if image:
        # 将图片保存到本地
        image.save("image.png")
        return "Image uploaded successfully."
    else:
        return "No image found in the request."


@main.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'})
