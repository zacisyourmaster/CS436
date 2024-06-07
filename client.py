from socket import *
from prettytable import PrettyTable
import pickle


class Client:
    def __init__(self, username="", balance=0, transaction_list=[]) -> None:
        self.username = username
        self.balance = balance
        self.transaction_list = transaction_list


class Transaction:
    def __init__(
        self,
        status=1,
        tx_id=None,
        payer=None,
        amount=None,
        payee1=None,
        payment1=None,
        payee2=None,
        payment2=None,
    ):
        self.status = status
        self.tx_id = tx_id
        self.payer = payer
        self.amount = amount
        self.payee1 = payee1
        self.payment1 = payment1
        self.payee2 = payee2
        self.payment2 = payment2

    def update_status(self, new_status):
        self.status = new_status


serverName = "localhost"
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)


def send(message):
    try:
        clientSocket.sendto(message.encode(), (serverName, serverPort))
        return True
    except Exception as e:
        print("Message not Sent")
        print("Exception:", e)
        return False


def login(client):
    print("Welcome to your Bitcoin Wallet. Log In Below.")
    while True:
        username = input("Username: ")
        password = input("Password: ")
        command = "LOGIN"
        message = command + "," + username + "," + password
        send(message)
        data, serverAddress = clientSocket.recvfrom(2048)
        response = pickle.loads(data)
        # response = ast.literal_eval(data.decode())r
        if response[0]:  # If authentication is successful
            client.username = username
            client.balance = response[1][0]  # Get user balance
            client.transaction_list = response[1][1]  # Get user transactions
            print("")
            print("Balance: ", client.balance)
            return True
        print("User authentication failed.")
        user_choice = input("Enter 1 to try again, or 2 to quit: ")
        if user_choice == "2":
            return False  # Return False if user chooses to quit


def make_transaction(client):
    users = ["A", "B", "C", "D"]
    tx = Transaction()
    tx.payer = client.username

    while True:
        try:
            tx.amount = int(input("How Much do you Transfer? "))
            break
        except ValueError:
            print("Please enter a valid integer.")

    possible_payees = [user for user in users if user != tx.payer]

    tx.payee1 = input(f"Who will be Payee1? {possible_payees}\n")

    while True:
        while True:
            try:
                tx.payment1 = int(input("How Much Will Payee1 Receive? "))
                break
            except ValueError:
                print("Please enter a valid integer.")
        if tx.payment1 <= tx.amount:
            break
        print(f"Please Enter Value Less Than or Equal to {tx.amount}BTC")

    if tx.payment1 < tx.amount:
        possible_payees.remove(tx.payee1)
        tx.payee2 = input(f"Who will be Payee2 {possible_payees}\n")
        tx.payment2 = tx.amount - tx.payment1
        print(f"{tx.payee2} will receive: {tx.payment2}BTC")

    # find id
    user_txs = [
        tx.tx_id for tx in client.transaction_list if tx.payer == client.username
    ]
    if user_txs:
        highest_tx_id = max(user_txs)
        new_tx_id = highest_tx_id + 1
    else:
        new_tx_id = {"A": 100, "B": 200, "C": 300, "D": 400}[client.username]

    tx.tx_id = new_tx_id
    client.transaction_list.append(tx)

    message = f"TX,{tx.tx_id},{tx.payer},{tx.amount},{tx.payee1},{tx.payment1},{tx.payee2},{tx.payment2}"
    send(message)

    data, serverAddress = clientSocket.recvfrom(2048)
    response = pickle.loads(data)

    print()
    if response[0] == False:
        print("Transaction was Rejected")
        tx.status = 2
    else:
        print("Transaction Confirmed")
        tx.status = 3
        client.balance = response[1]


def display_transactions(tx_list):
    table = PrettyTable(
        [
            "Transaction ID",
            "Payer",
            "Amount",
            "Payee 1",
            "Payment 1",
            "Payee 2",
            "Payment 2",
        ]
    )

    for tx in tx_list:
        table.add_row(
            [
                tx.tx_id,
                tx.payer,
                tx.amount,
                tx.payee1,
                tx.payment1,
                tx.payee2,
                tx.payment2,
            ]
        )

    print(table)


if __name__ == "__main__":
    client = Client()
    if not login(client):
        exit()

    if client.transaction_list:
        display_transactions(client.transaction_list)
    else:
        print("No transactions available.")

    while True:
        # main menu
        print("+----------------- Main Menu ---------------------+")
        print("| 1. Make a Transaction                           |")
        print("| 2. Fetch and Display the List of Transactions   |")
        print("| 3. Quit                                         |")
        print("+-------------------------------------------------+")
        choice = input("Enter: ")

        if choice == "1":
            make_transaction(client)
            print()
        elif choice == "2":
            if client.transaction_list:
                message = f"LIST,{client.username}"
                send(message)

                data, serverAddress = clientSocket.recvfrom(2048)
                response = pickle.loads(data)
                client.balance, transactions = response[0], response[1]

                existing_ids = {tx.tx_id for tx in client.transaction_list}

                client.transaction_list.extend(
                    tx for tx in transactions if tx.tx_id not in existing_ids
                )

                print(f"Balance: {client.balance}")
                display_transactions(client.transaction_list)
            else:
                print("No transactions available.")

        elif choice == "3":
            break

    clientSocket.close()
