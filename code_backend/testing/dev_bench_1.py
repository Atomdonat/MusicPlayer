"""
File to develop and debug methods, class and more
"""

import json
import random
import sys


def all_shuffle(collection_tracks: list) -> list:
    """
    Shuffles the given list using the PRNG random.randint(). Every item will occur exactly once.
    :param collection_tracks: list to be shuffled
    :return: shuffled list
    """
    shuffled_collection = []
    shuffle_track_ids = collection_tracks
    while len(shuffle_track_ids) > 0:
        random_position = random.randint(0, len(shuffle_track_ids) - 1)
        current_track_id = shuffle_track_ids[random_position]
        shuffled_collection.append(current_track_id)
        shuffle_track_ids.pop(random_position)
    return shuffled_collection


def get_collisions(list_a:list[str], list_b:list[str]) -> list:
    print(len(list_a), len(list_b))
    if len(list_a) != len(list_b):
        print("List length does not match")
        sys.exit(1)

    matches = []
    for a_item,b_item in zip(list_a,list_b):
        if a_item == b_item:
            matches.append(a_item)

    return matches

if __name__ == "__main__":
    with open("debugging.json", "r") as file:
        data = json.load(file)

    origin_list = [i["uri"] for i in data]
    shuffled_list = all_shuffle(origin_list)
    collisions = get_collisions(origin_list, shuffled_list)

    with open("debugging_2.json", "w") as file:
        json.dump({"collisions": collisions}, file)
