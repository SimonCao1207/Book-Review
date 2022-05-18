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

from bookshelf import get_model
from flask import Blueprint, redirect, render_template, request, url_for


crud = Blueprint('crud', __name__)

# [START list]
@crud.route("/")
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    books, next_page_token = get_model().list(cursor=token)

    return render_template(
        "list.html",
        books=books,
        next_page_token=next_page_token)

# [END list]

@crud.route('/<id>')
def view(id):
    book = get_model().read(id)
    rating, cntRate = get_model().avg_rating(id)
    return render_template("view.html", book=book, rating=rating, cntRate=cntRate)


# [START add]
@crud.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        book = get_model().create(data)
        get_model().create_review({'book_id' : book['id']})
        return redirect(url_for('.view', id=book['id']))
    return render_template("form.html", action="Add", book={})
# [END add]

# [START search]
@crud.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        print(data)
        results =  get_model().find(data)
        return render_template("list_search.html", results=results)
    return render_template("search.html")
# [END search]



@crud.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    book = get_model().read(id)
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        book = get_model().update(data, id)
        return redirect(url_for('.view', id=book['id']))
    return render_template("form.html", action="Edit", book=book)


@crud.route('/<id>/delete')
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.list'))


@crud.route('/<id>/review', methods=['GET', 'POST'])
def edit_review(id):
    book = get_model().read(id)
    reviews = get_model().read_review(id)
    print(reviews)
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        stat = get_model().find_user(data["user_name"], id)
        if (stat is not None):
            get_model().update_review(data, id, data["user_name"])
        else:
            data['book_id'] = id
            get_model().create_review(data)
        return redirect(url_for('.view', id=book['id']))
    return render_template("review_form.html", action='Review', book=book, review={}, reviews=reviews)
