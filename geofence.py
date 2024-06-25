
class GeoFence:
    name = ''
    TopLong = 0
    TopLat = 0
    BotLong = 0
    BotLat = 0

    def __init__(self, name, TopLong, TopLat, BotLong, BotLat) -> None:
        self.name = name
        self.TopLong = float(TopLong)
        self.TopLat = float(TopLat)
        self.BotLong = float(BotLong)
        self.BotLat = float(BotLat)

