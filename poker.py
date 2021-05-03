"""
Poker

Author: Joe Taylor, Scott Vaughan

A script to read in a series of cards, group into two hands of five, and output which hand
would win if scored by standard poker rules.

Written to solve https://projecteuler.net/problem=54
"""

from collections import Counter
from contextlib import ExitStack
from enum import IntEnum
from itertools import islice
import sys


class HandType(IntEnum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIRS = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9


def read_cards(source_file):
    """
    Read a series of cards from a source file and output as generator of (value, suit) pairs

    Converts value of King etc to numeric equivalent. Suit is single character.
    """
    pictures = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10}
    for line in source_file:
        for card in line.split(" "):
            try:
                value = int(card[0])
            except ValueError:
                value = pictures[card[0].upper()]
            yield (value, card[1])


def chunk(iterable, chunk_size):
    iterator = iter(iterable)
    while chunk := list(islice(iterator, chunk_size)):
        yield chunk


def read_hand(cards):
    """
    Generator which groups cards into sorted hands of five
    """
    yield from (sorted(hand, reverse=True) for hand in chunk(cards, 5))


class HandRater:
    match_fns = []

    @classmethod
    def register_match_fn(cls, value):
        def _wrapped(fn):
            cls.match_fns.append((value, fn))
            cls.match_fns.sort(key=lambda x: x[0], reverse=True)
            return fn

        return _wrapped

    @classmethod
    def rate_hand(cls, hand):
        for rank, fn in cls.match_fns:
            value = fn(hand)
            if value:
                return rank, value


def is_flush(hand):
    return len(set(card[1] for card in hand)) == 1


def get_groups(hand):
    counter = Counter(card[0] for card in hand)
    groupings, cards = zip(
        *sorted(((count, card) for card, count in counter.items()), reverse=True)
    )
    return groupings, cards


@HandRater.register_match_fn(HandType.HIGH_CARD)
def check_highest_card(hand):
    return tuple(card[0] for card in hand)


@HandRater.register_match_fn(HandType.PAIR)
def check_pair(hand):
    groupings, cards = get_groups(hand)
    if groupings[:2] == (2, 1):
        return cards


@HandRater.register_match_fn(HandType.TWO_PAIRS)
def check_two_pairs(hand):
    groupings, cards = get_groups(hand)
    if groupings[:2] == (2, 2):
        return cards


@HandRater.register_match_fn(HandType.THREE_OF_A_KIND)
def check_three_oak(hand):
    groupings, cards = get_groups(hand)
    if groupings[:2] == (3, 1):
        return cards


@HandRater.register_match_fn(HandType.STRAIGHT)
def check_straight(hand):
    if all((a[0] - b[0]) == 1 for (a, b) in zip(hand[:-1], hand[1:])):
        return hand[0][0]


@HandRater.register_match_fn(HandType.FLUSH)
def check_flush(hand):
    if is_flush(hand):
        return check_highest_card(hand)


@HandRater.register_match_fn(HandType.FULL_HOUSE)
def check_full_house(hand):
    groupings, cards = get_groups(hand)
    if groupings[:2] == (3, 2):
        return cards


@HandRater.register_match_fn(HandType.FOUR_OF_A_KIND)
def check_four_oak(hand):
    groupings, cards = get_groups(hand)
    if groupings[:2] == (4, 1):
        return cards


@HandRater.register_match_fn(HandType.STRAIGHT_FLUSH)
def check_straight_flush(hand):
    if is_flush(hand):
        return check_straight(hand)


if __name__ == "__main__":
    try:
        target = sys.argv[1]
    except IndexError:
        target = "-"
    with ExitStack() as stack:
        if target == "-":
            fh = sys.stdin
        else:
            fh = stack.enter_context(open(target))
        games_won = {
            "Player 1": 0,
            "Player 2": 0,
        }
        for player_1, player_2 in chunk(
            (HandRater.rate_hand(hand) for hand in read_hand(read_cards(fh))), 2
        ):
            winner = "Player 1" if player_1 > player_2 else "Player 2"
            print(f"Winner is {winner}: {player_1!r} vs {player_2!r}")
            games_won[winner] += 1
        print(
            "Player 1 won {Player 1} games, Player 2 won {Player 2} games".format(
                **games_won
            )
        )
