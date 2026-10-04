"""Single-instance lock: hold a bound localhost TCP port for the life of the process."""
import socket

PORT = 52345


def acquire_instance_lock(port: int = PORT):
    """The bound socket (keep it referenced while running), or None if another instance holds the port."""
    s = socket.socket()
    # On Windows SO_REUSEADDR lets a second process bind the same port (the lock would never fail); use the exclusive flag.
    s.setsockopt(socket.SOL_SOCKET, getattr(socket, "SO_EXCLUSIVEADDRUSE", socket.SO_REUSEADDR), 1)
    try:
        s.bind(("127.0.0.1", port))
        s.listen(1)
        return s
    except OSError:
        s.close()
