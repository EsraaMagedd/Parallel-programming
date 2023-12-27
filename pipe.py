import multiprocessing

def send_msgs(conn, msgs):
    for msg in msgs:
        conn.send(msg)
    conn.close()

def recv_msg(conn):
    while 1:
        msg = conn.recv()
        if msg == "END":
            break
        print(msg)

if __name__ == "__main__":

    msgs = ["Hello there", "You Have been transfered mony", "Amount transfered = 200", "END"]
    parent_conn, child_conn = multiprocessing.Pipe()
    p1 = multiprocessing.Process(target=send_msgs, args=(parent_conn, msgs))
    p2 = multiprocessing.Process(target=recv_msg, args=(child_conn,))
    p1.start()
    p2.start()

    p1.join()
    p2.join()