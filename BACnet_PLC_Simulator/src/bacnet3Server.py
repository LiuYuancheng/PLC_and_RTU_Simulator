import asyncio
from bacpypes3.app import Application
from bacpypes3.object import DeviceObject, AnalogValueObject, BinaryValueObject
from bacpypes3.pdu import Address


async def main():
    # --------------------------------------------------
    # Device Object
    # --------------------------------------------------
    device = DeviceObject(
        objectIdentifier=("device", 1234),
        objectName="BACpypes3-Test-Server",
        vendorIdentifier=999,   # ✅ correct BACnet property
    )

    # --------------------------------------------------
    # BACnet Objects
    # --------------------------------------------------
    av1 = AnalogValueObject(
        objectIdentifier=("analogValue", 1),
        objectName="Temperature",
        presentValue=22.5,
        units="degreesCelsius",
    )

    bv1 = BinaryValueObject(
        objectIdentifier=("binaryValue", 1),
        objectName="PumpEnable",
        presentValue="inactive",
    )

    # --------------------------------------------------
    # Application (IMPORTANT FIX)
    # --------------------------------------------------
    app = Application(
        device=device,
        localAddress=Address("0.0.0.0:47808"),
    )

    app.add_object(av1)
    app.add_object(bv1)

    print("BACnet Server running")
    print("  Device ID:", device.objectIdentifier)

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
