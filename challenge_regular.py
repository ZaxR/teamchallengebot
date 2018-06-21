from collections import defaultdict

import pandas as pd
from prompt_toolkit import prompt, AbortAction
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter


class Challenge(object):

    def __init__(self, name):
        self.name = name
        self.participants = pd.DataFrame(columns=['Lines of Code'])

    def add_participant(self, no_cmd_msg: str):
        # todo improve parse no_cmd_msg
        name = no_cmd_msg.split(',')[0].strip()
        lines_of_code = int(no_cmd_msg.split(',')[1].strip())

        new_df = pd.DataFrame([[name, lines_of_code]], columns=["Name", "Lines of Code"])
        new_df = new_df.set_index('Name')

        self.participants = pd.concat([self.participants[~self.participants.index.isin(new_df.index)], new_df])

        print(f"{name} added.")

    def bulk_add_participants(self, no_cmd_msg: str):
        # todo improve parse no_cmd_msg
        path = no_cmd_msg.strip()
        new_df = pd.read_csv(path, index_col=0)

        self.participants = pd.concat([self.participants[~self.participants.index.isin(new_df.index)], new_df])

        print(f"Participants from {path} added.")

    def clear_participants(self, no_cmd_msg: str):
        clear_y_n = prompt("Are you sure you want to remove all participants? ")
        if str(clear_y_n).lower() in ["y", "yes"]:
            self.participants = pd.DataFrame(index=['Name'], columns=['Lines of Code'])
            print("Aaaall gone.")
        elif str(clear_y_n).lower() in ["n", "no"]:
            print("Ok - we didn't touch anything.")
        else:
            print(f" '{clear_y_n}'' is not a valid command.")

    def create_groups(self, no_cmd_msg: str):
        """Creates groups with one participant per quintile by lines of code written.

        Args:
                group_size: The number of participants per group; also number of bins.
                channel: The Slack channel to output to.
                df: Participants and their lines of code written.

        Example:
                `@<botname> group 4` will create groups of 4.

        """
        df = self.participants.copy()
        df['Lines of Code'] = df['Lines of Code'].astype('int32')
        # todo handle group_size of 0 and empty df

        try:
            group_size = 4 if not no_cmd_msg else int(no_cmd_msg)
        except ValueError:
            raise ValueError(f"group_size expects an integer. You input the string {no_cmd_msg}.")

        if group_size > df.shape[0]:
            raise ValueError(f"group_size ({group_size}) is greater than the number of participants ({df.shape[0]}).")

        # Quantiles are derived from ranked lines_of_code to break ties.
        # Specifically, method='first' is used to break the ties
        df['rank'] = df['Lines of Code'].rank(method='first', ascending=False)
        df['quantile'] = pd.qcut(df['rank'], group_size, labels=False)

        # Shuffle the dataframe
        df = df.sample(frac=1)
        df.index.name = 'Name'
        print(df)
        # Create groups
        groups = defaultdict(list)
        for name, group in df.groupby('quantile'):
            print(name, group)
            c = 0
            for i, r in group.iterrows():
                c += 1
                groups[f"Group {c}"].append(r.name)
        # Identify small groups
        small_groups = []
        for group_name, group_members in groups.items():
            if len(group_members) < group_size - 1:
                small_groups.append(group_name)

        # Redistribute members of small groups to the larger groups
        to_redistribute = []
        for group_name in small_groups:
            to_redistribute.extend(groups.pop(group_name))

        while to_redistribute:
            for group_name, group_members in groups.items():
                if not to_redistribute:
                    break
                group_members.append(to_redistribute.pop())

        for k, v in groups.items():
            print(f"{k}: {', '.join(v)}")

    def list_participants(self, no_cmd_msg: str):
        # print(self.participants['Name'].tolist())
        print(self.participants)

    def remove_participants(self, no_cmd_msg: str):
        # todo parse no_cmd_msg
        participant_names = [i.strip() for i in no_cmd_msg.split(",")]
        self.participants = self.participants[~self.participants.index.isin(participant_names)]
        print(f"{participant_names} removed.")

    def parse_event(self, event_data):
        message = event_data.strip()

        valid_commands = {"add ": self.add_participant,
                          "bulk add ": self.bulk_add_participants,
                          "clear ": self.clear_participants,
                          "list": self.list_participants,
                          "remove ": self.remove_participants,
                          "group": self.create_groups}

        for command in valid_commands:
            if message.lower().startswith(command):
                valid_commands[command](message.lower()[len(command):])
                break
        else:
            return f"{message} is an invalid command. Please choose from: {', '.join([c for c in valid_commands])}."


def main():
    command_completer = WordCompleter(['add', 'bulk add', 'clear', 'list', 'remove', 'group'], ignore_case=True)
    history = InMemoryHistory()
    challenge = Challenge('Current')

    while True:
        try:
            event_data = prompt('> ',
                                completer=command_completer,
                                history=history,
                                on_abort=AbortAction.RETRY)
            challenge.parse_event(event_data)
        except EOFError:
            break  # Control-D pressed.

    print('GoodBye!')


if __name__ == '__main__':
    challenge = Challenge('Current')
    main()
