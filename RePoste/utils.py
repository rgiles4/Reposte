# import os

# # import sys
# # from collections import namedtuple
# # import datetime
# # import logging


# def ensure_directory_exists(directory):
#     if not os.path.exists(directory):
#         os.makedirs(directory)


# def setup_logging(level=logging.DEBUG):
#     """
#     Sets up basic logging configuration for the entire application.
#     """
#     # You can modify the logging format as you like.
#     logging.basicConfig(
#         level=level,
#         format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
#         stream=sys.stdout,
#     )
#     logging.info("Logging has been configured.")


# FencingMatch = namedtuple(
#     "FencingMatch", ["fencer1", "fencer2", "location", "start_time"]
# )


# class MatchDataManager:
#     """
#     Manages the storage and retrieval of data about the fencing match.
#     """

#     def __init__(self):
#         self.current_match = None

#     def create_new_match(self, fencer1, fencer2, location):
#         start_time = datetime.datetime.now()
#         self.current_match = FencingMatch(
#             fencer1=fencer1,
#             fencer2=fencer2,
#             location=location,
#             start_time=start_time,
#         )
#         logging.info(f"New match created: {self.current_match}")

#     def get_match_info(self):
#         return self.current_match
