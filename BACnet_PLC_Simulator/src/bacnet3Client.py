import asyncio
from bacpypes3.app import Application
from bacpypes3.object import DeviceObject
from bacpypes3.pdu import Address
from bacpypes3.primitivedata import Real, Enumerated, ObjectIdentifier


async def main():
    device = DeviceObject(
        objectIdentifier=("device", 5678),
        objectName="BACpypes3-Test-Client",
        vendorIdentifier=999,
    )

    # ✅ MUST be SimpleApplication
    app = Application(
        device=device,
        localAddress=Address("0.0.0.0:40809"),
    )

    server = Address("127.0.0.1:40808")

    av1 = ObjectIdentifier(("analogValue", 1))
    bv1 = ObjectIdentifier(("binaryValue", 1))

    value = await app.read_property(server, av1, "presentValue")
    print("Read Temperature:", value)

    await app.write_property(server, av1, "presentValue", Real(26.8))
    print("Wrote Temperature")

    value = await app.read_property(server, av1, "presentValue")
    print("Read Temperature After Write:", value)

    value = await app.read_property(server, bv1, "presentValue")
    print("Read PumpEnable:", value)

    await app.write_property(server, bv1, "presentValue", Enumerated(1))
    print("Wrote PumpEnable = active")

    value = await app.read_property(server, bv1, "presentValue")
    print("Read PumpEnable After Write:", value)


if __name__ == "__main__":
    asyncio.run(main())
