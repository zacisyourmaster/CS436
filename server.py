from socket import *
import pickle


# User class
class User:
    def __init__(self, username, password, balance=10):
        self.username = username
        self.password = password
        self.balance = balance


# Define Transaction as a named tuple
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


users = {
    "A": User("A", "A"),
    "B": User("B", "B"),
    "C": User("C", "C"),
    "D": User("D", "D"),
}
transactions = []


# Authentication
def authenticate(username, password):
    if username in users:
        user = users[username]

        if user.password == password:
            print(f"User {username} Authenticated")

            return True, list_transactions(username)

    print("User Authentication Failed")
    return False, None


# List Transactions
def list_transactions(username):
    user_transactions = [
        tx
        for tx in transactions
        if tx.payer == username or username == tx.payee1 or tx.payee2 == username
    ]
    return users[username].balance, user_transactions


# Process transaction
def process_transaction(tx):
    current_user = users[tx.payer]
    if current_user.balance < tx.amount:
        return False, current_user.balance

    transactions.append(tx)

    current_user.balance -= tx.amount

    users[tx.payee1].balance += tx.payment1

    if tx.payee2 is not None:
        users[tx.payee2].balance += tx.payment2

    return True, current_user.balance


def initialize():
    serverPort = 12000
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(("", serverPort))
    print("The server is ready to receive")
    return serverPort, serverSocket


def main():

    serverPort, serverSocket = initialize()
    while 1:
        data, clientAddress = serverSocket.recvfrom(2048)
        message = data.decode()
        fields = message.split(",")
        command = fields[0]
        if command == "LOGIN":
            username, password = fields[1], fields[2]
            print(f"Received an authentication request from user {username}")
            response = authenticate(username, password)

            if response[0]:  # If authentication is successful
                print(f"User {username} is authenticated")
            else:
                print(f"User {username} authentication failed")
        elif command == "TX":
            tx = Transaction(
                tx_id=int(fields[1]),
                payer=fields[2],
                amount=int(fields[3]),
                payee1=fields[4],
                payment1=int(fields[5]),
                payee2=fields[6] if fields[6] != "None" else None,
                payment2=int(fields[7]) if fields[7] != "None" else None,
            )
            print(f"Received Transaction Request from user {tx.payer}")
            response = process_transaction(tx)

            if response[0]:  # If transaction is successful
                print(f"Confirmed a transaction for user {tx.payer}")
            else:
                print(f"Transaction for user {tx.payer} failed")
        elif command == "LIST":
            username = fields[1]
            print(f"Received List Request from user {username}")
            response = list_transactions(username)
            print(f"Sent the list of transactions to user {username}")

        # serverSocket.sendto(response.encode(), clientAddress)
        serverSocket.sendto(pickle.dumps(response), clientAddress)


if __name__ == "__main__":
    main()
