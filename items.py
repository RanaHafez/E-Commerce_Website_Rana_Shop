import os
books = [
    {
        "id": 1,
        "price_id": os.environ["PRODUCT_1_PRICE_KEY"],
        "image": "https://www.richdad.com/MediaLibrary/RichDad/Images/books/rich-dad-poor-dad/RDPD-25th-cover-2022-864x1296-144dpi.jpg",
        "name": "Rich Dad Poor Dad",
        "description":"What the Rich Teach Their Kids About Money That the Poor and Middle Class Do Not!",
    },
    {
        "id": 2,
        "price_id": os.environ["PRODUCT_2_PRICE_KEY"],
        "image": "https://m.media-amazon.com/images/I/513TQ4ihqqL.jpg",
        "name": "Harry Potter and the Goblet of Fire",
        "description":"Harry Potter and the Goblet of Fire is a fun and entertaining book to read",
    }
]
