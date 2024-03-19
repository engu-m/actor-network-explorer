import math


def deathYear_parser(deathYear: float):
    if not deathYear or math.isnan(deathYear):
        return ""
    else:
        return int(deathYear)


def node_string(node_info: dict):
    pName = node_info["primaryName"]
    birthYear = int(node_info["birthYear"])
    deathYear = deathYear_parser(node_info["deathYear"])
    sex = "M" if node_info["primaryProfession"] == "actor" else "F"
    node_str = "\n".join([pName, f"({birthYear}-{deathYear})"])
    return node_str


def parseRuntime(runtimeMinutes: int):
    if math.isnan(runtimeMinutes):
        return ""
    else:
        hours, minutes = divmod(runtimeMinutes, 60)
        if hours > 0:
            return f"{hours}h {minutes}min"
        else:
            return f"{minutes}min"


def movie_string(movie_info: dict):
    pTitle = movie_info["primaryTitle"]
    oTitle = movie_info["originalTitle"]
    releaseYear = movie_info["releaseYear"]
    runtime = parseRuntime(movie_info["runtimeMinutes"])
    genres = movie_info["genres"]

    movie_str = f"{oTitle} / {pTitle} ({releaseYear}, {runtime})"
    return movie_str


def edge_string(common_movies: list):
    s = "s" if len(common_movies) > 1 else ""
    edge_str = f"{len(common_movies)} common movie{s}:\n"  # add unordered list html element instead
    edge_str += "\n".join([movie_string(movie_info) for movie_info in common_movies])
    return edge_str
