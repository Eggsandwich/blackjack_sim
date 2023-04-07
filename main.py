import random
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Define the configurable variables
num_decks = 1
surrender_option = "early"  # "early", "late", or "none"
surrender_return = 0.5
blackjack_payout = 1.25
double_option = "any"
split_option = "any"
shuffle_option = "every_hand"
num_simulations = 100000
num_hands_per_session = 100
initial_balance = 1000
bet_amount = 50

def get_deck(num_decks):
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    deck = [{'rank': rank, 'suit': suit} for rank in ranks for suit in suits] * num_decks
    return deck

def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

def deal_cards(deck):
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    return player_hand, dealer_hand

def card_value(card):
    if card['rank'] in ['2', '3', '4', '5', '6', '7', '8', '9', '10']:
        return int(card['rank'])
    elif card['rank'] in ['J', 'Q', 'K']:
        return 10
    elif card['rank'] == 'A':
        return 11

def calculate_hand_value(hand):
    value = sum(card_value(card) for card in hand)
    num_aces = len([card for card in hand if card['rank'] == 'A'])
    while value > 21 and num_aces > 0:
        value -= 10
        num_aces -= 1
    return value

def play_dealer_hand(dealer_hand, deck):
    while calculate_hand_value(dealer_hand) < 17 or (calculate_hand_value(dealer_hand) == 17 and any(card['rank'] == 'A' for card in dealer_hand)):
        dealer_hand.append(deck.pop())
    return dealer_hand

def basic_strategy(player_hand, dealer_up_card):
    dealer_up_card_value = card_value(dealer_up_card)
    player_total = calculate_hand_value(player_hand)

    if len(player_hand) == 2 and player_total == 11:
        return 'double' if double_option == 'any' else 'hit'
    if len(player_hand) == 2 and player_total == 10 and dealer_up_card_value <= 9:
        return 'double' if double_option == 'any' else 'hit'
    if len(player_hand) == 2 and player_total == 9 and dealer_up_card_value in [3, 4, 5, 6]:
        return 'double' if double_option == 'any' else 'hit'

    if player_total < 12:
        return 'hit'
    if player_total == 12:
        return 'hit' if dealer_up_card_value in [2, 3, 7, 8, 9, 10, 11] else 'stand'
    if player_total >= 13 and player_total <= 16:
        return 'hit' if dealer_up_card_value in [7, 8, 9, 10, 11] else 'stand'
    if player_total >= 17:
        return 'stand'
    
    else:
        if player_total == 11:
            return 'double'
        if player_total == 10 and dealer_up_card not in ['10', 'A']:
            return 'double'
        if player_total == 9 and dealer_up_card in ['3', '4', '5', '6']:
            return 'double'
        if player_total <= 11:
            return 'hit'
        if player_total == 12:
            return 'hit' if dealer_up_card in ['2', '3', '7', '8', '9', '10', 'A'] else 'stand'
        if player_total >= 13 and player_total <= 16:
            return 'hit' if dealer_up_card in ['7', '8', '9', '10', 'A'] else 'stand'
        if player_total >= 17:
            return 'stand'


def simulate_blackjack(num_simulations, num_hands_per_session):
    results = []
    for i in range(num_simulations):
        deck = get_deck(num_decks)
        shuffle_deck(deck)
        balance = initial_balance
        wins, losses = 0, 0
        for j in range(num_hands_per_session):
            if shuffle_option == "every_hand":
                deck = shuffle_deck(get_deck(num_decks))
            if len(deck) < 20:
                deck = shuffle_deck(get_deck(num_decks))

            player_hand, dealer_hand = deal_cards(deck)
            dealer_up_card = dealer_hand[1]

            # Added line: Initialize current_bet variable
            current_bet = bet_amount

            while True:
                action = basic_strategy(player_hand, dealer_up_card)
                if action == "hit":
                    player_hand.append(deck.pop())
                elif action == "double":
                    player_hand.append(deck.pop())

                    # Modified line: Update current_bet instead of bet_amount
                    current_bet *= 2

                    break
                elif action == "stand":
                    break

            if calculate_hand_value(player_hand) > 21:
                losses += 1

                # Modified line: Use current_bet instead of bet_amount
                balance -= current_bet

            else:
                dealer_hand = play_dealer_hand(dealer_hand, deck)
                if calculate_hand_value(dealer_hand) > 21 or calculate_hand_value(player_hand) > calculate_hand_value(dealer_hand):
                    wins += 1
                    if len(player_hand) == 2 and calculate_hand_value(player_hand) == 21:

                        # Modified line: Use current_bet instead of bet_amount
                        balance += current_bet * blackjack_payout

                    else:

                        # Modified line: Use current_bet instead of bet_amount
                        balance += current_bet

                elif calculate_hand_value(player_hand) < calculate_hand_value(dealer_hand):
                    losses += 1

                    # Modified line: Use current_bet instead of bet_amount
                    balance -= current_bet

            if balance <= 0:
                break

        results.append((wins, losses, balance))

    return results

results = simulate_blackjack(num_simulations, num_hands_per_session)
final_balances = [balance for _, _, balance in results]

# Display the results
print("Simulation Results:")
print("--------------------")
print(f"Number of simulations: {num_simulations}")
print(f"Number of hands per session: {num_hands_per_session}")
print(f"Initial balance: ${initial_balance}")
print(f"Bet amount: ${bet_amount}")
print("\nResults:")
print("--------")
print(f"Average final balance: ${np.mean(final_balances):.2f}")
print(f"Median final balance: ${np.median(final_balances):.2f}")
print(f"Minimum final balance: ${np.min(final_balances)}")
print(f"Maximum final balance: ${np.max(final_balances)}")

# Plot the distribution of final balances
sns.histplot(final_balances, kde=True)
plt.xlabel('Final balance')
plt.ylabel('Frequency')
plt.title('Distribution of Final Balances')
plt.show()
