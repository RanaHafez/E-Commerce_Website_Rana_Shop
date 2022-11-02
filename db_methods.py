# get

def find_by_id(collection, id):
    return collection.query.get(int(id))


def find_all(db, collection):
    return db.session.query(collection).all()
# book = Book.query.filter_by(title="Harry Potter").first()