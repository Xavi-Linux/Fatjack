from games import blackjacks as game


def setup_game():
    game_error = True
    num_players = 0
    num_decks = 0
    while game_error:
        try:
            if num_players == 0:
                num_players = int(input('Please, crunch how many players want to play:'))
            if num_decks == 0:
                num_decks = int(input('Please, crunch how many decks you want to play with (6 or 8):'))
            match = game.Blackjack(num_decks, num_players)
            game_error = False
        except ValueError:
            print('ERROR-->', 'Input must be an integer')
        except game.MinimumPlayersError as ex:
            print('ERROR-->', ex)
            num_players = 0
        except game.MaxNumberPlayersError as ex:
            print('ERROR-->', ex)
            num_players = 0
        except game.DeckNumberError as ex:
            print('ERROR-->', ex)
            num_decks = 0
    return match


def players_features_list(n):
    players = []
    for i in range(1, n+1):

        players.append({'name': None,
                        'initial_cash': None,
                        'allow_debt': None
                        }
                       )

    return players


def place_bets(players):
    for player in players:
        error = True
        while error:
            try:
                money = int(input('Please,{}! Place your bet: '.format(player.name)))
                player.place_bet(money)
                error = False
            except ValueError:
                print('ERROR-->', 'Input must be an integer')
            except game.MaxCashExceededError as ex:
                print('ERROR-->', ex)
            except game.IllegalBetError as ex:
                print('ERROR-->', ex)
        print('Current bet: ', player.current_bet, '\n', 'Current cash: ', player.cash)


def define_gamers(gamers):
    for i, gamer in enumerate(gamers):
        game_error = True
        while game_error:
            try:
                if gamer['name'] is None:
                    print('\n------Player{}------'.format(i + 1))
                    gamer['name'] = input("Enter Players{}'s name:".format(i + 1))
                if gamer['initial_cash'] is None:
                    gamer['initial_cash'] = int(input("Enter Players{}'s initial cash:".format(i + 1)))
                    if gamer['initial_cash'] < 1000:
                        raise game.MinimumCashError('Initial credit must be equal or greater than €1,000')
                if gamer['allow_debt'] is None:
                    gamer['allow_debt'] = input("Do you want to allow indebtness?(y/n) ").lower()
                    gamer['allow_debt'] = True if gamer['allow_debt']=='y' else False
                game_error = False
            except ValueError:
                print('ERROR-->', 'Input must be an integer')
                gamer['initial_cash'] = None
            except game.MinimumCashError as ex:
                print(ex)
                gamer['initial_cash'] = None
    return gamers


def execute_game(match):
    match.start()
    while match.game_on:
        place_bets(match.alive_players)
        match.start_round()
        for player in match.alive_players:
            print('--------{0}---------\n'.format(player.name), player.current_hand)
            print('--------Croupier---------\n', match.croupier_hand)
        hand_players = match.retrieve_hands_alive()
        while len(hand_players)!=0:
            for player in hand_players:
                action = input('\n{0}, Choose an action (hit/stand): '.format(player.name))
                match.send_action(player, action)
                if action=='hit':
                    print('--------{0}---------\n'.format(player.name), player.current_hand, '\n', 'Current bet: ', player.current_bet,
                          '\n', 'Current cash: ', player.cash,'\n')
                    #print('--------Croupier---------\n', match.croupier_hand,'\n')
            hand_players = match.retrieve_hands_alive()
        if not all(map(lambda p:p.current_hand.is_busted, match.alive_players)):
            croupier_hand = match.get_croupier_hand()
            print('--------Croupier---------\n', croupier_hand, '\n')
        for player in match.alive_players:
            print(match.resolve_round(player).upper(), '\n')
        for player in match.alive_players:
            print("{0}'s balance after the last round is:\n\t- Total cash: {1:,}\n\t- Total gains: {2:,}\n".format(
                player.name, player.cash, player.gains), '\n')
        for player in match.alive_players:
            print('\n')
            answer = input('{0}, do you want to play on? (y/n) '.format(player.name))
            if answer=='n':
                player.kill()
        message = match.assess_continuity()
        if message is not None:
            print(message)


if __name__ == '__main__':

    print('Welcome to Blackjack!')

    bj = setup_game()

    print('\nFine!\n\t- Number of players is {0}\n\t- Number of decks is {1}'.format(bj.numplayers, bj.numdecks))

    empty_players = players_features_list(bj.numplayers)

    filled_players = define_gamers(empty_players)

    bj.setup_players(filled_players)

    stop = False

    while not stop:

        execute_game(bj)

        answer = input('Do you want to play again? (y/n) ')

        if answer == 'n':

            stop = True
