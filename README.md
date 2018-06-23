# teamchallengebot

Two scripts are included in this project:
1. challenge_grouper.py is an offline command line tool to group participants in a coding challenge based on an even mix of experience levels.
2. teamchallengebot.py is a slack bot version of challenge_grouper (currently in progress).

List of commands:
- 'add': Adds participants one at a time in a <name>, <int> format.
- 'bulk add': Loads participants and their experience levels from a csv file at the given path.
- 'clear': Clears all participants.
- 'group': Creates groups of a given size (default 4), evenly distributing experience levels (any int) across groups.
- 'list': Displays a list of participants.
- 'remove': Removes one or more participants, separating with commas.
- 'save': Saves the list of participants and their experience scores to a csv at the given path.


This project was inspired by the needs of Chicago Python User Group (ChiPy)'s Project Nights, but given that it takes any list of names and associated numeric scores, and that the group size is customizable, it can be used for a variety of use cases.

Feel free to use this project in whole or part in any non-commercial, non-damaging endeavours.
