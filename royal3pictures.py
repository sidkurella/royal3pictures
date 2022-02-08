#! /usr/bin/env python3
"""
Simulator for the casino game "Royal 3 Pictures".

As found in The Venetian Hotel and Casino, Las Vegas, NV.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple

import argparse
import itertools
import random


class Suit(Enum):
    """
    A suit for a playing card.
    """
    SPADES = 's'
    DIAMONDS = 'd'
    HEARTS = 'h'
    CLUBS = 'c'


class Rank(Enum):
    """
    A rank for a playing card.
    """
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'


    def is_face(self) -> bool:
        """
        Returns if this card is a face card.
        """
        return self in (Rank.JACK, Rank.QUEEN, Rank.KING)


    def points(self) -> int:
        """
        Calculates the number of points this card is worth in the game.
        """
        if self.is_face():
            return 0

        return self.value


class OutcomeType(Enum):
    """
    Enumerates the outcome types in the game.
    """
    EVEN_MONEY = 1
    HALF_MONEY = 2
    LOSS = 3
    PUSH = 4


@dataclass
class Card:
    """
    A representation of a playing card.
    """
    rank: Rank
    suit: Suit


    def __str__(self) -> str:
        return f"{self.rank.value}{self.suit.value}"


    def __repr__(self) -> str:
        return str(self)


SUITS = list(Suit)
RANKS = list(Rank)
DECK = [Card(rank=x[0], suit=x[1]) for x in itertools.product(RANKS, SUITS)]


def calculate_payout(
    wager: float,
    player_hand: List[Card],
    dealer_hand: List[Card],
) -> Tuple[float, OutcomeType]:
    """
    Calculate the payout given the player and dealer hands.

    Calculates the payout, including returning the original wager on a winning bet.
    """
    player_pictures = len(list(filter(lambda x: x.rank.is_face(), player_hand)))
    dealer_pictures = len(list(filter(lambda x: x.rank.is_face(), dealer_hand)))
    player_points = sum(x.rank.points() for x in player_hand) % 10
    dealer_points = sum(x.rank.points() for x in dealer_hand) % 10

    if player_pictures > dealer_pictures:
        return wager * 2, OutcomeType.EVEN_MONEY
    if dealer_pictures > player_pictures:
        return 0, OutcomeType.LOSS

    if player_points > dealer_points:
        if player_points != 6:
            return wager * 2, OutcomeType.EVEN_MONEY

        return wager * 1.5, OutcomeType.HALF_MONEY
    if dealer_points > player_points:
        return 0, OutcomeType.LOSS

    return wager, OutcomeType.PUSH # Push


def run_iteration(wager: float) -> Tuple[float, OutcomeType]:
    """
    Runs one iteration of the game.
    """
    random.shuffle(DECK)
    player_hand = DECK[0:3]
    dealer_hand = DECK[3:6]
    return calculate_payout(wager, player_hand, dealer_hand)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simulate the Royal 3 Pictures game")
    parser.add_argument('--runs',
        '-n',
        metavar='n',
        type=int,
        default=1_000_000,
        help="Number of runs to simulate",
    )
    parser.add_argument('--bankroll', type=int, default=None, help="Initial bankroll size")
    parser.add_argument('--wager', type=int, default=1, help="Wager size")

    args = parser.parse_args()

    if args.bankroll is None:
        args.bankroll = args.runs

    print(f"Runs: {args.runs}\tBankroll: {args.bankroll}\tWager: {args.wager}")
    print("Running simulation...")

    initial_bankroll = args.bankroll
    current_bankroll = args.bankroll

    outcome_times: Dict[OutcomeType, int] = {}

    for i in range(0, args.runs):
        print(f"Run: {i + 1}")
        current_bankroll -= args.wager
        payout, outcome = run_iteration(args.wager)
        current_bankroll += payout

        try:
            outcome_times[outcome] += 1
        except KeyError:
            outcome_times[outcome] = 1

    edge = (initial_bankroll - current_bankroll) / initial_bankroll
    print(f"Initial bankroll: {initial_bankroll}\tFinal bankroll: {current_bankroll}")
    print(f"House edge: {edge:.5%}")
    print("")

    even_money_wins = outcome_times[OutcomeType.EVEN_MONEY]
    half_money_wins = outcome_times[OutcomeType.HALF_MONEY]
    losses = outcome_times[OutcomeType.LOSS]
    pushes = outcome_times[OutcomeType.PUSH]
    total = args.runs
    print(f"Even money wins: {even_money_wins}\tRate: {even_money_wins/total:.5%}")
    print(f"Half money wins: {half_money_wins}\tRate: {half_money_wins/total:.5%}")
    print(f"Losses: {losses}\tRate: {losses/total:.5%}")
    print(f"Pushes: {pushes}\tRate: {pushes/total:.5%}")
