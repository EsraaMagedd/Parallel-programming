import queue
import streamlit as st
import multiprocessing
import threading
import time
from queue import Empty


### parallel execution
def withdraw_amount(output_queue, balance, amount):
    output_queue.put(f"Withdrawal of ${amount} started")
    time.sleep(3)
    balance.value -= amount
    output_queue.put(f"Withdrawal of ${amount} completed. Updated Balance: ${balance.value}")


def deposit_amount(output_queue, balance, amount):
    output_queue.put(f"Deposit of ${amount} started")
    time.sleep(2)
    balance.value += amount
    output_queue.put(f"Deposit of ${amount} completed. Updated Balance: ${balance.value}")


def transfer_amount(output_queue, balance, amount):
    output_queue.put(f"Transfer of ${amount} started")
    time.sleep(4)
    balance.value -= amount  # Assuming transfer is a withdrawal
    output_queue.put(f"Transfer of ${amount} completed. Updated Balance: ${balance.value}")


def loan_amount(output_queue, balance, amount):
    output_queue.put(f"Loan application for ${amount} started")
    time.sleep(1)
    balance.value += amount
    output_queue.put(f"Loan application for ${amount} completed. Updated Balance: ${balance.value}")


def view_balance(output_queue, balance):
    output_queue.put(f"View Balance. Current Balance: ${balance.value}")


def run_parallel_processes(num_processes, functions_to_run, output_queue, balance):
    processes = []
    function_map = {
        1: withdraw_amount,
        2: deposit_amount,
        3: transfer_amount,
        4: loan_amount,
        5: view_balance,
    }
    amounts = []  # Store amounts for each function
    for function_id in functions_to_run:
        if function_id in function_map:
            amount = 0
            if function_id != 5:
                amount = st.number_input(f"Enter the amount for Operation {function_map[function_id].__name__}:",
                                         min_value=1, value=1, step=1)
                amounts.append(amount)
                process = multiprocessing.Process(target=function_map[function_id],
                                                  args=(output_queue, balance, amount))
            else:
                amounts.append(0)  # View Balance doesn't require an amount
                process = multiprocessing.Process(target=function_map[function_id], args=(output_queue, balance))

            processes.append(process)
        else:
            output_queue.put(f"Invalid function number: {function_id}")

    # Display the button after inputting amounts
    if st.button("Execute Processes"):
        # Start processes
        for process in processes:
            process.start()

        # Wait for processes to finish
        for process in processes:
            process.join()

        # Check if there are additional messages in the queue
        try:
            while True:
                output = output_queue.get_nowait()
                st.write(output)
        except Empty:
            pass

        # Display success message
        st.success("All processes completed")


def run_parallel_threads(num_threads, functions_to_run, output_queue, balance):
    lock = threading.Lock()

    threads = []
    function_map = {
        1: withdraw_with_lock,
        2: deposit_with_lock,
    }

    for function_id, amount in functions_to_run:
        if function_id in function_map:
            thread = threading.Thread(target=function_map[function_id], args=(output_queue, balance, amount, lock))
            threads.append(thread)
        else:
            output_queue.put(f"Invalid function number: {function_id}")

    if st.button("Execute Threads"):
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        # Check if there are additional messages in the queue
        try:
            while True:
                output = output_queue.get_nowait()
                st.write(output)
        except queue.Empty:
            pass

        st.success("All threads started")


### Synchronization
#multiprocessing
def withdraw_with_lock(output_queue, balance, lock, amount):
    with lock:
        current_balance = balance.value
        output_queue.put(f"Withdrawal of ${str(amount)} started")
        time.sleep(3)
        current_balance -= amount
        balance.value = current_balance
        output_queue.put(f"Withdrawal of ${str(amount)} completed. Updated Balance: ${balance.value}")


def deposit_with_lock(output_queue, balance, lock, amount):
    with lock:
        current_balance = balance.value
        output_queue.put(f"Deposit of ${str(amount)} started")
        time.sleep(2)
        current_balance += amount
        balance.value = current_balance
        output_queue.put(f"Deposit of ${str(amount)} completed. Updated Balance: ${balance.value}")
#threading

def thread_withdraw_with_lock(output_queue, balance, lock, amount):
    with lock:
        current_balance = balance
        output_queue.put(f"Withdrawal of ${str(amount)} started")
        time.sleep(3)
        current_balance -= amount
        balance = current_balance
        output_queue.put(f"Withdrawal of ${str(amount)} completed. Updated Balance: ${str(balance)}")

def thread_deposit_with_lock(output_queue, balance, lock, amount):
    with lock:
        current_balance = balance
        output_queue.put(f"Deposit of ${str(amount)} started")
        time.sleep(2)
        current_balance += amount
        balance = current_balance
        output_queue.put(f"Deposit of ${str(amount)} completed. Updated Balance: ${str(balance)}")


### server process
def run_server_processes(processes, output_queue, balance, result_list):
    st.write(result_list)
    st.success("All processes completed")


def deposit(balance, result_list, deposit_amount):
    current_balance = balance.value
    current_balance += deposit_amount
    balance.value = current_balance
    result_list.append({'action': 'deposit', 'amount': deposit_amount, 'balance': balance.value})


def print_balance(balance, result_list):
    result_list.append({'balance': balance.value})
    st.write(f"Current Balance: {balance.value}")


### pipe

def deposit_and_check_balance(conn, result_list, deposit_amount):
    current_balance = conn.recv()
    current_balance += deposit_amount
    conn.send(current_balance)
    result_list.append({'Note': 'Please be informed that a deposit operation is being performed on your account.',
                        'Deposit Amount': deposit_amount})


def initialize_balance(conn, result_list):
    initial_balance = 1000.0  # Initial balance for the bank account
    conn.send(initial_balance)
    result_list.append({'balance': initial_balance})


def print_balance_ui(balance):
    st.write(f"Current Balance: {balance}")


# Modify the print_balance function to update the UI within the main process
def print_balance(conn, result_list):
    try:
        while True:
            if conn.poll(timeout=1):  # Check if there is data in the pipe (non-blocking)
                current_balance = conn.recv()
                if current_balance == "END":
                    break
                result_list.append({'balance': current_balance})
                print_balance_ui(current_balance)
    except (EOFError, KeyboardInterrupt):
        pass

    # Send a termination signal to the main process
    conn.send("END")


# Modify the run_processes function to remove the st.write calls
def run_processes(processes, result_list, balance):
    try:
        while processes:
            output = result_list.pop(0)
    except IndexError:
        pass

    st.success("All processes completed")


### queue
def deposit_to_account(user_balance, deposit_amount, output_queue):
    updated_balance = user_balance + deposit_amount
    output_queue.put(updated_balance)


def withdraw_to_account(user_balance, withdraw_amount, output_queue):
    updated_balance = user_balance - withdraw_amount
    output_queue.put(updated_balance)


if __name__ == "__main__":
    st.title("Welcome to our Banking System")
    st.write("Welcome to our Banking System, where your financial journey begins and your aspirations thrive! "
             "We are delighted to have you as a valued member. Our commitment is to"
             " provide you with seamless and innovative financial operations tailored "
             "to meet your unique needs. Thank you for choosing us.")
    execution_mode = st.selectbox("Select the execution module you want to perform the tasks on:",
                                  ["multiprocessing", "threading"])

    function_map = {
        1: withdraw_amount,
        2: deposit_amount,
        3: transfer_amount,
        4: loan_amount,
        5: view_balance,
    }

    if execution_mode == "multiprocessing":
        synchronization = st.selectbox("Select the task you want to do:",
                                       ["Parallel Execution",
                                        "Sharing data between processes using Server process",
                                        "Communication between processes using Queue",
                                        "Communication between processes using Pipe",
                                        "Synchronization between processes and race condition problems"])
        if synchronization == "Parallel Execution":
            num_processes = st.number_input("Enter the number of operations to run in parallel:", min_value=1,
                                            max_value=5,
                                            value=1, step=1)

            functions_to_run = []
            st.write("Select operations to run in parallel:")
            for i in range(1, 6):
                if st.checkbox(f"perform: {function_map[i].__name__}", key=f"func_checkbox_{i}"):
                    functions_to_run.append(i)

            if len(functions_to_run) != num_processes:
                st.error("Error: The number of selected operations must match the total number of operations.")
            else:
                initial_balance = st.number_input("Enter the initial balance:", min_value=0, value=1000, step=1)
                with multiprocessing.Manager() as manager:
                    output_queue = manager.Queue()
                    balance = multiprocessing.Value('i', initial_balance)  # Initial user balance

                    # Run the parallel processes
                    run_parallel_processes(num_processes, functions_to_run, output_queue, balance)
        elif synchronization == "Sharing data between processes using Server process":
            with multiprocessing.Manager() as manager:
                initial_balance = st.number_input("Enter the initial balance:", min_value=0, value=1000, step=1)
                account_balance = manager.Value('d', initial_balance)
                result_list = manager.list()

                deposit_amount = st.number_input("Enter the deposit amount:",
                                                 value=0)  # User enters the deposit amount directly

                if st.button("Confirm Deposit"):
                    # Process 1: Deposit money into the account
                    p1 = multiprocessing.Process(target=deposit, args=(account_balance, result_list, deposit_amount))

                    # Process 2: Print the current balance
                    p2 = multiprocessing.Process(target=initialize_balance, args=(account_balance, result_list))

                    p1.start()
                    p2.start()

                    p1.join()
                    p2.join()

                    run_server_processes([p1, p2], None, account_balance, result_list)
        elif synchronization == "Communication between processes using Queue":
            q = multiprocessing.Queue()
            # Take user input for initial balance
            initial_balance = st.number_input("Enter the initial balance:", value=1000)
            user_balance = initial_balance
            st.write("\nChoose operation:")
            st.write("1. Deposit")
            st.write("2. Withdraw")

            choice = st.text_input("Enter your choice (1/2): ")

            if choice == '1':
                deposit_amount = st.number_input("Enter the deposit amount:", value=0)
                p = multiprocessing.Process(target=deposit_to_account, args=(user_balance, deposit_amount, q))
            elif choice == '2':
                withdraw_amount = st.number_input("Enter the withdrawal amount:", value=0)
                p = multiprocessing.Process(target=withdraw_to_account, args=(user_balance, withdraw_amount, q))
            else:
                st.write("Invalid choice. Please enter 1, 2, or 3.")
                p = multiprocessing.Process(target=withdraw_to_account, args=(user_balance, withdraw_amount, q))
            p.start()
            p.join()

            # Retrieve and update the balance for the next operation
            user_balance = q.get()

            st.write(f"Updated balance after the operation: {user_balance}")
        elif synchronization == "Communication between processes using Pipe":
            balance = 0
            with multiprocessing.Manager() as manager:
                result_list = manager.list()
                parent_conn, child_conn = multiprocessing.Pipe()

                deposit_amount = st.number_input("Enter the deposit amount:",
                                                 value=0)  # User enters the deposit amount directly

                p0 = multiprocessing.Process(target=initialize_balance, args=(parent_conn, result_list))
                p1 = multiprocessing.Process(target=deposit_and_check_balance,
                                             args=(parent_conn, result_list, deposit_amount))
                p2 = multiprocessing.Process(target=print_balance, args=(parent_conn, result_list))

                processes = [p0, p1, p2]

                if st.button("Execute Processes"):
                    # Start processes
                    for process in reversed(processes):
                        process.start()

                    # Wait for processes to finish
                    for process in reversed(processes):
                        process.join()

                    st.success("All processes completed")
        elif synchronization == "Synchronization between processes and race condition problems":
            lock = multiprocessing.Lock()

            # Get initial balance from the user
            initial_balance = st.number_input("Enter the initial balance:", min_value=0, value=1000, step=1)

            # Initialize multiprocessing manager, output queue, and balance
            with multiprocessing.Manager() as manager:
                output_queue = manager.Queue()
                balance = multiprocessing.Value('i', initial_balance)  # Initial user balance

                # Run two withdrawal threads with lock
                withdraw_processes = []
                for _ in range(2):
                    withdraw = multiprocessing.Process(target=withdraw_with_lock, args=(output_queue, balance, lock, 1))
                    withdraw_processes.append(withdraw)
                    withdraw.start()

                # Run two deposit threads with lock
                deposit_processes = []
                for _ in range(2):
                    deposit = multiprocessing.Process(target=deposit_with_lock, args=(output_queue, balance, lock, 1))
                    deposit_processes.append(deposit)
                    deposit.start()

                # Wait for all withdrawal threads to finish
                for withdraw_thread in withdraw_processes:
                    withdraw_thread.join()

                # Wait for all deposit threads to finish
                for deposit_thread in deposit_processes:
                    deposit_thread.join()

                # Check if there are additional messages in the queue
                try:
                    while True:
                        output = output_queue.get_nowait()
                        st.write(output)
                except queue.Empty:
                    pass

                # Display the final balance to the user
                st.success(f"The final balance after performing the operations: ${balance.value}")


    else:
        synchronization = st.selectbox("Select the operation you want to do:",
                                       ["Parallel Execution",
                                        "Synchronization between threads and race condition problems"])
        if synchronization == "Parallel Execution":
            num_processes = st.number_input("Enter the number of threads to run in parallel:", min_value=1,
                                            max_value=5,
                                            value=1, step=1)
            functions_to_run = []
            st.write("Select functions to run:")
            for i in range(1, 6):
                if st.checkbox(f"Function {i}: {function_map[i].__name__}", key=f"func_checkbox_{i}"):
                    functions_to_run.append(i)

            if len(functions_to_run) != num_processes:
                st.error("Error: The number of selected operations must match the number of threads.")
            else:
                initial_balance = st.number_input("Enter the initial balance:", min_value=0, value=1000, step=1)
                with multiprocessing.Manager() as manager:
                    output_queue = manager.Queue()
                    balance = multiprocessing.Value('i', initial_balance)  # Initial user balance
                    processes_output = []
                    # Run the parallel processes
                    run_parallel_threads(num_processes, functions_to_run, output_queue, balance)
                    # Retrieve outputs from the queue
                    while not output_queue.empty():
                        output = output_queue.get()
                        processes_output.append(output)
                        st.write(output)
        else:
            lock = threading.Lock()
            output_queue = queue.Queue()

            initial_balance = st.number_input("Enter the initial balance:", min_value=0, value=1000, step=1)
            balance = initial_balance

            output_queue = queue.Queue()

            withdraw_threads = []
            for _ in range(2):
                withdraw = threading.Thread(target=thread_withdraw_with_lock, args=(output_queue, balance, lock, 1))
                withdraw_threads.append(withdraw)
                withdraw.start()

            deposit_threads = []
            for _ in range(2):
                deposit = threading.Thread(target=thread_deposit_with_lock, args=(output_queue, balance, lock, 1))
                deposit_threads.append(deposit)
                deposit.start()


            # Wait for all withdrawal threads to finish
            for withdraw_thread in withdraw_threads:
                withdraw_thread.join()

            # Wait for all deposit threads to finish
            for deposit_thread in deposit_threads:
                deposit_thread.join()

            # Check if there are additional messages in the queue
            try:
                while not output_queue.empty():
                    output = output_queue.get_nowait()
                    st.write(output)
            except queue.Empty:
                pass
            # Display the final balance to the user
            st.success(f"The final balance after performing the operations: {balance}")
