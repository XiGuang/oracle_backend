from backend import db


class Meaning(db.Model):
    __tablename__ = 'meaning'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    meaning = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return '<meaning %r>' % self.meaning


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return '<image %r>' % self.image


class Word(db.Model):
    __tablename__ = 'word'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.String(1), nullable=False)
    pinyin = db.Column(db.String(10), nullable=True)
    radical = db.Column(db.String(10), nullable=True)
    meaning_id = db.Column(db.Integer, db.ForeignKey('meaning.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))

    def __repr__(self):
        return '<word %r>' % self.word


class OrdinaryTest(db.Model):
    __tablename__ = 'ordinary_test'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    A = db.Column(db.String(100), nullable=True)
    B = db.Column(db.String(100), nullable=True)
    C = db.Column(db.String(100), nullable=True)
    D = db.Column(db.String(100), nullable=True)
    answer = db.Column(db.Text, nullable=False)
    answer_explanation = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return '<ordinary_test %r>' % self.question


class Idiom(db.Model):
    __tablename__ = 'idiom'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idiom = db.Column(db.String(4), nullable=False)
    word_id_1 = db.Column(db.Integer, db.ForeignKey('word.id'))
    word_id_2 = db.Column(db.Integer, db.ForeignKey('word.id'))
    word_id_3 = db.Column(db.Integer, db.ForeignKey('word.id'))
    word_id_4 = db.Column(db.Integer, db.ForeignKey('word.id'))

    def __repr__(self):
        return '<idiom %r>' % self.idiom


class Vocabulary(db.Model):
    __tablename__ = 'vocabulary'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vocabulary = db.Column(db.String(2), nullable=False)
    word_id_1 = db.Column(db.Integer, db.ForeignKey('word.id'))
    word_id_2 = db.Column(db.Integer, db.ForeignKey('word.id'))

    def __repr__(self):
        return '<vocabulary %r>' % self.vocabulary


class Essay(db.Model):
    __tablename__ = 'essay'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<essay %r>' % self.title
