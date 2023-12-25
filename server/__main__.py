import asyncio
import asyncio_dgram

import render_letters

async def udp_server():
    stream = await asyncio_dgram.bind(("0.0.0.0", 8888))
    print(f"Started listening on {stream.sockname}")
    try:
        print_str = ""
        while True:
            data, _ = await stream.recv()
            if len(data) < 420:
                print(f"Messaged received only {len(data)} bytes long")
                continue
            message = data[419:420].decode()
            print(f"Data received: {message}")
            if message == '@':
                render_letters.render_str(print_str)
                print_str = ""
                continue
            elif message == '+':
                print_str += " "
            elif message == '-':
                if len(print_str)>0:
                    print_str = print_str[:-1]
            else:
                print_str += message
            print(f'Current string: {print_str}')
    finally:
        stream.close()

def main():
    asyncio.run(udp_server())

if __name__ == "__main__":
    main()