from collections import UserDict
from datetime import datetime, date
import pickle


def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except IndexError:
            return 'Not enough params. Try help'
        except ValueError:
            return 'Invalid value. Try again'
        except KeyError:
            return 'Contact not found. Try again'
    return inner


class Field:
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self) -> str:
        return str(self)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if not value.isdigit() or len(value) != 12:
            raise ValueError('Phone number must be a 12-digit number')
        self.__value = value


class Birthday(Field):
    def __init__(self, value=None):
        self.__value = None
        if value is not None:
            self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        try:
            self.__value = datetime.strptime(value, '%d-%m-%Y')
        except ValueError:
            raise ValueError('Birthday must be in "dd-mm-yyyy" format')

    def __str__(self):
        return self.__value.strftime('%d-%m-%Y')


class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.phones = [phone] if phone else None
        self.birthday = birthday

    def add_phone(self, phone):
        self.phones.append(phone)
        return f'Phone {phone} successfully added'

    def change_phone(self, index, phone):
        self.phones[index] = phone
        return f'Phone {phone} successfully changed'

    def delete_phone(self, phone):
        self.phones.remove(phone)

    def __str__(self) -> str:
        return f'{str(self.name)} {", ".join([str(p) for p in self.phones])} {str(self.birthday)}'

    def set_birthday(self, birthday):
        self.birthday = birthday

    def get_birthday(self, birthday):
        return self.birthday.value if self.birthday else None

    def days_to_bd(self):
        if not self.birthday:
            return None
        today = date.today()
        bd = self.birthday.value
        next_birthday = bd.replace(year=today.year).date()
        if next_birthday and next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
            if next_birthday.year - today.year > 1:
                return None
        if next_birthday:
            days_to_birthday = (next_birthday - today).days
            return days_to_birthday


class AddressBook(UserDict):
    start_iterate = 0

    def add_record(self, record):
        name = record.name.value
        self.data[name] = record

    def iterator(self, page=2):
        while True:
            if self.start_iterate >= len(self.data):
                break

            yield list(self.data.values())[self.start_iterate:self.start_iterate + page]
            self.start_iterate += page

    def show_all(self):
        result = []
        for record_batch in self.iterator():
            for record in record_batch:
                result.append(str(record))
        return '\n'.join(result)
    
    def search(self, query):
        result = []
        for record in self.data.values():
            if query.lower() in record.name.value.lower() or any(query in phone.value for phone in record.phones):
                result.append(str(record))
        return '\n'.join(result)
    
    def save(self, file_name):
        file_name = 'data.bin'

        with open(file_name, "wb") as fh:
            pickle.dump(self.data, fh)

        print('Your address book saved successfully')

    def load(self, file_name):
        with open(file_name, "rb") as fh:
            self.data = pickle.load(fh)
        print('Your address book load successfully')

contacts = AddressBook()


def help(*args):
    return '''
    "hello", відповідає у консоль "How can I help you?"

    "help" Викликає список доступних команд

    "add ...". За цією командою бот зберігає у пам'яті (у словнику наприклад) новий контакт. Замість ... 
користувач вводить ім'я та номер телефону, обов'язково через пробіл.

    "change..." За цією командою бот зберігає в пам'яті новий номер телефону існуючого контакту. Замість ...
 користувач вводить ім'я та індекс та новий номер телефону, обов'язково через пробіл.

    "phone ...." За цією командою бот виводить у консоль номер телефону для зазначеного контакту. Замість ... 
    користувач вводить ім'я контакту, чий номер треба показати.

    "daystobd ..." Повертає кількість днів до наступного дня народження контакту

    "show all". За цією командою бот виводить всі збереженні контакти з номерами телефонів у консоль.

    "search". Для пошуку за частковим співпадінням серед усіх існуючих контактів.

    "good bye", "close", "exit" по будь-якій з цих команд бот завершує свою роботу після того, як виведе у консоль "Good bye!".
    '''


def hello(*args):
    return '''How can I help you?'''


def exit(*args):
    return '''Good Bye'''


def no_command(*args):
    return '''Unknown command, try again'''


def show_all(*args):
    return contacts.show_all()

def search(*args):
    query = args[0]
    result = contacts.search(query)
    if result:
        return result
    return "No contacts found"


@input_error
def add(*args):
    name = Name(args[0])
    phone = Phone(args[1])
    birthday = Birthday(args[2])
    rec = contacts.get(str(name))
    if rec:
        return rec.add_phone(phone)
    record = Record(name, phone, birthday)
    contacts.add_record(record)
    days_to_bd = record.days_to_bd()
    if days_to_bd:
        print(f'{days_to_bd} days until next birthday')
    return f"Added <{name.value}> with phone <{phone.value}> and birthday <{str(birthday)}>"


@input_error
def phone(*args):
    name = Name(args[0])
    rec = contacts.get(name.value)
    if rec:
        return rec.phones
    return f'There are no phones with name {name}'


def change(*args):
    name = Name(args[0])
    index = int(args[1])
    new_phone = Phone(args[2])
    rec = contacts.get(str(name))
    if rec:
        return rec.change_phone(index, new_phone)
    return f'There are no phones with name {name}'


def days_to_bd(*args):
    name = Name(args[0])
    rec = contacts.get(str(name))
    if rec:
        return rec.days_to_bd()
    return f'There are no contacts with name {name}'


def save(*args):
    return contacts.save("data.bin")

def load(*args):
    return contacts.load("data.bin")


COMMANDS = {help: 'help',
            add: 'add',
            exit: ['exit', 'close', 'good bye'],
            hello: 'hello',
            phone: 'phone',
            change: 'change',
            show_all: 'show all',
            days_to_bd: 'days_to_bd',
            search: 'search',
            save: 'save',
            load: 'load'
            }


def command_handler(text):
    for command, kword in COMMANDS.items():
        if isinstance(kword, str):
            if text.lower().startswith(kword):
                return command, text.replace(kword, '').strip().split()
        elif isinstance(kword, list):
            if text.strip().lower() in kword:
                return command, []
    return no_command, None


def main():
    print(help())
    while True:
        user_input = input('>>>')
        command, data = command_handler(user_input)

        print(command(*data))

        if command == exit:
            break


if __name__ == '__main__':
    main()
