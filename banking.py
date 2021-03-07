# SIMPLE BANKING SYSTEM
# This procedure provides some options via console:
# - sign up (generating of card number and pin)
# - log in
# - check the balance
# - add income or transfer it to another account
# - close account
# - log out and exit
# ---------------------------------------------------
# 1) session starts always by printing the main menu
# 2) user may choose the option by entering the number of this option
# 3) user session ends when user input equals to 0
# 4) generated card numbers are verified by Luhn algorithm
# 5) cards' data is stored in a database (sqlite)
# ---------------------------------------------------

import random
import sqlite3

# menu constants
ACC_CREATE = '1. Create an account'
ACC_LOG_IN = '2. Log into account'
ACC_LOG_OUT = '5. Log out'
EXIT = '0. Exit'
BALANCE = '1. Balance'
INCOME = '2. Add income'
TRANSFER = '3. Do transfer'
ACC_CLOSE = '4. Close account'
IIN = '400000'


def main():
    # start user session
    session = True

    while session:
        menu = show_main_menu()
        if menu == 1:
            create_account()
            print()
        elif menu == 2:
            user_card = input('\nEnter your card number:\n')
            user_pin = input('Enter your PIN:\n')
            if user_card in get_cards() and user_pin in get_pins():
                print('\nYou have successfully logged in!')
                print()
                log_in = True
                while log_in:
                    user_menu = show_user_menu()
                    if user_menu == 1:
                        user_balance = check_balance(user_card)
                        print(f'\nBalance: {user_balance}')
                        print()
                    elif user_menu == 2:
                        add_income(user_card)
                    elif user_menu == 3:
                        check_transfer(user_card)
                    elif user_menu == 4:
                        delete_info(user_card)
                        log_in = False
                    elif user_menu == 5:
                        print('\nYou have successfully logged out!')
                        print()
                        log_in = False
                    elif user_menu == 0:
                        log_in = False
                        session = False
                        print('\nBye!')
                    else:
                        print('\nPlease, choose the number from 0 to 5')
            else:
                print('\nWrong card number or PIN!')
                print()
        elif menu == 0:
            print('\nBye!')
            session = False
        else:
            print('\nPlease, choose the number from 0 to 2')


# the function to add new data into the db
def add_info(card_number, pin_code):
    cursor.execute(f'''
        INSERT INTO card (number, pin)
        VALUES ({card_number}, {pin_code});
    ''')
    conn.commit()
    print('\nYour card has been created\n'
          f'Your card number:\n{card_number}\n'
          f'Your card PIN:\n{pin_code}')
    print()


# the function to delete account from db
def delete_info(card_number):
    cursor.execute(f'''
        DELETE FROM card
        WHERE number = {card_number};
    ''')
    conn.commit()
    print('\nThe account has been closed!')
    print()


# the function to check the balance of the card
def check_balance(card_number):
    cursor.execute(f'''
        SELECT balance
        FROM card
        WHERE number = {card_number};
    ''')
    return cursor.fetchone()[0]


# the function to get all the cards we store
def get_cards():
    cursor.execute('''
        SELECT number FROM card;
    ''')
    card_list = [card[0] for card in cursor.fetchall()]
    return card_list


# the function to get all the pin-codes we store
def get_pins():
    cursor.execute('''
        SELECT pin FROM card;
    ''')
    pin_list = [pin[0] for pin in cursor.fetchall()]
    return pin_list


# the function to add income to the db
def add_income(card_number):
    income_amt = int(input('\nEnter income:\n'))
    current_balance = check_balance(card_number)
    cursor.execute(f'''
        UPDATE card
        SET balance = {current_balance} + {income_amt}
        WHERE number = {card_number};
    ''')
    conn.commit()
    print('Income was added!')
    print()


# the function to validate a card for money transfer
def check_transfer(card_number):
    print('\nTransfer')
    receiver_card = input('Enter card number:\n')
    if receiver_card == card_number:
        print("You can't transfer money to the same account!")
        print()
    elif not check_luhn(receiver_card):
        print('Probably you made a mistake in the card number. Please try again!')
        print()
    elif receiver_card not in get_cards():
        print('Such a card does not exist.')
        print()
    else:
        transfer_amt = int(input('Enter how much money you want to transfer:\n'))
        if transfer_amt <= check_balance(card_number):
            cursor.execute(f'''
                UPDATE card
                SET balance = {check_balance(receiver_card)} + {transfer_amt}
                WHERE number = {receiver_card};
            ''')
            cursor.execute(f'''
                UPDATE card
                SET balance = {check_balance(card_number)} - {transfer_amt}
                WHERE number = {card_number};
            ''')
            conn.commit()
            print('Success!')
            print()
        else:
            print('Not enough money!')
            print()


# create a card with Luhn algorithm
def create_card():
    card = IIN + '{:09d}'.format(
        random.randrange(000000000, 999999999))
    digits_list = list(card)
    new_list = []
    for idx, digit in enumerate(digits_list):
        if not (idx and idx % 2):
            if int(digit) * 2 > 9:
                digit = int(digit) * 2 - 9
                new_list += [digit]
            else:
                digit = int(digit) * 2
                new_list += [digit]
        else:
            digit = int(digit)
            new_list += [digit]
    digits_sum = sum(new_list)
    if digits_sum % 10:
        checksum = 10 - (digits_sum % 10)
    else:
        checksum = 0
    return card + str(checksum)


# checking if the card number satisfies Luhn algorithm
def check_luhn(card_number):
    digits_list = list(card_number[:-1])
    new_list = []
    for idx, digit in enumerate(digits_list):
        if not (idx and idx % 2):
            if int(digit) * 2 > 9:
                digit = int(digit) * 2 - 9
                new_list += [digit]
            else:
                digit = int(digit) * 2
                new_list += [digit]
        else:
            digit = int(digit)
            new_list += [digit]
    digits_sum = sum(new_list)
    if digits_sum % 10:
        checksum = 10 - (digits_sum % 10)
    else:
        checksum = 0
    if checksum == int(card_number[-1:]):
        return True
    else:
        return False


# generate new account
def create_account():
    # generating a card number with verifying of Luhn alg
    card_num = create_card()
    # generating a random pin
    pin = '{:04d}'.format(random.randrange(0000, 9999))
    # add data to users dictionary and card table
    users_dict[card_num] = pin
    add_info(card_num, pin)


# shows the main menu
def show_main_menu():
    return int(input(f'{ACC_CREATE}\n{ACC_LOG_IN}\n{EXIT}\n'))


# shows user menu
def show_user_menu():
    return int(input(f'{BALANCE}\n{INCOME}\n{TRANSFER}\n'
                     f'{ACC_CLOSE}\n{ACC_LOG_OUT}\n{EXIT}\n'))


# main program
if __name__ == '__main__':
    # the dictionary to store accounts
    users_dict = {}

    # the connection to the database to store cards/pins
    conn = sqlite3.connect('card.s3db')
    cursor = conn.cursor()

    cursor.execute('''
                CREATE TABLE IF NOT EXISTS card (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    number TEXT,
                    pin TEXT,
                    balance INTEGER DEFAULT 0
                );
            ''')
    conn.commit()

    # start of the user session
    main()
