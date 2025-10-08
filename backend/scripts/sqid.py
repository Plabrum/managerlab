#!/usr/bin/env python3
import sys
import sqids

sqid_encoder = sqids.Sqids(alphabet="abcdefghijklmnopqrstuvwxyz", min_length=8)


def sqid_decode(value: str) -> int:
    decoded = sqid_encoder.decode(value)
    if not decoded:
        raise ValueError(f"Invalid SQID: {value}")
    return decoded[0]


def sqid_encode(value: int) -> str:
    return sqid_encoder.encode([value])


def main():
    if len(sys.argv) != 2:
        print("Usage: sqid <id or sqid>")
        sys.exit(1)

    arg = sys.argv[1]

    # Try to detect if it's numeric or encoded
    try:
        value = int(arg)
        print(sqid_encode(value))
    except ValueError:
        # Not an int, so try decoding
        try:
            print(sqid_decode(arg))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
