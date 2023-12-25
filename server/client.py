import asyncio
import asyncio_dgram


async def udp_echo_client():
    stream = await asyncio_dgram.connect(("127.0.0.1", 8888))
    try:
        while True:
            str = ("!"*419)+input("Message: ")
            await stream.send(bytes(str, 'utf-8'))
    finally:
        stream.close()

def main():
    asyncio.run(udp_echo_client())

if __name__ == "__main__":
    main()