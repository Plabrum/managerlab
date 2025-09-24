from sqids import Sqids

_sqids = Sqids(min_length=8)


class Sqid(str):
    """A public ID string encoded via Sqids."""

    pass


def encode_sqid(value: int) -> Sqid:
    return Sqid(_sqids.encode([value]))


def decode_sqid(value: Sqid) -> int:
    return _sqids.decode(value)[0]
