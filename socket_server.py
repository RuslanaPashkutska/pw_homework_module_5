import socket
import asyncio
from datetime import datetime


from aiofile import AIOFile
from aiopath import AsyncPath

from main import get_rates

LOG_FILE = AsyncPath("exchange.log")

async def log_command(message: str, client_address: tuple):
    async with AIOFile(LOG_FILE, "a") as af:
        log_line = f"{datetime.now().isoformat()} - {client_address} - {message}\n"
        await af.write(log_line)

async def handler_exchange_command(message: str) -> str:
    parts = message.strip().split()
    days = 1

    if len(parts) > 1:
        try:
            days = int(parts[1])
        except ValueError:
            return "Invalid number format."
        if not (1 <= days <=10):
            return "Number of days must be between 1 and 10."
        try:
            results = await get_rates(days, ["USD", "EUR"])
        except Exception as e:
            return f"Error fetching exchange rates: {e}"

        response_lines = []
        for entry in results:
            for date, currencies in entry.items():
                currencies_line = ", ".join(
                    [f"{cur}: sale={info['sale']} / purchase={info['purchase']}" for cur, info in currencies.items()]
                )
                response_lines.append(f"{date}: {currencies_line}")
            return "\n".join(response_lines)

async def main():
    host = socket.gethostname()
    port = 5001
    print(f"Server started on {host}:{port}")

    loop = asyncio.get_event_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    sock.setblocking(False)

    while True:
        try:
            data, client_addr = await loop.sock_recvfrom(sock, 1024)
            message = data.decode().strip()
            print(f"Received from {client_addr}: {message}")

            if message.startswith("exchange"):
                await log_command(message, client_addr)
                response = await handler_exchange_command(message)
            else:
                response = f"Unknown command: {message}"

            await loop.sock_sendto(sock, response.encode(), client_addr)

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())




