class Course:
    def __init__(self, id, title, description, price):
        self.id = id
        self.title = title
        self.description = description
        self.price = price

# Saytda ko'rinadigan barcha kurslar ro'yxati (Yagona manba)
courses_list = [
    Course(1, "Python Dasturlew", "Nolden professionalga shekem.", "500,000 som"),
    Course(2, "Web Dizayn", "Shirayli interfeyslar.", "450,000 som"),
    Course(3, "SMM ham Marketing", "Brendti rawajlandiriw.", "400,000 som"),
    Course(4, "Grafik Dizayn", "Photoshop ham Illustrator.", "420,000 som"),
    Course(5, "Telegram Bot", "Quramali botlar jaratiwdi uyrenin.", "400,000 som"),
]