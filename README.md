# Parallel-programming
Running bank system operations in parallel

 ## How to run
! Open the main.py file on a Python editor Pycharm is preferred
Type this command on the editor's local terminal: streamlit run main.py
! The app screens would be displayed 

### The project has five main functions:
1. Withdraw amount(output queue, balance, amount):
- Initiates a withdrawal operation with a specified amount.
- Simulates the withdrawal process with a sleep of 3 seconds.
- Updates the user's balance by deducting the withdrawal amount.
- Outputs messages indicating the start, completion, and updated balance to the output queue.

2. Deposit amount(output queue, balance, amount):
- Initiates a deposit operation with a specified amount.
- Simulates the deposit process with a sleep of 2 seconds.
- Updates the user's balance by adding the deposit amount.
- Outputs messages indicating the start, completion, and updated balance to the output queue.

3. Transfer amount(output queue, balance, amount):
- Initiates a transfer operation with a specified amount (treated as a withdrawal).
- Simulates the transfer process with a sleep of 4 seconds.
- Updates the user's balance by deducting the transfer amount.
- Outputs messages indicating the start, completion, and updated balance to the output queue.

4. Loan amount(output queue, balance, amount):
- Initiates a loan application with a specified amount.
- Simulates the loan application process with a sleep of 1 second.
- Updates the user's balance by adding the loan amount.
- Outputs messages indicating the start, completion, and updated balance to the output queue.

5. View balance(output queue, balance):
- Provides the user with the current balance information.
- Outputs a message indicating the current balance to the output queue.


### Depending on these five functions we are performing the following operations:
1. Parallel Execution: for executing these five functions in parallel using the multiprocessing module.
2. Sharing data between processes using Server process.
3. Communication between processes using Queue.
4. Communication between processes using Pipe.
5. Synchronization between threads and race condition problems
