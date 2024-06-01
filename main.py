import pickle
from collections import UserDict
from datetime import datetime, timedelta
import re

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if self.validate(value):
            super().__init__(value)
        else:
            raise ValueError("Invalid phone number. It must contain exactly 10 digits.")

    @staticmethod
    def validate(value):
        return bool(re.fullmatch(r"\d{10}", value))

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        if not Phone.validate(new_phone):
            raise ValueError("Invalid phone number. It must contain exactly 10 digits.")
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", Birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today()
        next_week = today + timedelta(days=7)
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday_date = record.birthday.value.replace(year=today.year)
                if birthday_date < today:
                    birthday_date = birthday_date.replace(year=today.year + 1)
                if today <= birthday_date <= next_week:
                    upcoming_birthdays.append((record.name.value, record.birthday))
        return upcoming_birthdays

def input_error(func):
    def wrapper(args, book):
        try:
            return func(args, book)
        except ValueError as e:
            print(e)
        except IndexError:
            print("Invalid number of arguments.")
        except KeyError:
            print("Invalid key.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    return wrapper

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise IndexError("Invalid number of arguments for 'add-birthday' command. Usage: add-birthday [ім'я] [дата народження]")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        print(f"Birthday added for {name}.")
    else:
        print(f"Contact '{name}' not found.")

@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise IndexError("Invalid number of arguments for 'show-birthday' command. Usage: show-birthday [ім'я]")
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        print(f"Birthday for {name}: {record.birthday.value.strftime('%d.%m.%Y')}")
    else:
        print(f"Birthday for contact '{name}' not found.")

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        print("Upcoming birthdays:")
        for name, birthday in upcoming_birthdays:
            print(f"{name}: {birthday.value.strftime('%d.%m.%Y')}")
    else:
        print("No upcoming birthdays.")

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            print("No command entered. Please try again.")
            continue

        command, *args = user_input.split()

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            try:
                if len(args) < 2:
                    raise IndexError("Invalid number of arguments for 'add' command. Usage: add [ім'я] [телефон]")
                name, *phones = args
                record = book.find(name)
                if record:
                    for phone in phones:
                        record.add_phone(phone)
                    print(f"Added phone(s) for existing contact '{name}'.")
                else:
                    new_record = Record(name)
                    for phone in phones:
                        new_record.add_phone(phone)
                    book.add_record(new_record)
                    print(f"New contact '{name}' added with phone(s).")
            except ValueError as e:
                print(e)
            except IndexError as e:
                print(e)

        elif command == "change":
            try:
                if len(args) != 2:
                    raise IndexError("Invalid number of arguments for 'change' command. Usage: change [ім'я] [новий телефон]")
                name, new_phone = args
                record = book.find(name)
                if record:
                    old_phones = [phone.value for phone in record.phones]
                    if old_phones:
                        record.edit_phone(old_phones[0], new_phone)
                        print(f"Phone number changed for contact '{name}'.")
                    else:
                        print(f"No phone numbers found for {name}.")
                else:
                    print(f"Contact '{name}' not found.")
            except ValueError as e:
                print(e)
            except IndexError as e:
                print(e)

        elif command == "phone":
            if len(args) != 1:
                print("Invalid number of arguments for 'phone' command. Usage: phone [ім'я]")
            else:
                name = args[0]
                record = book.find(name)
                if record:
                    if record.phones:
                        print(f"Phone(s) for {name}: {', '.join(str(phone) for phone in record.phones)}")
                    else:
                        print(f"No phone numbers found for {name}.")
                else:
                    print(f"Contact '{name}' not found.")

        elif command == "all":
            if book.data:
                print("All contacts:")
                for record in book.data.values():
                    print(record)
            else:
                print("No contacts found.")

        elif command == "add-birthday":
            add_birthday(args, book)

        elif command == "show-birthday":
            show_birthday(args, book)

        elif command == "birthdays":
            birthdays(args, book)

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
