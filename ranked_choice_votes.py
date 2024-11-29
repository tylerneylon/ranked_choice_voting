#!/usr/bin/env python3
# coding: utf-8
''' ranked_choice_votes.py

    Usage:
        ./ranked_choice_votes.py <google_form_data.csv>

    This interactive script determines the winner of a ranked-choice
    vote based on data from a Google form. Please provide the name of google
    form's csv file to get started.
'''


# ______________________________________________________________________
# Imports

import csv
import random
import sys
from collections import Counter


# ______________________________________________________________________
# Globals

titles = None


# ______________________________________________________________________
# Functions

def get_acceptable_answer(prompt, is_acceptable):
    ''' Ask for an answer until we receive an acceptable answer. '''
    while True:
        inp = input(prompt)
        if is_acceptable(inp):
            return inp

def find_winner(votes, be_verbose=True, ignore=set()):
    ''' This function expects each row of `votes` to represent the ordered
        votes of a voter. This function expects there to be no duplicates
        within a row (which would be an invalid list of votes). Given that,
        this implements instant-runoff voting, verbosely explaining the
        steps. It is possible for the result to be a tie, in which case
        all final-tied votes are given. The result is both printed and
        returned as a list.
    '''

    # Make a deep copy of `votes` so we can edit it.
    votes = [[b for b in voter if b not in ignore] for voter in votes]

    def pr(*args):
        if be_verbose:
            print(*args)

    while True:

        removed = set()
        
        top_votes = Counter()
        for voter in votes:
            if len(voter) > 0:
                top_votes[voter[0]] += 1

        if len(top_votes) == 0:
            print('Error: Reached a point with no valid votes left.')
            return []

        n = sum(top_votes.values())
        pr('Top remaining votes:', top_votes)
        top = top_votes.most_common(1)[0]
        if top[1] > n / 2:
            pr('Winner:', top[0])
            return [top[0]]

        # Case: We have a plurality of count values, so we can eliminate some.
        vote_counts = set(top_votes.values())
        if len(vote_counts) > 1:
            max_count = max(vote_counts)
            for book, count in top_votes.items():
                if count < max_count:
                    pr(f'Removing book {book}')
                    removed.add(book)

        # Case: Complete tie, and no other votes remain.
        elif all(len(v) < 2 for v in votes):
            winners = list(top_votes.keys())
            pr('Tied winners:', winners)
            return winners

        # Case: Complete tie, and there are backup votes.
        #       Try to resolve this by giving partial credit based on backup votes.
        else:
            new_votes = Counter()
            for voter in votes:
                score = 1
                for b in voter:
                    new_votes[b] += score
                    score /= 2
            vote_counts = {new_votes[b] for b in top_votes}
            if len(vote_counts) > 1:
                max_count = max(vote_counts)
                for book in top_votes:
                    if new_votes[book] < max_count:
                        pr(f'Removing book {book} (tie-breaking with backup votes)')
                        removed.add(book)
            else:
                # In theory, perhaps I should eliminate all candidates here,
                # but it makes more sense to me to declare this a tie case.
                winners = list(new_votes.keys())
                pr('Tied winners:', winners)
                return winners

        # Remove all eliminated candidates.
        votes = [
            [b for b in voter if b not in removed]
            for voter in votes
        ]

def print_vote_table(votes):
    ''' Print out a human-friendly table of the votes in `votes`. '''
    top_row = list(range(1, len(titles) + 1))
    for i, row in enumerate([top_row] + votes):
        prefix = '    book' if i == 0 else f'voter {i:2d}'
        print(prefix + ' |', end='')
        for vote in row:
            vote_str = '   ' if vote == 0 else f'{vote:3d}'
            print(vote_str, end='')
        if i > 0 and not is_ok[i - 1]:
            print('  *', end='')
        print()
        if i == 0:
            print('_' * (4 * len(titles) + 9))
    
    if not all(is_ok):
        print(
                '\n* Indicates a naughty voter = someone has given ' +
                'multiple votes to the same choice!'
        )
        print('  (gasp)')

    print()  # This is a blank separator line after the table.

def book_iter(row, tie_breaker):
    ''' This returns a generator for the given row of votes, returning, in
        order, the items voted for from first preference to last. The given
        tie_breaker method (either 'r' or a voter index) is used to break ties
        in the case of repeats at any given choice level.
    '''
    r = list(row)

    while True:
        choices_left = sorted(list(set(r) - {0}))
        if len(choices_left) == 0:
            return
        choice_num = choices_left[0]
        books = [i for i, v in enumerate(r) if v == choice_num]
        b = random.choice(books)  # This is deterministic if len(books) == 1.
        if len(books) > 1 and tie_breaker != 'r':
            # We're aligning with another voter.
            align_with = sorted([
                (v, i)
                for i, v in enumerate(votes[tie_breaker - 1])
                if v > 0
            ])
            align_rank = [
                    align_pt[1]
                    for align_pt in align_with
                    if align_pt[1] in books
            ]
            if align_rank:
                b = align_rank[0]
            else:
                print('Warning: using a random choice to fix improper vote.')
        r[b] = 0
        yield b

# ______________________________________________________________________
# Main script

# __________
# Confirm that we have a csv filename.

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(0)

# __________
# Print out welcome message.

welcome_msg = '''
Welcome to the ranked-choice voting machine!

Prepare yourself.

This voting machine assumes that:
 * We're working with a CSV file from Google forms.
 * That the questions all begin with the title of the books.
   Specifically, I'll use the first line of each question as a title.
 * That the ranked choice votes are of the form "First choice"
   up through a maximum of "Fifth choice". Case doesn't matter.
 * The laws of physics remain relatively stable, at least for now.

This script is perfect! However, due to things like gamma rays
and such, it may have some bugs after all.
'''
print(welcome_msg)

# __________
# Check that the admin remembered to vote.

print('First things first.')
inp = get_acceptable_answer(
    'Did you remember to vote? [y]es / [n]o ',
    lambda inp: inp.lower() in 'yn'
)
if inp.lower() == 'n':
    print('Ruh-roh. Please go vote! Using the same Google form. Then run this on the new data!')
    sys.exit(0)
else:
    print('\nPhew, I was nervous about that. Good job.\n')

# __________
# Load in the data.

with open(sys.argv[1]) as f:
    rows = list(csv.reader(f))

# __________
# Figure out which columns are books and print out the titles.
# The first column is always the timestamp.

answers_per_column = list(zip(*rows[1:]))
rank_answers = [
    '', 'first choice', 'second choice', 'third choice',
    'fourth choice', 'fifth choice'
]
is_col_ranked = [
    all(answer.lower() in rank_answers for answer in answers)
    for answers in answers_per_column
]
titles = [
    rows[0][i].split('\n')[0]
    for i in range(len(answers_per_column))
    if is_col_ranked[i]
]
print('I believe the book titles are:\n')
for i, title in enumerate(titles):
    print(f'{i + 1:5d}. {title}')

# __________
# Parse and print out the votes.

votes = [
    [rank_answers.index(vote.lower()) for i, vote in enumerate(row) if is_col_ranked[i]]
    for row in rows[1:]
]
# Identify naughty voters; these are votes who haven't voted properly.
is_ok = []
for row in votes:
    c = Counter(row)
    del c[0]
    reverse_counter = {v:k for k, v in c.items()}
    if 1 in reverse_counter:
        del reverse_counter[1]
    is_ok.append(len(reverse_counter) == 0)
print('\nHere are the raw votes. Each row is a single voter.\n')
print_vote_table(votes)

# __________
# As needed, adjust naughty votes.

prompt = 'How shall I fix naughty votes? [r]andomize within conflicts / '
prompt += f'[1-{len(votes)}] resolve conflicts by aligning with another voter '

def is_good(inp):
    if inp.lower() == 'r':
        return True
    if not inp.isdigit() or not (int(inp) in range(1, len(votes) + 1)):
        return False
    if not is_ok[int(inp) - 1]:
        print('To align with a voter, please choose a non-naughty voter.')
        return False
    return True

tie_breaker = 'r'  # This is a reasonable default if all is ok.
if not all(is_ok):
    tie_breaker = get_acceptable_answer(
        prompt,
        is_good
    )
    if tie_breaker != 'r':
        tie_breaker = int(tie_breaker)

# __________
# We'll have book_votes[voter_idx] = [list of books, first choice first].

book_votes = [list(book_iter(row, tie_breaker)) for row in votes]

# __________
# If needed, print out the adjusted votes.

if not all(is_ok):
    is_ok = [True] * len(titles)
    print('Adjusted votes:\n')
    print_vote_table([
        [books.index(i) + 1 if i in books else 0 for i in range(len(titles))]
        for books in book_votes
    ])

# __________
# Print out the main winner, and rank the rest as well.

print('Finding the first-place winner:')
winners = find_winner(book_votes, be_verbose=True)
print('\nFirst place winner(s):')
for w in winners:
    print(titles[w])

print('\nFull ranking of all candidates:')
books_left = set(sum(book_votes, start=[]))
ignore = set()
rank = 1

while len(books_left) > 0:

    # I'm leaving this here in case any loops need debugging.
    if False:
        print('\n' + '_' * 70)
        print('ignore', ignore)
        print('books_left', books_left)

    winners = find_winner(book_votes, be_verbose=False, ignore=ignore)
    tie_str = '(tie)' if len(winners) > 1 else '     '
    for w in winners:
        print(f'{rank:2d}. {tie_str} {titles[w]}')
        ignore.add(w)
        books_left.remove(w)
    rank += len(winners)

print('\nThanks for using the ranked-choice voting machine!\n')
