from itertools import product
from random import randint
from functools import reduce


class MinimumCashError(BaseException):

    def __init__(self, text):
        super().__init__(text)


class MinimumPlayersError(BaseException):

    def __init__(self, text):
        super().__init__(text)


class DeckNumberError(BaseException):

    def __init__(self, text):
        super().__init__(text)


class PlayerSetUpError(BaseException):

    def __init__(self, text):
        super().__init__(text)


class NumberPlayersError(BaseException):

    def __init__(self, text):
        super().__init__(text)


class MaxNumberPlayersError(BaseException):

    def __init__(self, text):
        super().__init__(text)


class MaxCashExceededError(BaseException):

    def __init__(self, text):
        super().__init__(text)


class NoBetsPlacedError(BaseException):

    def __init__(self, text):
        super().__init__(text)


class ComeAlivePlayerError(BaseException):

    def __init__(self, text):
        super().__init__(text)


class IllegalBetError(BaseException):

    def __init__(self, text):
        super().__init__(text)


class GameAlreadyStarted(BaseException):

    def __init__(self,text):
        super().__init__(text)


class Decks:

    __SUITS = ('D', 'C', 'H', 'S')
    __CARDS = ('A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K')

    def __init__(self,number=1):
        self.deck_cards = list(map(lambda t: [str(t[0])+str(t[1]),t[2]], product(self.__CARDS, self.__SUITS, [number])))

    @staticmethod
    def print__cards_ref():
        return 'D: Diamonds\nC: Clubs\nH: Hearts\nS: Spades'


class BlackjackDecks(Decks):

    __VALUES = {'A': [1, 11],
                 2: 2,
                 3: 3,
                 4: 4,
                 5: 5,
                 6: 6,
                 7: 7,
                 8: 8,
                 9: 9,
                 10: 10,
                'J': 10,
                'Q': 10,
                'K': 10
                }

    def __init__(self, number=1):
        super().__init__(number)

        self.decks = self.__build_initial_deck()

    def __build_initial_deck(self):
        decks = {}
        for i, card in enumerate(self.deck_cards):
            decks[i+1]= {'Name': card[0],
                         'Value': self.__num_value(card[0]) if self.__VALUES.get(card[0][0]) is None\
                                                            else self.__VALUES.get(card[0][0]),
                         'Available': card[1]
                         }

        return decks

    def __num_value(self, value):
        return self.__VALUES.get(int(value[:2])) if self.__VALUES.get(int(value[0])) is None\
                                                 else self.__VALUES.get(int(value[0]))

    def pick_random_card(self):
        card = self.decks[randint(1,52)]
        while card['Available'] == 0:
            card = self.decks[randint(1, 52)]

        card['Available'] = card['Available'] - 1
        return [card['Name'], card['Value']]

    def get_total_deck_value(self):
        return reduce(lambda a,b: a+b,
                      map(lambda v: v['Value'] * v['Available'] if isinstance(v['Value'], int) else max(v['Value']) * v['Available'],
                          self.decks.values())
                      )

    def __str__(self):
        return '{}'.format(self.decks)


class BlackjackPlayer:

    __MIN_CASH = 1000

    def __init__(self, name, initial_cash=10000, allow_debt=False):
        if initial_cash < self.__MIN_CASH:
            raise MinimumCashError('{0}! Initial credit must be equal or greater than €{1}'.format(name, self.__MIN_CASH))

        self.name = name
        self.cash = initial_cash
        self.gains = 0
        self.allow_debt = allow_debt
        self.alive = True
        self.current_bet = 0
        self.current_hand_alive = True
        self.current_hand = None

    def check_status(func):
        def wrapper(*args):
            if not args[0].alive:
                raise ComeAlivePlayerError('Player can no longer play this game')

            return func(*args)

        return wrapper

    def place_bet(self, amount):
        if amount > self.cash and not self.allow_debt:
            raise MaxCashExceededError('You do not have enough cash to place that bet')

        if amount <= 0:
            raise IllegalBetError('The amount must be greater than 0')

        self.current_bet += amount
        self.cash -= amount
        self.current_hand_alive = True

    @check_status
    def change_state(self, outcome):
        if outcome == 'simple_win':
            self.cash += self.current_bet * 2
            self.gains += self.current_bet
        elif outcome == 'draw':
            self.cash += self.current_bet
        elif outcome == 'defeat':
            self.gains -= self.current_bet
        elif outcome =='blackjack_win':
            self.cash += self.current_bet * 2.5
            self.gains += self.current_bet * 1.5

        self.current_bet = 0
        self.current_hand = None
        self.current_hand_alive = True
        if self.cash <= 0 and not self.allow_debt:
            self.kill()

    @check_status
    def kill(self):
        self.alive = False

    @check_status
    def receive_hand(self, hand):
        self.current_hand = hand

    @classmethod
    def build_instances(cls, players):
        instances = []
        for player in players:
            if not isinstance(player, dict):
                raise TypeError('List elements must be dictionaries')

            if player.get('name') is None or player.get('initial_cash') is None or player.get('allow_debt') is None:
                raise KeyError('Dictionary must contain the following keys: name, initial_cash and allow_debt')
            instances.append(cls(player['name'],player['initial_cash'], player['allow_debt']))

        return instances

    def __str__(self):
        cadena = '\n'
        for attr in filter(lambda a: not str(a).startswith('_'), dir(self)):
            if type(getattr(self,attr)).__name__ != 'method':
                cadena += '\t{0}: {1}\n'.format(attr,''if getattr(self,attr) is None else getattr(self,attr))

        return cadena


class Hand:

    def __init__(self, cards, croupier=False):
        if croupier:
            self.card_names = [cards[0]]
            self.card_values = [cards[1]]
        else:
            self.card_names = list(map(lambda l: l[0], cards))
            self.card_values = list(map(lambda l: l[1], cards))

        self.locked = False
        self.is_croupier = croupier
        self.__adjust_aces()

    @property
    def minvalue(self):
        return reduce(lambda a,b: a+b,
                      map(lambda v: v[0] if isinstance(v, list) else v, self.card_values))

    @property
    def maxvalue(self):
        return reduce(lambda a,b: a+b,
                      map(lambda v: v[1] if isinstance(v, list) else v, self.card_values))

    @property
    def is_blackjack(self):
        evaluation = len(self.card_names) == 2 and self.maxvalue == 21
        if evaluation:
            self.locked = True

        return evaluation

    @property
    def is_busted(self):
        evaluation = self.minvalue > 21
        if evaluation:
            self.locked = True

        return evaluation

    @property
    def is_over_17(self):
        evaluation = (17 <= self.maxvalue <= 21) or (self.minvalue >= 17)
        if evaluation:
            self.locked = True

        return evaluation

    def append_card(self, card):
        self.card_names.append(card[0])
        self.card_values.append(card[1])
        self.__adjust_aces()

    def __adjust_aces(self):
        j=0
        for i, name in enumerate(self.card_names):
            if name.startswith('A'):
                j+=1
                if j > 1:
                    self.card_values[i] = 1

    @property
    def best_value(self):
        if self.is_croupier:
            return self.maxvalue if self.maxvalue <= 21 else self.minvalue
        else:
            if not self.is_busted:
                if self.minvalue <= self.maxvalue <= 21:
                    return self.maxvalue

            return self.minvalue

    def __str__(self):
        return 'Cards: {0}\n Min. value: {1}\n Max. Value: {2}'.format(' '.join(self.card_names),
                                                                       self.minvalue,
                                                                       self.maxvalue)


class Blackjack:

    def __init__(self, decks=6, players=1):
        if players < 1:
            raise MinimumPlayersError('At least, one player is needed to launch the game')
        elif players > 5:
            raise MaxNumberPlayersError('Number of player cannot exceed 5')

        if decks == 6 or decks == 8:
            self.numdecks = decks
        else:
            raise DeckNumberError('Deck number must be either 6 or 8!')

        self.game_on = False
        self.numplayers = players
        self.players = None
        self.__deck = None
        self.alive_players = None
        self.croupier_hand = None

    def setup_players(self, players: list):
        if len(players) < self.numplayers:
            raise NumberPlayersError('Too many players have been set up')
        elif len(players) > self.numplayers:
            raise NumberPlayersError('Too few players have been set up')

        self.players = BlackjackPlayer.build_instances(players)
        self.alive_players = self.players

    def start(self):
        if self.players is None:
            raise PlayerSetUpError('Players must be set up before starting a game')

        if self.game_on:
            raise GameAlreadyStarted('Game has already been started. Do not call this method again')

        self.__deck = BlackjackDecks(self.numdecks)
        self.game_on = True

    def start_round(self):
        if any([player.current_bet == 0 for player in self.alive_players]):
            raise NoBetsPlacedError('Place bets before starting a new round')

        for player in self.alive_players:
            player.receive_hand(Hand([self.__deck.pick_random_card(), self.__deck.pick_random_card()]))
            self.croupier_hand = Hand(self.__deck.pick_random_card(), croupier=True)

    def retrieve_hands_alive(self):
        for player in filter(lambda p: p.current_hand_alive, self.alive_players):
            if player.current_hand.is_busted or player.current_hand.is_blackjack or player.current_hand.minvalue == 21 or \
                    player.current_hand.maxvalue == 21:
                player.current_hand_alive = False

        return list(filter(lambda p: p.current_hand_alive, self.alive_players))

    def send_action(self, player:BlackjackPlayer, action: str):
        if action.lower() == 'stand':
            player.current_hand_alive = False
        elif action.lower() == 'hit':
            player.current_hand.append_card(self.__deck.pick_random_card())

    def get_croupier_hand(self):
        while not self.croupier_hand.is_over_17:
            self.croupier_hand.append_card(self.__deck.pick_random_card())

        return self.croupier_hand

    def resolve_round(self, player):
        if player.current_hand.is_busted:
            player.change_state('defeat')
            return 'The House beats {0}'.format(player.name)

        if player.current_hand.is_blackjack and not self.croupier_hand.is_blackjack:
            player.change_state('blackjack_win')
            return 'Blackjack for {0}'.format(player.name)

        if not player.current_hand.is_busted and self.croupier_hand.is_busted:
            player.change_state('simple_win')
            return '{0} beats the House'.format(player.name)

        if player.current_hand.best_value > self.croupier_hand.best_value:
            player.change_state('simple_win')
            return '{0} beats the House'.format(player.name)

        if player.current_hand.best_value < self.croupier_hand.best_value:
            player.change_state('defeat')
            return 'The House beats {0}'.format(player.name)

        if (player.current_hand.best_value == self.croupier_hand.best_value) or (player.current_hand.is_blackjack
                                                                                 and self.croupier_hand.is_blackjack):
            player.change_state('draw')

            return 'DRAW'

    def assess_continuity(self):
        self.alive_players = list(filter(lambda player:player.alive, self.players))
        if not self.is_playable:
            self.game_on = False
            return 'Game over: no cards left to play'

        if not self.alive_players:
            self.game_on = False
            return 'Game over: No players left to play'

        self.croupier_hand = None
        return None

    @property
    def is_playable(self):
        return self.__deck.get_total_deck_value() > 21 * self.numplayers + 17

    def print_players_info(self):
        cadena = ''
        if self.players is not None:
            for n, player in enumerate(self.players):
                cadena += '\n---------Player{}---------\n'.format(n+1)
                cadena += str(player)

        return cadena

