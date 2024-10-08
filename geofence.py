
class GeoFence:
    def __init__(self, name, TopLong, TopLat, BotLong, BotLat, Email) -> None:
        self.name = name
        self.TopLong = float(TopLong)
        self.TopLat = float(TopLat)
        self.BotLong = float(BotLong)
        self.BotLat = float(BotLat)
        self.Email = Email
