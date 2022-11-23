class BaseValue:
    def __init__(self):
        self.type = str
        self._value = None

    @property
    def is_filled(self):
        return self._value is not None

    @classmethod
    def class_name(cls):
        return cls.__name__

    def __repr__(self):
        return f"{self._value}: {self.type.__name__}"

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, _value):
        if _value is not None:
            if isinstance(_value, self.type):
                self._value = _value
            else:
                raise ValueError(
                    f"Value of {self.__class__.__name__} must be instance of {self.type}")


class BaseString(BaseValue):
    def __init__(self):
        super(BaseString, self).__init__()
        self.type = str


class BaseEntity:
    def __repr__(self):
        output = {
            "class": self.__class__.__name__
        }
        for attr in self.attributes:
            output[attr] = self.get_attribute_type(attr)
        return str(output)

    @classmethod
    def class_name(cls):
        return cls.__name__

    @property
    def attributes(self):
        output = self.__dir__()
        return [item for item in output
                if "__" not in item and "_" != item[0]
                and item not in ["attributes", "get_attribute_type", "class_name", "has_attribute", "add_attribute"]]

    def get_attribute_type(self, attr_name):
        if attr_name in self.attributes:
            return self.__getattribute__(attr_name)

    def add_attribute(self, item):
        for attr in self.attributes:
            attr_value = self.get_attribute_type(attr)
            if attr_value.type.__name__ == item.class_name():
                attr_value.value = item
                return True
        return False

    # def add_attribute(self, item):
    #     attr_value = self.get_attribute_type(item.class_name())
    #     attr_value.value = item


class Title(BaseValue):
    def __init__(self):
        super(Title, self).__init__()
        self.type = str


class Month(BaseValue):
    def __init__(self):
        super(Month, self).__init__()
        self.type = str


class Year(BaseValue):
    def __init__(self):
        super(Year, self).__init__()
        self.type = str


class Date(BaseValue):
    def __init__(self):
        super(Date, self).__init__()
        self.type = str


class Person(BaseEntity):
    def __init__(self, name=None, age=None):
        super(Person, self).__init__()
        self._name = BaseString()
        self._age = Year()
        self._name.value = name
        self._age.value = age

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, _age):
        self.age.value = _age

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, _name):
        self._name.value = _name


class Time(BaseEntity):
    date = Date()
    month = Month()
    year = Year()

    def __init__(self, date=None, month=None, year=None):
        self.date.value = date
        self.month.value = month
        self.year.value = year


class PersonType(BaseValue):
    def __init__(self):
        super(PersonType, self).__init__()
        self.type = Person


class TimeType(BaseValue):
    def __init__(self):
        super(TimeType, self).__init__()
        self.type = Time


class Document(BaseEntity):
    def __init__(self, title=None, author=None, time=None):
        super(Document, self).__init__()
        self._title = BaseString()
        self._author = PersonType()
        self._time = TimeType()
        self._title.value = title
        self._author.name = author
        self._time.value = time

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, _title):
        self._title.value = _title

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, _author):
        self._author = _author


person_entities = ["Hồ Chí Minh", "Nguyễn Trãi"]
year_entities = [str(i) for i in range(1000, 2025)]
document_entities = ["Nhật ký trong tù", "Đường Kách Mệnh", "Bình Ngô đại cáo", "Quốc âm thi tập",
                     "Quân trung từ mệnh tập", "Dư địa chí"]


class NER:
    @staticmethod
    def extract(input_text):
        output = []
        for ent in person_entities:
            if ent in input_text:
                output.append(Person(name=ent))

        for ent in year_entities:
            if ent in input_text:
                output.append(Time(year=ent))

        for ent in document_entities:
            if ent in input_text:
                output.append(Document(title=ent))

        return output


# ví dụ extract data từ câu:

text = "Nhật ký trong tù là tác phẩm của Hồ Chí Minh"
entities = NER.extract(text)
print(entities)


# Ví dụ extract relation or ontology mapping:

class RelationExtraction:
    @staticmethod
    def mapping(input_entities: [BaseEntity]):
        for src_entity in input_entities:
            for dst_entity in input_entities:
                # Giả định các phần tử trong câu nói về 1 thực thể => gán hết attribute cho thực thể đó theo ontology
                # không quan tâm relation
                success = src_entity.add_attribute(dst_entity)
                print(f"ORIGINAL ENTITY: {src_entity}")
                if success:
                    print(f"MAPPED ENTITY: {src_entity}")
                print("++++++++++++++++++++++++++++++++++++++++")


RelationExtraction.mapping(entities)
