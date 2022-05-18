# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from email.policy import default
from operator import or_

from pkg_resources import resource_listdir
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


builtin_list = list


db = SQLAlchemy()


def init_app(app):
    # Disable track modifications, as it unnecessarily uses memory.
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)


def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data


# [START model]
class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    author = db.Column(db.String(255))
    publishedDate = db.Column(db.String(255))
    imageUrl = db.Column(db.String(255))
    description = db.Column(db.String(4096))
    createdBy = db.Column(db.String(255))
    createdById = db.Column(db.String(255))

    def __repr__(self):
        return "<Book(title='%s', author=%s)" % (self.title, self.author)
# [END model]

# [START model]
class Review(db.Model):
    __tablename__ = "reviews"
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    user_name = db.Column(db.String(255), primary_key=True, default="admin")
    rating = db.Column(db.Integer, default=0)
    comment = db.Column(db.String(4096), default="")

    def __repr__(self):
        return "<Review(account='%s', bookID=%s)" % (self.user_name, self.book_id)
# [END model]

# [START list]
def list(limit=10, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (Book.query
             .order_by(Book.title)
             .limit(limit)
             .offset(cursor))
    books = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(books) == limit else None
    return (books, next_page)
# [END list]

# [START read]
def read(id):
    result = Book.query.get(id)
    if not result:
        return None
    return from_sql(result)
# [END read]

# [START avg_rating]
def avg_rating(id):
    stats = db.session.query(Review.book_id, db.func.sum(Review.rating), db.func.count(Review.rating)).group_by(Review.book_id).all()
    for stat in stats:
        book_id, sumRate, cntRate = stat
        if (str(book_id) == id):
            if (cntRate > 1):
                cntRate -=1
            avgRating = int(sumRate) // cntRate
            break
        else:
            avgRating = 0
            cntRate = 1
    return avgRating, cntRate
# [END avg_rating]

# [START read_review]
def read_review(id):
    reviews = db.session.query(Review).filter(Review.book_id == id).all()
    return reviews
# [END read_review]

# [START create]
def create(data):
    book = Book(**data)
    db.session.add(book)
    db.session.commit()
    return from_sql(book)
# [END create]

# [START create review]
def create_review(data):
    review = Review(**data)
    db.session.add(review)
    db.session.commit()
# [END create review]


# [START update]
def update(data, id):
    book = Book.query.get(id)
    for k, v in data.items():
        setattr(book, k, v)
    db.session.commit()
    return from_sql(book)
# [END update]

# [START update review]
def update_review(data, id, user_name="admin"):
    review = Review.query.get((id, user_name))
    for k, v in data.items():
        setattr(review, k, v)
    db.session.commit()
# [END update review]

def delete(id):
    Review.query.filter_by(book_id=id).delete()
    Book.query.filter_by(id=id).delete()
    db.session.commit()

def find(data):
    title = data['title'].strip()
    year = data['year']
    results = Book.query.filter(or_(Book.title.ilike(f'%{title}%'), Book.publishedDate.ilike(f'%{year}%'))).all()
    return results

def find_user(user_name, id):
    results = Review.query.get((id, user_name))
    return results

def _create_database():
    """
    If this script is run directly, create all the tables necessary to run the
    application.
    """
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    init_app(app)
    with app.app_context():
        db.create_all()
    print("All tables created")


if __name__ == '__main__':
    _create_database()
