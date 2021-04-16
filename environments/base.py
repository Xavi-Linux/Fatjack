from .blackjack import HitStand


def make(environment_name):
    if environment_name == 'hitstand':
        return HitStand()

    return None
