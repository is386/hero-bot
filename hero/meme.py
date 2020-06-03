from random import choice, seed

meme_path: str = "databases/memes"


def get_random_meme():
    with open(meme_path, "r") as f:
        seed()
        return choice(f.readlines())


def add_meme(meme: str):
    with open(meme_path, "a") as f:
        f.write("\n" + meme)
